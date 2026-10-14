
#!/usr/bin/env python3
"""Diagnostic test for Bose SmartSpeaker Bus availability and input status.

This is a standalone diagnostic script. Do not run it while bose_control.py
is running, because both programs use the same UART interface.
"""

import time
import serial

PORT = "/dev/ttyAMA0"
BAUDRATE = 4800
READ_WINDOW = 0.5

STATUS_QUERY = bytes.fromhex("0B 00 00 0B")
INPUT_STATUS_QUERY = bytes.fromhex("0B 00 05 0E")


def read_response(ser, query):
    """Send a query and collect the received bytes for a short period."""
    ser.reset_input_buffer()
    ser.write(query)
    ser.flush()

    received = bytearray()
    deadline = time.monotonic() + READ_WINDOW

    while time.monotonic() < deadline:
        received.extend(ser.read(ser.in_waiting or 1))

    data = bytes(received)

    print(f"Query sent: {query.hex(' ').upper()}")
    print(f"Raw response: {data.hex(' ').upper() or '(no data)'}")

    if data.startswith(query):
        data = data[len(query):]
        print(f"Response without query echo: {data.hex(' ').upper()}")

    return data


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
        print("Testing Bose bus availability...")
        availability = read_response(ser, STATUS_QUERY)

        print("\nTesting Bose audio input status...")
        input_status = read_response(ser, INPUT_STATUS_QUERY)

        print("\nExpected responses observed during development:")
        print("Availability: 00 0C 00 F0 FC")
        print("Input status: 00 0C 00 10 1C")

        print("\nDiagnostic finished.")
        print("Availability bytes:", availability.hex(" ").upper())
        print("Input status bytes:", input_status.hex(" ").upper())


if __name__ == "__main__":
    main()

