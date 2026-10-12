# Documentation

This directory contains the technical documentation for the Bose-Pi project.

Bose-Pi explores how a Raspberry Pi can provide network audio playback for a Bose Lifestyle AV18/PS28 speaker installation while investigating the Bose SmartSpeaker Bus.

## Documents

### System Design

- [Architecture](architecture.md) — Overall system architecture and the separation between digital audio playback and bus communication.
- [Hardware](hardware.md) — Main components, Raspberry Pi interfaces, UART configuration, passive monitoring, and electrical design considerations.
- [Enclosure Design](enclosure.md) — Mechanical integration and the planned 3D-printed enclosure.

### SmartSpeaker Bus Investigation

- [SmartSpeaker Bus](smartspeaker-bus.md) — Current findings and the investigation of the Bose communication bus.
- [State Machine](state-machine.md) — The planned approach to understanding and implementing the PS28 communication and state model.

## Software

The passive bus sniffer and its supporting documentation are located in the [`scripts`](../scripts/) directory.

The sniffer is intended for passive observation. Captured bytes and protocol interpretations should be distinguished clearly: an observed byte sequence does not by itself establish the meaning of a message or prove that the PS28 generated a response.

## Project Status

The documentation describes the current implementation and investigation. Details that have not yet been verified against measurements, source code, or the physical hardware should be treated as provisional.

As the project progresses, measured results, verified circuit details, protocol findings, and reproducible test procedures will be added to the relevant documents.
