# Bose-Pi Scripts

This directory contains software tools developed for the Bose-Pi project.

## Passive PS28 SmartSpeaker Bus Sniffer

### File

`ps28_sniffer.py`

### Purpose

The sniffer passively observes electrical transitions on the Bose SmartSpeaker Bus using Raspberry Pi GPIO16.

It captures edge events, reconstructs serial bytes, and prints the decoded data with timestamps.

**The sniffer is receive-only. It does not transmit commands onto the bus.**

### Hardware

- Raspberry Pi 5
- GPIO16, physical pin 36
- An appropriate electrical interface to the SmartSpeaker Bus

Do not connect Raspberry Pi GPIO directly to a bus whose electrical levels and compatibility have not been verified.

### Serial Configuration

| Parameter | Value |
|---|---|
| Baud rate | 4800 |
| Data bits | 8 |
| Parity | None |
| Stop bits | 1 |
| Framing | 8N1 |
| Capture method | GPIO edge events |
| GPIO library | libgpiod Python bindings, version 2.x |

### Software Requirements

The script requires:

- Python 3
- The Python `gpiod` bindings compatible with libgpiod 2.x
- Permission to access `/dev/gpiochip0`

The exact installation procedure depends on the Debian packages and Python environment used on the Raspberry Pi.

### Running the Sniffer

From the directory containing the script, run:

```bash
python3 ps28_sniffer.py
```

Press `Ctrl-C` to stop the program.

Depending on the system configuration, access to GPIO may require appropriate permissions or elevated privileges.

### Output

The sniffer prints timestamps and decoded bytes. A typical line has the following structure:

```text
TIMESTAMP         RX  BYTE
```

An idle-time annotation may be printed when a sufficiently long interval occurs between decoded bytes.

The timestamps are used to investigate the timing and grouping of observed bus traffic.

### Limitations

The sniffer reconstructs bytes from GPIO edge events. It does not automatically establish the meaning of every byte or identify the transmitting device.

In particular:

- A decoded byte is not necessarily a complete protocol message.
- Burst boundaries do not necessarily correspond to protocol frame boundaries.
- A captured sequence must not be interpreted as a PS28 response without supporting evidence.
- The script does not implement active bus communication or the complete SmartSpeaker protocol.

The decoder and protocol analysis may evolve as additional measurements become available.

## Development Status

The passive sniffer is part of the SmartSpeaker Bus investigation. Its output supports further analysis of timing, message boundaries, and protocol behaviour.
