# Bose-Pi

**Giving a classic Bose Lifestyle sound system a second life with a Raspberry Pi.**

A little reverse engineering, a custom hardware interface, and a stubborn refusal to throw away good speakers.

## The Story

About twenty years ago, when we renovated our house, we invested in a Bose Lifestyle AV18 home cinema system. The installation included five satellite speakers, a subwoofer, and a central receiver. The speakers were permanently wired into the house and mounted high on the walls, providing an elegant surround sound setup.

The system worked beautifully for more than a decade. An Apple AirPort Express, connected through its optical digital output, made it possible to stream music to the Bose receiver.

Then a thunderstorm changed everything.

An indirect lightning strike destroyed the AV18 receiver beyond repair. The speakers, subwoofer, and in-wall cabling survived, but without the central unit, the entire system became unusable.

Replacing everything seemed unnecessary. The speakers were still perfectly good, and our listening habits had changed considerably over the years.

The question was simple:

**Could a Raspberry Pi replace the missing receiver and bring the system back to life?**

## The Idea

The goal is to turn the existing Bose installation into a modern network audio system, with AirPlay as the intended way to stream music from an iPhone.

Instead of rebuilding the complete original receiver, this project focuses on the functions we actually need:

- Digital audio output through S/PDIF.
- Communication with the Bose subwoofer over the SmartSpeaker Bus.
- A dedicated hardware interface between the Raspberry Pi and the Bose system.
- Reliable software control using an explicit state machine.
- A compact, custom-built enclosure.

## The Technical Challenge

The Bose receiver communicates with the subwoofer through two distinct signal paths:

- **Digital audio:** an S/PDIF-based connection carrying the audio signal.
- **SmartSpeaker Bus:** a separate communication interface used for system control.

Publicly available service documentation and patent material provide a starting point for understanding the hardware. Community reverse-engineering work, including Kenneract's Bose-Reverse-Engineering project, provides additional insights into the protocol and its real-world behaviour.

The implementation is based on investigation and testing rather than assuming that every detail in a patent matches the hardware.

## Hardware

The current hardware concept includes:

- Raspberry Pi 5.
- INNO-MAKER Digi One HAT for S/PDIF digital audio.
- A custom SmartSpeaker Bus interface built on a prototype breakout board.
- A purpose-designed, 3D-printed enclosure.

## Project Status

Bose-Pi is an ongoing engineering and reverse-engineering project.

The repository will document the hardware, protocol investigation, software architecture, test results, and practical construction steps as the project develops.

The distinction between experimentally verified behaviour, documented technical information, and planned functionality will be maintained throughout the documentation.

## Documentation

Detailed documentation will be added here as the project evolves.

- [Project architecture](docs/architecture.md) - planned.
- [SmartSpeaker Bus investigation](docs/smartspeaker-bus.md) - planned.
- [Software state machine](docs/state-machine.md) - planned.
- [Hardware and construction](docs/hardware.md) - planned.
- [3D-printed enclosure](docs/enclosure.md) - planned.

## Why Bose-Pi?

The original receiver was destroyed by a thunderstorm. The speakers remained silent for years.

Now, a Raspberry Pi is being taught to speak a language that was never intended for it.

**Keep the speakers. Replace the brain. Let the music play again.**

## Disclaimer

Bose-Pi is an independent, unofficial project and is not affiliated with or endorsed by Bose. Bose and Lifestyle are trademarks of their respective owners.
