# Documentation

This directory contains the technical documentation for Bose-Pi, a Raspberry Pi-based replacement for the failed Bose AV28 central console in a Bose Lifestyle 28 system.

The documentation covers the system architecture, hardware construction, digital audio path, SmartSpeaker Bus interface, software components, and operating behaviour.

## Getting Started

If you want to understand or reproduce the project, read the documents in this order:

1. [System Architecture](architecture.md) — Understand the audio path, control path, and passive monitoring interface.
2. [Hardware Overview](hardware.md) — Review the components and electrical interfaces.
3. [Hardware Build Guide](hardware/build-guide.md) — Follow the assembly instructions.
4. [Reference Wiring](hardware/reference-wiring.md) — Check the wiring, GPIO assignments, and connector details.
5. [SmartSpeaker Bus](smartspeaker-bus.md) — Understand the bus interface and documented communication behaviour.
6. [Control Software](control-software.md) — Review the software components and their responsibilities.
7. [Operating Mode](operating-mode.md) — Review the serial configuration and operating restrictions.
8. [State Machine](state-machine.md) — Understand the documented system states and transitions.

The [Enclosure Design](enclosure.md) document covers the mechanical integration of the hardware and should be treated separately from the electrical build instructions.

## Document Responsibilities

| Document | Purpose |
|---|---|
| [Architecture](architecture.md) | Overall system design and signal paths |
| [Hardware](hardware.md) | Components, interfaces, and electrical design |
| [Hardware Build Guide](hardware/build-guide.md) | Practical hardware assembly |
| [Reference Wiring](hardware/reference-wiring.md) | Wiring diagram and connection reference |
| [SmartSpeaker Bus](smartspeaker-bus.md) | Bus interface, observations, and validated behaviour |
| [Control Software](control-software.md) | Software structure and component responsibilities |
| [Operating Mode](operating-mode.md) | Serial configuration and operating restrictions |
| [State Machine](state-machine.md) | System states, transitions, and control behaviour |
| [Enclosure Design](enclosure.md) | Mechanical integration and enclosure work |

## Software Tools

The [`scripts/`](../scripts/) directory contains the passive PS28 SmartSpeaker Bus sniffer and its supporting documentation.

The sniffer observes bus activity through a separate Raspberry Pi GPIO input. It is distinct from the active UART communication path.

## Technical Accuracy

The documentation distinguishes between:

- **Verified behaviour:** functionality tested on the actual hardware.
- **Observed traffic:** bytes or electrical activity captured during measurements.
- **Protocol interpretation:** conclusions drawn from observed traffic and subsequent testing.

An observed byte sequence alone does not establish its meaning or prove which device transmitted it. Claims about operating behaviour and protocol semantics should be supported by repeatable tests or clearly identified evidence.

The normal SmartSpeaker operating mode is used. TAP mode is outside the scope of this project.

## Scope

Bose-Pi restores selected functionality of the original Bose Lifestyle 28 installation using a Raspberry Pi 5. It provides network audio playback and a separate interface to the Bose SmartSpeaker Bus.

The project does not claim to reproduce every feature of the original AV28 console. The documented hardware and software describe the implementation and behaviour established for this project.
