# System Architecture

## Overview

Bose-Pi replaces the failed Bose AV28 central console of a Bose Lifestyle 28 system with a Raspberry Pi 5.

The implementation provides network audio playback and a separate interface to the Bose SmartSpeaker Bus. The original PS28 powered bass module and the existing satellite speakers remain in use.

The system consists of three distinct signal paths:

1. Digital audio playback.
2. Active serial communication with the SmartSpeaker Bus.
3. Passive monitoring of bus activity.

These paths have different purposes and must not be confused with one another.

## 1. Audio Path

The Raspberry Pi receives audio over AirPlay and forwards it to the INNO-MAKER Digi One HAT for digital output.

```text
iPhone / Mac
    |
    | AirPlay
    v
Shairport Sync
    |
    | ALSA
    v
INNO-MAKER Digi One HAT
    |
    | S/PDIF digital audio
    v
Bose PS28
    |
    v
Bose Lifestyle satellite speakers
```

Shairport Sync receives the AirPlay stream. ALSA provides the Linux audio interface used by the playback software. The INNO-MAKER Digi One HAT provides the S/PDIF output connected to the Bose system.

The digital audio connection is independent of the SmartSpeaker Bus control interface.

## 2. Active SmartSpeaker Bus Interface

The Raspberry Pi communicates with the Bose SmartSpeaker Bus through its UART0 serial interface and an SN74HC07N open-collector interface.

```text
Raspberry Pi 5
    |
    | UART0
    | TX: GPIO14
    | RX: GPIO15
    v
SN74HC07N interface
    |
    | Project-specific electrical interface
    v
Bose SmartSpeaker Bus
    |
    v
Bose PS28
```

The serial interface uses the following configuration:

| Parameter | Value |
|---|---|
| Linux device | `/dev/ttyAMA0` |
| Transmit | GPIO14, physical pin 8 |
| Receive | GPIO15, physical pin 10 |
| Baud rate | 4800 |
| Data bits | 8 |
| Parity | None |
| Stop bits | 1 |

The electrical interface is described in [Hardware](hardware.md) and the [Hardware Build Guide](hardware/build-guide.md). Follow the reference wiring documentation rather than inferring connections from this logical diagram.

The cable between the interface and the PS28 is a standard network cable used for project-specific signals. It does not carry Ethernet traffic.

## 3. Passive Bus Monitoring

A separate Raspberry Pi GPIO input is used to observe SmartSpeaker Bus activity.

```text
Bose SmartSpeaker Bus
    |
    | Passive observation
    v
Raspberry Pi GPIO16
    |
    v
PS28 sniffer
    |
    v
Captured and decoded traffic
```

The passive sniffer is used to record and inspect bus traffic. It is logically separate from the active UART communication path.

The sniffer's purpose is observation. It must not be described as an active controller or as a source of transmitted Bose commands.

## 4. Hardware Components

The documented implementation uses:

- Raspberry Pi 5 Model B.
- INNO-MAKER Digi One HAT for S/PDIF output.
- GeeekPi prototype breakout board.
- SN74HC07N open-collector buffer.
- The existing Bose Lifestyle 28 PS28 bass module and satellite speakers.

The electrical connections, component arrangement, and construction details are documented in the hardware-specific documents.

## 5. Software Responsibilities

The software is divided into separate responsibilities:

- **Audio playback:** Receives AirPlay audio and supplies it to the ALSA playback path.
- **Serial communication:** Provides access to UART0.
- **Bus handling:** Processes the SmartSpeaker Bus messages required by the implementation.
- **System control:** Coordinates the documented operating behaviour.
- **Passive monitoring:** Captures bus activity through GPIO16.

The exact implementation, service configuration, and runtime behaviour are documented in [Control Software](control-software.md) and [Operating Mode](operating-mode.md).

## 6. Operating Scope

Bose-Pi uses the normal SmartSpeaker operating mode. TAP mode is excluded.

The project replaces selected functions of the failed AV28 console. It does not claim to reproduce every feature of the original Bose Lifestyle system.

Protocol descriptions distinguish between directly observed traffic, behaviour verified on the actual hardware, and interpretations of the protocol.

## Related Documentation

- [Hardware](hardware.md)
- [Hardware Build Guide](hardware/build-guide.md)
- [Reference Wiring](hardware/reference-wiring.md)
- [SmartSpeaker Bus](smartspeaker-bus.md)
- [Control Software](control-software.md)
- [Operating Mode](operating-mode.md)
- [State Machine](state-machine.md)
