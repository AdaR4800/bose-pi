
#!/usr/bin/env python3
"""
Bose Control – zentraler Scheduler.

Steuert die Bose PS28 ereignisgesteuert anhand der AirPlay-Ereignisse.
Verwendet GPIO16 zur Zustandsbeobachtung und eine zentrale UART-Schnittstelle.

Funktionen:
- Bose-Verfügbarkeit beim Start prüfen
- GPIO16 mit einem Stabilitätsfenster von 200 ms auswerten
- Bei AirPlay-START ANTI_MUTE und FIVE_CHANNEL senden
- Bei AirPlay-STOP nach 5 Sekunden MUTE senden
- Nach insgesamt 10 Sekunden POWER_OFF senden
- Bei erneutem START ausstehende STOP-Timer abbrechen
- Kein periodisches Bus-Polling

Die serielle Übertragung bestätigt nicht automatisch, dass die Bose
den jeweiligen Befehl tatsächlich ausgeführt hat.
"""

import logging
import signal
import time
from pathlib import Path

import gpiod
from gpiod.line import Direction

from bose_bus import BoseBus


# -------------------------------------------------------------------
# Konfiguration
# -------------------------------------------------------------------

GPIO_CHIP = "/dev/gpiochip0"
GPIO_LINE = 16

GPIO_STABLE_TIME = 0.200

# Zeitangaben ab einem AirPlay-STOP
MUTE_DELAY = 5.0
POWER_OFF_DELAY = 10.0

# Scheduler-Intervall, kein periodisches Bus-Polling
SCHEDULER_TICK = 0.010

BASE_DIR = Path("/home/robert/bose-control")
LOG_FILE = BASE_DIR / "logs" / "bose-control.log"
EVENT_QUEUE = BASE_DIR / "events" / "queue"


# -------------------------------------------------------------------
# Zustände
# -------------------------------------------------------------------

class State:
    BOSE_UNAVAILABLE = "BOSE_UNAVAILABLE"
    AVAILABLE_IDLE = "AVAILABLE_IDLE"
    AIRPLAY_ACTIVE = "AIRPLAY_ACTIVE"
    STOP_PENDING = "STOP_PENDING"
    MUTED_IDLE = "MUTED_IDLE"
    BOSE_OFF = "BOSE_OFF"
    BUS_ERROR = "BUS_ERROR"


# -------------------------------------------------------------------
# Controller
# -------------------------------------------------------------------

