# Bose Pi -- Current Software Status

**Documentation status:** Intermediate milestone\
**Last verified:** 13 October 2026\
**Platform:** Raspberry Pi 5, Debian GNU/Linux 13 (Trixie)\
**Project:** Bose Lifestyle 28 / PS28 SmartSpeaker bus control

## 1. Overview

The Bose Pi software currently provides:

-   AirPlay audio playback through Shairport Sync to the Bose PS28 via
    S/PDIF.
-   Shairport Sync playback-session hooks that log AirPlay selection
    start and stop events.
-   A Python bus-availability check using the PS28 SmartSpeaker bus.
-   Passive GPIO16 monitoring with a 200 ms stability window.
-   A central Python scheduler that combines the bus result and stable
    GPIO16 level into a basic availability state.
-   Clean scheduler shutdown on `Ctrl+C` / `SIGTERM`.

The existing PS28 sniffer remains separate and unchanged.

## 2. Verified Hardware and Software

### Hardware interface

-   Raspberry Pi 5.
-   Bose PS28 connected using a standard network cable.
-   UART0 on GPIO14 (TX) and GPIO15 (RX), configured for 4800 baud, 8
    data bits, no parity, 1 stop bit (8N1).
-   GPIO16 is used as a passive input for the observed bus-related
    signal.
-   The UART transmit/receive setup uses the existing open-collector
    interface.
-   The audio path uses the Allo / InnoMaker Digi One S/PDIF interface.

### Observed GPIO16 levels

  Bose system condition                            GPIO16 level
  ------------------------------------------------ --------------
  PS28 switched on                                 HIGH
  PS28 switched off at the subwoofer main switch   LOW

These levels were observed repeatedly during testing.

### AirPlay audio path

`iPhone / Mac → AirPlay → Shairport Sync → ALSA → Digi One S/PDIF → Bose PS28`

The AirPlay audio path has been tested successfully.

## 3. Bus Availability Check

The diagnostic query used for the system-status check is:

``` text
Request:  0B 00 00 0B
Response: 00 0C 00 F0 FC
```

With the PS28 switched on, the complete request echo followed by the
expected response pattern was observed repeatedly. With the PS28
switched off, no valid response was confirmed.

The separate audio-input status query has also been observed to work:

``` text
Request:  0B 00 05 0E
Response: 00 0C 00 10 1C
```

The current availability function uses the system-status query. It
checks the echoed request, the expected response prefix and the XOR
checksum of the response. The UART read loop has a bounded timeout.

### File: `bus_availability.py`

Location:

``` text
/home/robert/bose-control/bus_availability.py
```

``` python
#!/usr/bin/env python3

import time
import serial

PORT = "/dev/ttyAMA0"
BAUDRATE = 4800
QUERY = bytes.fromhex("0B 00 00 0B")
TIMEOUT = 0.6


def check_bose_available():
    """Prüft, ob die Bose auf die Systemstatus-Abfrage antwortet."""

    with serial.Serial(PORT, BAUDRATE, timeout=0.1) as ser:
        ser.reset_input_buffer()
        ser.write(QUERY)
        ser.flush()

        received = bytearray()
        deadline = time.monotonic() + TIMEOUT

        while len(received) < 9 and time.monotonic() < deadline:
            received.extend(ser.read(9 - len(received)))

    data = bytes(received)

    if len(data) != 9 or data[:4] != QUERY:
        return False

    reply = data[4:]

    if reply[:2] != bytes.fromhex("00 0C"):
        return False

    checksum = 0
    for byte in reply[:4]:
        checksum ^= byte

    return checksum == reply[4]


if __name__ == "__main__":
    try:
        available = check_bose_available()
        print("Bose-Bus: ANTWORT ERKANNT" if available
              else "Bose-Bus: KEINE GÜLTIGE ANTWORT")
    except serial.SerialException as exc:
        print(f"UART-Fehler: {exc}")
```

Run the standalone check with:

``` bash
sudo python3 /home/robert/bose-control/bus_availability.py
```

Observed results:

-   PS28 on: `Bose-Bus: ANTWORT ERKANNT`
-   PS28 off: `Bose-Bus: KEINE GÜLTIGE ANTWORT`

## 4. GPIO16 Monitoring and State Logic

The controller uses the `gpiod` Python API v2. GPIO16 is requested as an
input on `/dev/gpiochip4`. The raw level must remain unchanged for 200
ms before it is accepted as the stable level.

The controller combines the accepted GPIO16 level with the bus
availability result obtained at startup:

  Stable GPIO16   Bus response at startup   Controller state
  --------------- ------------------------- ----------------------------------
  LOW             Either result             `BOSE_UNAVAILABLE`
  HIGH            Valid response            `AVAILABLE_IDLE`
  HIGH            No valid response         No availability state is granted

