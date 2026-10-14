
#!/usr/bin/env python3
"""Standalone diagnostic test for the Bose SmartSpeaker Bus status query.

Do not run this script while bose_control.py is running, because both
programs use the same UART interface.
"""

import time
import serial

PORT = "/dev/ttyAMA0"
BAUDRATE = 4800
STATUS_QUERY = bytes.fromhex("0B 00 00 0B")
READ_WINDOW = 0.5


def main():
    with serial.Serial(
        port=PORT,
        baudrate=BAUDRATE,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.05,
        write_timeout=1,
        rtscts=False,
        dsrdtr=False,
    ) as ser:
        ser.reset_input_buffer()

        print(
            "Sending Bose bus status query:",
            STATUS_QUERY.hex(" ").upper(),
        )

        ser.write(STATUS_QUERY)
        ser.flush()

        received = bytearray()
        deadline = time.monotonic() + READ_WINDOW

        while time.monotonic() < deadline:
            received.extend(ser.read(ser.in_waiting or 1))

        data = bytes(received)

        print("Raw received bytes:", data.hex(" ").upper() or "(no data)")

        if data.startswith(STATUS_QUERY):
            response = data[len(STATUS_QUERY):]
            print("Response without query echo:", response.hex(" ").upper())
        else:
            response = data
            print("No matching query echo at the beginning of the response.")

        expected = bytes.fromhex("00 0C 00 F0 FC")

        print("Expected response:", expected.hex(" ").upper())
        print("Observed response:", response.hex(" ").upper())

        if response == expected:
            print("Result: Expected Bose bus status response received.")
        else:
            print("Result: Response differs from the expected bytes.")


if __name__ == "__main__":
    main()
