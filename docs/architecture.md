# System Architecture

## 1. Overview

Bose-Pi is an independent hardware and software reverse-engineering project. Its objective is to restore the essential functionality of a surviving Bose Lifestyle AV18/PS28 speaker installation using a Raspberry Pi 5, modern network audio, and a custom SmartSpeaker Bus interface.

The architecture separates digital audio generation from control-bus communication.

## 2. Hardware Components

### Raspberry Pi 5

The Raspberry Pi 5 is the central computing platform. It runs Debian GNU/Linux 13 (trixie) and hosts the audio and serial communication software.

### INNO-MAKER Digi One HAT

The Digi One provides the S/PDIF digital audio output.

The original RCA connector was removed to support a compact hardware assembly.

The configured ALSA device is:

`iec958:sndallodigione`

### SmartSpeaker Bus Interface

A custom hardware interface is being developed to connect the Raspberry Pi to the Bose SmartSpeaker Bus.

The interface design includes an SN74HC07 open-collector buffer. The circuit's final electrical characteristics and supply configuration must be documented against the actual hardware implementation.

### Bose Speaker System

The surviving installation consists of one Bose subwoofer and five satellite speakers. The original central receiver was destroyed and is no longer available.

## 3. Digital Audio Path

The configured and operational Raspberry Pi audio chain is:

`AirPlay 2 → Shairport Sync 5.5.2 → ALSA → INNO-MAKER Digi One → S/PDIF`

Shairport Sync provides the AirPlay-compatible audio service. ALSA routes the audio to the Digi One, which generates the digital output.

This confirms the Raspberry Pi audio-output path. Complete playback through the Bose system must be evaluated separately from the operation of the audio service itself.

## 4. Control Communication Path

The control path is separate from the digital audio path.

`Raspberry Pi UART → electrical interface → Bose SmartSpeaker Bus`

The active UART interface uses:

- TX: GPIO14, physical pin 8.
- RX: GPIO15, physical pin 10.
- Serial device: `/dev/ttyAMA0`.
- Working bus configuration: 4800 baud, 8N1.

The electrical interface includes an SN74HC07N open-collector buffer for the transmit path.

### Independent Passive Observation

The bus is also observed through a separate passive sniffer:

`Bose SmartSpeaker Bus → GPIO16 → libgpiod 2.x → byte decoder`

GPIO16 (physical pin 36) captures signal edges. The sniffer reconstructs UART bytes and groups them into bursts without transmitting commands.

The active UART and passive sniffer serve different purposes. Their observations can be correlated to investigate transmission timing, possible bus echo, and potential PS28 responses.

The exact protocol behaviour required for reliable operation remains subject to repeatable hardware testing.

## 5. UART Configuration

The development platform uses the following UART connection:

| Parameter | Configuration |
|---|---|
| Raspberry Pi | Raspberry Pi 5 |
| Serial device | `/dev/ttyAMA0` |
| TX signal | GPIO14, physical pin 8 |
| RX signal | GPIO15, physical pin 10 |
| Working bus baud rate | 4800 baud |
| Serial framing | 8N1 |

The UART settings above describe the current bus investigation configuration. The final application configuration should be checked against the deployed software.

## 6. Passive Bus Sniffer

The passive sniffer observes serial traffic without actively transmitting commands.

Its current configuration uses 4800 baud, 8 data bits, no parity, and one stop bit.

The sniffer can decode complete data bursts. Captured byte sequences are recorded independently from their interpretation, allowing protocol assumptions to be revised as further evidence becomes available.

## 7. Software Responsibilities

The software architecture separates the following responsibilities:

- AirPlay-compatible audio service management.
- ALSA audio output.
- UART access and passive data capture.
- SmartSpeaker Bus protocol handling.
- Hardware detection and operational state management.
- Diagnostics and error handling.

The final state-machine behaviour must correspond to the actual implementation and verified interactions with the Bose hardware.

## 8. Design Principles

- Preserve the existing speaker installation.
- Reuse working audio hardware wherever practical.
- Separate digital audio from control communication.
- Keep electrical interfacing separate from protocol implementation.
- Base protocol conclusions on repeatable tests and captured evidence.
- Distinguish verified behaviour from interpretation and planned functionality.

## 9. Current Status

The AirPlay-compatible audio service and the Raspberry Pi digital audio output path are operational.

The UART configuration and passive sniffer are part of the bus investigation.

The complete SmartSpeaker Bus protocol, the required startup sequence, and the final control state machine remain under investigation.

Further details are maintained in the SmartSpeaker Bus and state-machine documentation.