This avoids treating GPIO16 HIGH alone as proof that the bus is
responding.

### File: `bose_control.py`

Location:

``` text
/home/robert/bose-control/bose_control.py
```

``` python
#!/usr/bin/env python3
"""
Bose Control – zentraler Scheduler
==================================

Aktueller Entwicklungsstand: Beobachtungsmodus.

WICHTIG:
- Der bestehende PS28-Sniffer bleibt unverändert.
- GPIO16 wird als Eingang gelesen.
- Die Bus-Verfügbarkeit wird beim Start einmal geprüft.
- Es werden keine Bose-Steuerbefehle ausgelöst.
- Es gibt kein periodisches Bus-Polling.

Architektur:
- Ein zentraler Scheduler koordiniert später GPIO, Bus und Timer.
- Bus-Transaktionen dürfen niemals unterbrochen werden.
- Bose-Befehle werden nur bei tatsächlichem Bedarf eingeplant.
"""

import logging
import signal
import time
import gpiod
from gpiod.line import Direction
from bus_availability import check_bose_available


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

GPIO_STABLE_TIME = 0.200
MUTE_DELAY = 5.0
POWER_OFF_DELAY = 10.0
SCHEDULER_TICK = 0.010

LOG_FILE = "/home/robert/bose-control/logs/bose-control.log"


# ------------------------------------------------------------
# States
# ------------------------------------------------------------

class State:
    BOSE_UNAVAILABLE = "BOSE_UNAVAILABLE"
    AVAILABLE_IDLE = "AVAILABLE_IDLE"
    AIRPLAY_ACTIVE = "AIRPLAY_ACTIVE"
    STOP_PENDING = "STOP_PENDING"
    MUTED_IDLE = "MUTED_IDLE"
    BOSE_OFF = "BOSE_OFF"
    BUS_ERROR = "BUS_ERROR"


# ------------------------------------------------------------
# Controller
# ------------------------------------------------------------

class BoseController:

    def __init__(self):
        self.state = State.BOSE_UNAVAILABLE

        self.gpio_level = None
        self.gpio_candidate = None
        self.gpio_candidate_since = None

        self.gpio_request = gpiod.request_lines(
            "/dev/gpiochip4",
            consumer="bose-control",
            config={
                16: gpiod.LineSettings(direction=Direction.INPUT)
            },
        )

        self.bose_available = None
        self.airplay_selected = False
        self.last_stop_time = None

        self.bus_transaction_active = False
        self.pending_commands = []
        self.running = True

        logging.info("Bose Control im Beobachtungsmodus gestartet")
        self.check_bus_availability()
        logging.info("GPIO16: Eingang aktiv, Stabilitätsfenster 200 ms")
        logging.info("Bus-Steuerbefehle: deaktiviert")
        logging.info("AirPlay-Dienststeuerung: deaktiviert")
        logging.info("Periodisches Bus-Polling: deaktiviert")

    def check_bus_availability(self):
        """Check the Bose bus; the serial read has a bounded timeout."""
        try:
            available = check_bose_available()
            self.bose_available = available
            logging.info(
                "Bose-Bus: %s",
                "Antwort erkannt" if available
                else "keine gültige Antwort",
            )
            return available
        except Exception:
            self.bose_available = False
            logging.exception("Fehler bei der Bose-Busprüfung")
            return False

    def _update_state_from_inputs(self):
        """Derive the availability state from GPIO16 and the bus result."""
        if self.gpio_level == 0:
            new_state = State.BOSE_UNAVAILABLE
        elif self.gpio_level == 1 and self.bose_available is True:
            new_state = State.AVAILABLE_IDLE
        else:
            # HIGH alone does not prove that the bus is responding.
            return

        if self.state != new_state:
            self.state = new_state
            logging.info("Zustand: %s", self.state)

    def observe(self):
        """One scheduler iteration; no Bose control commands are sent."""
        now = time.monotonic()

        raw_level = self.gpio_request.get_value(16)

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
                "GPIO16 stabil: %s",
                "HIGH" if raw_level else "LOW",
            )
            self._update_state_from_inputs()

        # Bus scheduler: no queued commands are executed in this version.
        # No periodic bus polling is performed.
        #
        # AirPlay timers are defined as design constants, but do not
        # trigger Mute or Power-Off commands in this version.

        return now

    def run(self):
        logging.info("Scheduler läuft; keine Hardwareaktionen")

        while self.running:
            self.observe()
            time.sleep(SCHEDULER_TICK)

        logging.info("Bose Control beendet")

    def shutdown(self, *_):
        logging.info("Beenden angefordert")
        self.running = False
        if hasattr(self, "gpio_request"):
            self.gpio_request.release()


# ------------------------------------------------------------
# Program entry point
# ------------------------------------------------------------

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
```

