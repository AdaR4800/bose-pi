
# Bose-Pi Controller

The controller software connects the Raspberry Pi to the Bose PS28
SmartSpeaker Bus and coordinates the Bose system with AirPlay playback.

## Components

- `bose_control.py` — Main controller process. Monitors GPIO16, processes
  AirPlay START/STOP events, and schedules the mute and power-off commands.
- `bose_bus.py` — UART interface for communication with the Bose system.
- `tests/bus_availability_test.py` — Standalone diagnostic for bus availability
  and audio input status.
- `tests/bus_input_status_test.py` — Standalone diagnostic for audio input
  status.
- `tests/bus_status_test.py` — Standalone diagnostic for bus status.

## Hardware interface

- Raspberry Pi UART: `/dev/ttyAMA0`
- Serial settings: 4800 baud, 8 data bits, no parity, 1 stop bit (8N1)
- GPIO input: GPIO16
- Bus interface: SN74HC07N open-collector buffer

## Dependencies

Install the Python dependencies listed in the repository's `requirements.txt`.

## Important

The diagnostic scripts use the same UART interface as the running controller.
Stop `bose-control.service` before running any of these tests, and restart it
afterwards.

The diagnostic scripts are intended for manual troubleshooting. They are not
part of the normal controller startup.
