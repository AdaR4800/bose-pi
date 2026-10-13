# Documentation

This directory contains the technical documentation for the Bose-Pi project.

Bose-Pi explores how a Raspberry Pi can provide network audio playback for a Bose Lifestyle AV18/PS28 speaker installation while investigating the Bose SmartSpeaker Bus.

## Documents

### System Design

- [Architecture](architecture.md) — Overall system architecture and the separation between digital audio playback and bus communication.
- [Hardware](hardware.md) — Overview of the main components, Raspberry Pi interfaces, UART configuration, passive monitoring, and electrical design.
- [Enclosure Design](enclosure.md) — Mechanical integration and the planned 3D-printed enclosure.
- [Operating Mode and Serial Interface](operating-mode.md) — Normal SmartSpeaker operation, serial-interface configuration, and operating-mode restrictions.

### Hardware Documentation

- [Hardware Build Guide](hardware/build-guide.md) — Components, assembly, electrical connections, and validation procedures.
- [Reference Wiring](hardware/reference-wiring.md) — Wiring diagrams, GPIO assignments, and connector notes.
- [SmartSpeaker Bus](smartspeaker-bus.md) — Electrical interface details and findings from the Bose communication bus investigation.

### SmartSpeaker Bus Investigation

- [State Machine](state-machine.md) — The planned approach to understanding and implementing the PS28 communication and state model.
- [PS28 Findings — 2026-10-11](findings/2026-10-11-ps28-findings.md) — Observed commands, responses, and the operational sequence that produced audible playback.

### Evidence and Verification

- [Evidence and Verification Status](EVIDENCE.md) — Evidence categories, completed tests, and remaining verification work.

## Software

The passive bus sniffer and its supporting documentation are located in the [`scripts`](../scripts/) directory.

The sniffer is intended for passive observation. Captured bytes and protocol interpretations should be distinguished clearly: an observed byte sequence does not by itself establish the meaning of a message or prove that the PS28 generated a response.

## Project Status

The documentation describes the current implementation and investigation. Details that have not yet been verified against measurements, source code, or the physical hardware should be treated as provisional.

As the project progresses, measured results, verified circuit details, protocol findings, and reproducible test procedures will be added to the relevant documents.

For contribution guidelines, see [Contributing to Bose-Pi](../CONTRIBUTING.md).
