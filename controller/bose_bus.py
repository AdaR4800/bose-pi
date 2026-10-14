
#!/usr/bin/env python3
"""Zentrale UART-Schnittstelle für Bose PS28."""

import logging
import threading
import time

import serial

PORT = "/dev/ttyAMA0"
BAUDRATE = 4800
STATUS_QUERY = bytes.fromhex("0B 00 00 0B")
STATUS_TIMEOUT = 0.6


class BoseBus:
    """Verwaltet eine serielle Verbindung innerhalb dieses Prozesses."""

    def __init__(self):
        self._lock = threading.Lock()
        self._ser = None

    def open(self):
        """Öffnet die UART-Verbindung, ohne Daten zu senden."""
        with self._lock:
            if self._ser is not None and self._ser.is_open:
                return

            self._ser = serial.Serial(
                port=PORT,
                baudrate=BAUDRATE,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.05,
                write_timeout=1,
                rtscts=False,
                dsrdtr=False,
            )
            logging.info(
                "Bose-Bus: UART geöffnet (%s, %d Baud)",
                PORT,
                BAUDRATE,
            )

    def check_availability(self):
        """Prüft die Bose mit der bekannten Statusabfrage."""
        with self._lock:
            if self._ser is None or not self._ser.is_open:
                raise RuntimeError("Bose-Bus ist nicht geöffnet")

            self._ser.reset_input_buffer()
            self._ser.write(STATUS_QUERY)
            self._ser.flush()

            received = bytearray()
            deadline = time.monotonic() + STATUS_TIMEOUT

            while len(received) < 9 and time.monotonic() < deadline:
                received.extend(self._ser.read(9 - len(received)))

            data = bytes(received)

            if len(data) != 9 or data[:4] != STATUS_QUERY:
                logging.info("Bose-Bus: keine gültige Statusantwort")
                return False

            reply = data[4:]

            if reply[:2] != bytes.fromhex("00 0C"):
                logging.info("Bose-Bus: unerwartete Statusantwort")
                return False

            checksum = 0
            for byte in reply[:4]:
                checksum ^= byte

            valid = checksum == reply[4]
            logging.info(
                "Bose-Bus: %s",
                "Antwort erkannt" if valid else "Prüfsummenfehler",
            )
            return valid

    def send_sequence(self, commands):
        """Sendet eine Befehlsfolge; Antworten werden nicht ausgewertet."""
        with self._lock:
            if self._ser is None or not self._ser.is_open:
                raise RuntimeError("Bose-Bus ist nicht geöffnet")

            results = []

            for name, command in commands:
                logging.info(
                    "Bose-Bus: sende %s: %s",
                    name,
                    command.hex(" ").upper(),
                )
                written = self._ser.write(command)
                self._ser.flush()

                success = written == len(command)
                results.append((name, success))

                if not success:
                    logging.error(
                        "Bose-Bus: unvollständige Übertragung bei %s",
                        name,
                    )
                    break

            return results

    def close(self):
        """Schließt die UART-Verbindung."""
        with self._lock:
            if self._ser is not None and self._ser.is_open:
                self._ser.close()
                logging.info("Bose-Bus: UART geschlossen")
            self._ser = None
