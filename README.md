# Bose-Pi

**Giving a classic Bose Lifestyle sound system a second life with a Raspberry Pi.**

An independent hardware and software reverse-engineering project to restore a Bose Lifestyle AV28/PS28 speaker installation using modern AirPlay audio and a custom SmartSpeaker Bus interface.

> Keep the speakers. Replace the brain. Let the music play again.

## The Story

About twenty years ago, we installed a Bose Lifestyle AV18 home cinema system in our house. The installation included five satellite speakers, a subwoofer, and a central receiver. The speakers were permanently wired into the house and mounted high on the walls.

An Apple AirPort Express, connected through its optical digital output, later made it possible to stream music to the Bose receiver.

The system worked for more than a decade. Then an indirect lightning strike destroyed the central receiver beyond repair. The speakers, subwoofer, and in-wall cabling survived, but without the receiver, the installation became unusable.

Replacing everything seemed unnecessary. The speakers were still perfectly good, and our listening habits had changed.

Could a Raspberry Pi replace the missing electronics and bring the system back to life?

That question became Bose-Pi.

Bose-Pi has a second goal beyond replacing a failed central receiver: bringing modern Apple AirPlay 2 streaming to a classic Bose Lifestyle sound system that is around twenty years old.

The approach is deliberately non-invasive. The Raspberry Pi provides the modern audio source and interfaces with the Bose SmartSpeaker Bus externally. The original subwoofer does not need to be opened, its internal electronics do not need to be modified, and the existing speaker installation and wiring can remain in place.

This makes it possible to preserve a working legacy sound system while adding a modern way to stream music — without replacing the speakers, rewiring the installation, or dismantling the subwoofer.

## Project Goals

The project aims to restore the essential functionality of the surviving Bose speaker installation without recreating the entire original receiver.

The main objectives are:

- Provide network audio playback through AirPlay 2.
- Generate digital audio using an INNO-MAKER Digi One HAT.
- Investigate and implement the Bose SmartSpeaker Bus interface.
- Develop reliable control software for the Raspberry Pi.
- Build a compact hardware assembly and a custom 3D-printed enclosure.
- Document the findings so that others can reproduce and understand the work.
- Provide a non-invasive way to add Apple AirPlay 2 to a classic Bose Lifestyle system while preserving the original subwoofer hardware and existing speaker wiring.
- Offer an alternative to the original central receiver when it fails or is no longer available, without requiring a complete replacement of the speaker installation.

## Current Status

### Verified: Digital Audio

The following audio path is operational:

`AirPlay 2 → Shairport Sync 5.5.2 → ALSA → INNO-MAKER Digi One → S/PDIF`

Shairport Sync runs as a system service. The configured ALSA device is `iec958:sndallodigione`. The Digi One generates the optical digital audio signal.

This verifies the Raspberry Pi audio-output path. Successful playback through the original Bose subwoofer still depends on validating the complete interface and system behaviour.

### Verified: Raspberry Pi UART

The development platform is a Raspberry Pi 5 running Debian GNU/Linux 13 (trixie).

The UART interface used for the Bose bus investigation is:

- Device: `/dev/ttyAMA0`
- TX: GPIO14, physical pin 8
- RX: GPIO15, physical pin 10

The passive sniffer is configured for 4800 baud, 8 data bits, no parity, and 1 stop bit (8N1). The implementation supports decoding complete data bursts.

### Verified: Passive Sniffer

The sniffer is designed to observe bus traffic without actively transmitting commands.

A captured byte sequence used during sniffer validation is:

`55 00 FF A5 0B`

Captured bytes are evidence of observed traffic; their protocol meaning must be established separately.

### In Progress: SmartSpeaker Bus

The Bose SmartSpeaker Bus is a separate control path from the digital audio connection.

Publicly available service documentation, patent material, and community reverse-engineering work provide useful starting points. The actual protocol must nevertheless be validated against the relevant hardware.

The complete PS28 initialization sequence, message semantics, and required state transitions remain under investigation.

### In Progress: Control Software

The software architecture is intended to separate UART access, protocol handling, hardware detection, and audio-service management.

The final state machine will be documented against the actual implementation and verified behaviour rather than assumed protocol functionality.

## Hardware

The current design uses:

- Raspberry Pi 5.
- INNO-MAKER Digi One HAT for S/PDIF digital audio.
- Custom SmartSpeaker Bus interface circuitry.
- A prototype breakout board for the bus interface.
- A planned custom 3D-printed enclosure.

The original Bose central receiver is no longer available. The surviving installation consists of one subwoofer and five satellite speakers.

## Documentation

The technical documentation is organized in the [`docs`](docs/README.md) directory.

- [Documentation Index](docs/README.md) — Overview of all technical documents.
- [System Architecture](docs/architecture.md) — Overall system design and component interactions.
- [Hardware](docs/hardware.md) — Hardware components, interfaces, UART configuration, and electrical design considerations.
- [SmartSpeaker Bus Investigation](docs/smartspeaker-bus.md) — Bus observations, protocol investigation, and current findings.
- [Software State Machine](docs/state-machine.md) — Planned control logic and the investigation of PS28 behaviour.
- [Enclosure Design](docs/enclosure.md) — Mechanical integration and the planned 3D-printed enclosure.

## Development Principles

Bose-Pi distinguishes between:

- **Verified:** confirmed through measurements or repeatable tests.
- **Observed:** recorded during an experiment, with interpretation still subject to investigation.
- **Planned:** intended functionality that has not yet been verified.

The project does not claim to reproduce the complete Bose protocol or all original receiver functionality.

## Acknowledgements

**Kenneract — [Bose-Reverse-Engineering](https://github.com/Kenneract/Bose-Reverse-Engineering)**

This project builds on the valuable reverse-engineering work documented by Kenneract on the Bose 3·2·1 GS Series III system, particularly the investigation of the Bose SmartSpeaker protocol.

Kenneract's research provides an important technical reference for understanding the bus architecture, serial communication, and observed protocol behaviour. It has informed the direction of the Bose-Pi investigation and helps guide our own experiments.

Bose-Pi is an independent project focused on restoring a surviving Bose Lifestyle AV18/PS28 installation. Our hardware, measurements, and implementation are documented separately, and protocol assumptions are verified against our own hardware wherever possible.

We gratefully acknowledge Kenneract's work and contribution to the Bose reverse-engineering community.

AI-assisted research and development tools have also been used during the engineering process.

## Disclaimer

Bose-Pi is an independent, unofficial project and is not affiliated with or endorsed by Bose. Bose and Lifestyle are trademarks of their respective owners.
