# Hardware

## 1. Overview

Bose-Pi uses a Raspberry Pi 5 to provide network audio playback and to investigate the control interface of a surviving Bose Lifestyle AV28/PS28 speaker installation.

The hardware design separates the digital audio output from the SmartSpeaker Bus interface.

This document records the current hardware configuration and identifies electrical details that must be confirmed against the final circuit.

## 2. Main Components

| Component | Purpose | Status |
|---|---|---|
| Raspberry Pi 5 Model B | Main computing platform | In use |
| INNO-MAKER Digi One HAT | S/PDIF digital audio output | In use |
| GeeekPi prototype breakout board | Base for custom interface circuitry | Selected |
| SN74HC07 open-collector buffer | Part of the SmartSpeaker Bus interface | Design component |
| Bose subwoofer and five satellite speakers | Existing audio system | Existing installation |

The original Bose AV18 central receiver was destroyed and is no longer available.

## 3. Raspberry Pi Platform

The development platform is a Raspberry Pi 5 Model B, Revision 1.0.

The recorded software environment is:

- Debian GNU/Linux 13 (trixie).
- Linux kernel `6.18.50+rpt-rpi-2712`.
- Python 3.13.5.
- PySerial 3.5 was installed for serial experiments.

The passive sniffer uses the Python `gpiod` bindings and the libgpiod 2.x API.

## 4. Digital Audio Interface

The INNO-MAKER Digi One HAT provides the S/PDIF digital audio output.

The configured ALSA device is:

`iec958:sndallodigione`

The operational audio software path is:

`AirPlay 2 → Shairport Sync 5.5.2 → ALSA → Digi One → S/PDIF`

The original RCA connector was removed to reduce the physical height and bulk of the assembly.

The final connector arrangement and enclosure dimensions should be documented with photographs and mechanical drawings when available.

## 5. UART Interface

The UART interface used during the SmartSpeaker Bus investigation is:

| Signal | Raspberry Pi connection |
|---|---|
| UART device | `/dev/ttyAMA0` |
| TXD0 | GPIO14, physical pin 8 |
| RXD0 | GPIO15, physical pin 10 |
| Serial configuration | 4800 baud, 8N1 for the bus investigation |

The Raspberry Pi 5 also exposes other serial devices. The device name must not be changed without checking the UART configuration and GPIO mapping.

The UART connection is intended for active serial communication. Passive bus observation is handled separately.

## 6. Passive Monitor

The passive sniffer observes the SmartSpeaker Bus using GPIO16, physical pin 36.

Its current configuration is:

| Parameter | Value |
|---|---|
| GPIO | GPIO16 |
| Physical pin | 36 |
| Capture method | GPIO edge events |
| Baud-rate assumption | 4800 |
| Serial framing | 8N1 |
| Direction | Receive-only / passive |

The passive monitor is independent of the active UART transmit path.

Its input must be electrically compatible with the monitored bus. The final schematic should establish the input protection, voltage levels, and connection point.

## 7. SmartSpeaker Bus Electrical Interface

The custom interface design includes an SN74HC07 open-collector buffer.

The purpose of the interface is to provide appropriate electrical coupling between the Raspberry Pi and the Bose SmartSpeaker Bus.

The final circuit documentation must identify:

- The exact SN74HC07 device and manufacturer.
- The supply voltage used by the device.
- The bus pull-up arrangement.
- The Raspberry Pi TX connection.
- The bus RX connection.
- The common reference and grounding arrangement.
- Any protection or isolation components.
- The measured logic levels on the bus.

The supply voltage, resistor values, and exact pin-to-pin wiring must be taken from the final schematic and verified circuit. They are intentionally not inferred here.

**Do not connect the Raspberry Pi GPIO directly to the Bose bus until electrical compatibility has been established.**

## 8. Wiring and Test Points

The hardware documentation should eventually include a labelled wiring diagram showing:

1. Raspberry Pi UART TX and RX.
2. GPIO16 passive-monitor input.
3. SN74HC07 connections.
4. The SmartSpeaker Bus connector.
5. The Digi One S/PDIF output.
6. Ground and power connections.
7. Test points for measuring bus voltage and signal timing.

Photographs of the actual assembled board should accompany the diagram so that the documented design can be compared with the physical implementation.

## 9. Mechanical Design

The project aims to integrate the Raspberry Pi, audio interface, and custom bus circuitry into a compact enclosure.

The original Digi One RCA connector was removed to support a lower-profile assembly.

The final enclosure is intended to be 3D-printed. Its design, dimensions, mounting points, ventilation requirements, and connector positions will be documented separately.

See [enclosure.md](enclosure.md) when that document becomes available.

## 10. Hardware Validation

The following checks are required for a reproducible build:

- Confirm the Raspberry Pi UART device and GPIO mapping.
- Verify the Digi One audio output independently.
- Measure the SmartSpeaker Bus idle voltage and signal levels.
- Verify the SN74HC07 supply and output configuration against its data sheet.
- Confirm the GPIO16 monitor input remains within safe limits.
- Verify the actual wiring against the schematic.
- Test the complete assembly before connecting it permanently to the Bose system.

## 11. Current Status

The Raspberry Pi, Digi One audio interface, UART configuration, and GPIO16 passive-monitor approach have been established as parts of the project.

The final electrical interface schematic, verified voltage levels, component values, and enclosure drawings should be added as the physical build is finalized.