## 5. Running the Controller

Run the controller from the project directory:

``` bash
cd /home/robert/bose-control
python3 -m py_compile bose_control.py
python3 bose_control.py
```

The controller logs the bus availability result at startup, then reads
GPIO16 continuously. A stable level is logged after the 200 ms stability
interval. Press `Ctrl+C` to stop it.

Typical observed log messages include:

``` text
INFO Bose Control im Beobachtungsmodus gestartet
INFO Bose-Bus: Antwort erkannt
INFO GPIO16: Eingang aktiv, Stabilitätsfenster 200 ms
INFO Bus-Steuerbefehle: deaktiviert
INFO AirPlay-Dienststeuerung: deaktiviert
INFO Periodisches Bus-Polling: deaktiviert
INFO Scheduler läuft; keine Bose-Steuerbefehle
INFO GPIO16 stabil: HIGH
INFO Zustand: AVAILABLE_IDLE
```

With the PS28 switched off, the observed startup result is
`Bose-Bus: keine gültige Antwort`, followed by `GPIO16 stabil: LOW` and
state `BOSE_UNAVAILABLE`.

## 6. Shairport Sync and Playback Hooks

Shairport Sync is installed as a custom build and runs as a systemd
service.

-   Binary: `/usr/local/bin/shairport-sync`
-   Configuration: `/etc/shairport-sync.conf`
-   Service: `/etc/systemd/system/shairport-sync.service`
-   AirPlay device name: `Bose Pi`
-   ALSA output: `iec958:sndallodigione`
-   Output format: 48 kHz, stereo, `S16_LE`

The relevant configuration is:

``` text
general =
{
    name = "Bose Pi";
    service_type = "airplay2";
    output_backend = "alsa";
    mdns_backend = "avahi";
    interpolation = "soxr";
    ignore_volume_control = "no";
};

alsa =
{
    output_device = "iec958:sndallodigione";
    output_rate = 48000;
    output_format = "S16_LE";
    output_channels = 2;
};

sessioncontrol =
{
    run_this_before_play_begins = "/usr/local/bin/bose-playback-start";
    run_this_after_play_ends = "/usr/local/bin/bose-playback-stop";
};
```

The hook scripts are:

-   `/usr/local/bin/bose-playback-start`
-   `/usr/local/bin/bose-playback-stop`

Both scripts have been invoked manually to verify that they run. Actual
AirPlay selection tests confirmed that selecting `Bose Pi` invokes the
START hook and deselecting it invokes the STOP hook. These events
indicate AirPlay output-session selection; they do not necessarily
indicate whether music is currently audible. Rapid switching can produce
short START/STOP event pairs.

The hooks currently provide logging. The scheduler's `airplay_selected`
flag is not yet driven by the hook scripts in the documented state.

## 7. Existing Sniffer

The passive PS28 sniffer remains separate and unchanged.

Primary files:

``` text
/home/robert/ps28-sniffer/ps28_sniffer_v1_reference.py
/home/robert/ps28-sniffer/ps28_sniffer_v2.py
```

The sniffer is used for observing SmartSpeaker bus traffic. The
controller and the availability test do not modify these files.

## 8. Current Project Files

``` text
/home/robert/
├── ps28-sniffer/
│   ├── ps28_sniffer_v1_reference.py
│   └── ps28_sniffer_v2.py
└── bose-control/
    ├── bose_control.py
    ├── bus_availability.py
    ├── logs/
    └── tests/
        ├── bus_status_test.py
        ├── bus_input_status_test.py
        └── bus_availability_test.py
```

## 9. Verified Milestone Summary

-   AirPlay playback through Shairport Sync and S/PDIF to the PS28
    works.
-   Shairport Sync START/STOP hooks run and their selection events have
    been verified.
-   The system-status query produces the expected complete response
    pattern while the PS28 is switched on.
-   The availability check returns a positive result when the PS28 is on
    and no valid response when it is switched off.
-   GPIO16 reads HIGH when the PS28 is on and LOW when it is off in the
    tested setup.
-   GPIO16 is read with `gpiod` API v2 and a 200 ms stability window.
-   The controller maps the observed inputs to `AVAILABLE_IDLE` and
    `BOSE_UNAVAILABLE`.
-   The Python controller compiles and starts/stops cleanly.
-   The controller does not send Bose control commands or perform
    periodic bus polling.
-   The existing passive sniffer remains unchanged.