class BoseController:
    def __init__(self):
        self.state = State.BOSE_UNAVAILABLE

        self.gpio_level = None
        self.gpio_candidate = None
        self.gpio_candidate_since = None

        self.gpio_request = gpiod.request_lines(
            GPIO_CHIP,
            consumer="bose-control",
            config={
                GPIO_LINE: gpiod.LineSettings(
                    direction=Direction.INPUT
                )
            },
        )

        self.bose_available = None

        self.airplay_selected = False
        self.event_queue = EVENT_QUEUE

        self.mute_requested = False
        self.power_off_requested = False
        self.last_stop_time = None

        self.bus = BoseBus()
        self.bus_transaction_active = False
        self.pending_commands = []

        self.running = True

        logging.info("Bose Control gestartet")
        self.check_bus_availability()
        logging.info(
            "GPIO%d: Eingang aktiv, Stabilitätsfenster %.0f ms",
            GPIO_LINE,
            GPIO_STABLE_TIME * 1000,
        )
        logging.info("Buszugriffe: ereignisgesteuert")
        logging.info("AirPlay-Dienststeuerung: deaktiviert")
        logging.info("Periodisches Bus-Polling: deaktiviert")

    def check_bus_availability(self):
        """Prüft die Bose über die zentrale UART-Verbindung."""
        try:
            self.bus.open()
            available = self.bus.check_availability()
            self.bose_available = available
            return available
        except Exception:
            self.bose_available = False
            logging.exception("Fehler bei der Bose-Busprüfung")
            return False

    def _update_state_from_inputs(self):
        """Leitet den Zustand aus GPIO16 und der Busprüfung ab."""
        if self.gpio_level == 0:
            new_state = State.BOSE_UNAVAILABLE
        elif self.gpio_level == 1 and self.bose_available is True:
            new_state = State.AVAILABLE_IDLE
        else:
            return

        if self.state != new_state:
            self.state = new_state
            logging.info("Zustand: %s", self.state)

    def process_airplay_events(self):
        """Verarbeitet wartende START-/STOP-Ereignisse in Reihenfolge."""
        try:
            events = sorted(self.event_queue.iterdir())
        except OSError:
            logging.exception(
                "AirPlay-Ereigniswarteschlange nicht lesbar"
            )
            return

        for event_file in events:
            if not event_file.is_file():
                continue

            name = event_file.name

            if name.endswith("-START"):
                self.airplay_selected = True
                self.last_stop_time = None
                self.mute_requested = False
                self.power_off_requested = False
                self.state = State.AIRPLAY_ACTIVE

                # Eine zusammenhängende Befehlsfolge vormerken.
                self.pending_commands.clear()
                self.pending_commands.append([
                    ("ANTI_MUTE", bytes.fromhex("01 00 01 00")),
                    ("FIVE_CHANNEL", bytes.fromhex("05 00 05 00")),
                ])

                logging.info(
                    "AirPlay-Ereignis: START; "
                    "STOP-Timer abgebrochen; Zustand: %s",
                    self.state,
                )
                logging.info(
                    "Befehlsfolge vorgemerkt: ANTI_MUTE -> FIVE_CHANNEL"
                )

            elif name.endswith("-STOP"):
                self.airplay_selected = False
                self.last_stop_time = time.monotonic()
                self.mute_requested = False
                self.power_off_requested = False
                self.state = State.STOP_PENDING
                self.pending_commands.clear()

                logging.info(
                    "AirPlay-Ereignis: STOP; Zustand: %s",
                    self.state,
                )

            else:
                logging.warning(
                    "Unbekanntes AirPlay-Ereignis: %s",
                    name,
                )

            try:
                event_file.unlink()
            except OSError:
                logging.exception(
                    "Ereignisdatei konnte nicht entfernt werden: %s",
                    name,
                )

    def process_stop_timers(self, now):
        """Sendet MUTE nach 5 s und POWER_OFF nach insgesamt 10 s."""
        if self.airplay_selected or self.last_stop_time is None:
            return

        elapsed = now - self.last_stop_time

        def send_stop_command(name, frame):
            if self.bose_available is not True:
                logging.warning(
                    "Bose-Bus: %s ausgelassen; "
                    "Verfügbarkeit nicht bestätigt",
                    name,
                )
                return False

            try:
                self.bus.open()
                results = self.bus.send_sequence([
                    (name, bytes.fromhex(frame))
                ])

                if results and all(success for _, success in results):
                    logging.info("Bose-Bus: %s übertragen", name)
                    return True

                self.state = State.BUS_ERROR
                logging.error(
                    "Bose-Bus: %s Übertragung fehlgeschlagen",
                    name,
                )

            except Exception:
                self.state = State.BUS_ERROR
                logging.exception(
                    "Bose-Bus: Fehler bei %s",
                    name,
                )

            return False

        if elapsed >= MUTE_DELAY and not self.mute_requested:
            self.mute_requested = True
            logging.info(
                "Timer: MUTE fällig nach %.1f s",
                elapsed,
            )
            send_stop_command("MUTE", "02 00 78 7A")

        if elapsed >= POWER_OFF_DELAY and not self.power_off_requested:
            self.power_off_requested = True
            logging.info(
                "Timer: POWER_OFF fällig nach %.1f s",
                elapsed,
            )
            if send_stop_command("POWER_OFF", "01 00 80 81"):
                self.state = State.BOSE_OFF

    def observe(self):
        """Ein Scheduler-Durchlauf."""
        now = time.monotonic()

        # GPIO16: Eingang mit 200-ms-Stabilitätsfenster
        raw_level = self.gpio_request.get_value(GPIO_LINE)

        if raw_level != self.gpio_candidate:
            self.gpio_candidate = raw_level
            self.gpio_candidate_since = now

        elif (
            self.gpio_level != raw_level
            and self.gpio_candidate_since is not None
            and now - self.gpio_candidate_since >= GPIO_STABLE_TIME
        ):
            self.gpio_level = raw_level
            logging.info(
                "GPIO%d stabil: %s",
                GPIO_LINE,
                "HIGH" if raw_level else "LOW",
            )
            self._update_state_from_inputs()

        # AirPlay-Ereignisse und verzögerte STOP-Aktionen
        self.process_airplay_events()
        self.process_stop_timers(now)

        # Bus-Scheduler: nur bei aktivem AirPlay und bestätigter
        # Verfügbarkeit Befehlsfolgen übertragen.
        if (
            self.pending_commands
            and self.airplay_selected
            and self.bose_available is True
            and not self.bus_transaction_active
        ):
            sequence = self.pending_commands.pop(0)
            self.bus_transaction_active = True

            try:
                self.bus.open()
                results = self.bus.send_sequence(sequence)

                if results and all(success for _, success in results):
                    logging.info(
                        "Bose-Bus: Befehlsfolge übertragen"
                    )
                else:
                    self.state = State.BUS_ERROR
                    logging.error(
                        "Bose-Bus: Befehlsfolge unvollständig"
                    )

            except Exception:
                self.state = State.BUS_ERROR
                logging.exception(
                    "Bose-Bus: Übertragung fehlgeschlagen"
                )

            finally:
                self.bus_transaction_active = False

        # Kein periodisches Bus-Polling.
        return now

    def run(self):
        logging.info(
            "Scheduler läuft; ereignisgesteuerte Busbefehle aktiv"
        )

        while self.running:
            self.observe()
            time.sleep(SCHEDULER_TICK)

        logging.info("Bose Control beendet")

    def shutdown(self, *_):
        logging.info("Beenden angefordert")
        self.running = False

        if hasattr(self, "gpio_request"):
            self.gpio_request.release()

        if hasattr(self, "bus"):
            self.bus.close()


# -------------------------------------------------------------------
# Programmeinstieg
# -------------------------------------------------------------------

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_FILE),
        ],
    )

    controller = BoseController()

    signal.signal(signal.SIGINT, controller.shutdown)
    signal.signal(signal.SIGTERM, controller.shutdown)

    controller.run()


if __name__ == "__main__":
    main()

