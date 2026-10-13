# Hardware

## 1. Overview

Bose-Pi uses a Raspberry Pi 5 to provide Apple AirPlay 2 audio playback for an existing Bose Lifestyle AV28/PS28 speaker installation and to investigate its SmartSpeaker Bus control interface.

The project has two complementary goals:

- Add modern network audio streaming to the original speaker installation without opening the subwoofer or modifying its internal electronics or existing speaker wiring.
- Provide an alternative to the original central receiver, which is no longer available in this project.

The hardware design separates the digital audio path from the SmartSpeaker Bus interface. Audio playback and bus communication are independent functions and should be tested independently.

## 2. Main Components

| Component | Purpose | Status |
|---|---|---|
| Raspberry Pi 5 Model B, Revision 1.0 | Main computing platform | In use |
| INNO-MAKER Digi One HAT | S/PDIF digital audio output | In use |
| GeeekPi prototype breakout board | Base for custom interface circuitry | Selected |
| SN74HC07N open-collector buffer | SmartSpeaker Bus interface | In use in the interface design |
| Bose PS28 subwoofer and five satellite speakers | Original audio system | Existing installation |

The original Bose AV28 central receiver was destroyed and is no longer available.

## 3. Raspberry Pi Platform

The recorded development environment is:

- Debian GNU/Linux 13 (trixie).
- Linux kernel `6.18.50+rpt-rpi-2712`.
- Python 3.13.5.
- PySerial 3.5.
- Python `gpiod` bindings using the libgpiod 2.x API.

The Raspberry Pi provides separate interfaces for digital audio, active serial communication, and passive bus observation.

## 4. Digital Audio Interface

The INNO-MAKER Digi One HAT provides the S/PDIF digital audio output.

The configured ALSA device is:

`iec958:sndallodigione`

The operational audio path is:

`Apple AirPlay 2 → Shairport Sync 5.5.2 → ALSA → INNO-MAKER Digi One → S/PDIF → Bose PS28`

Audible playback through the PS28 has been demonstrated. AirPlay volume control also worked with the Shairport Sync configuration set to `ignore_volume_control = "no"`.

The original RCA connector was removed to reduce the height and bulk of the assembly.

See the [Hardware Build Guide](hardware/build-guide.md) and [Reference Wiring](hardware/reference-wiring.md) for physical integration details.

## 5. Active UART Interface

The active UART used for SmartSpeaker Bus communication is configured as follows:

| Signal | Raspberry Pi connection |
|---|---|
| UART device | `/dev/ttyAMA0` |
| TXD0 | GPIO14, physical pin 8 |
| RXD0 | GPIO15, physical pin 10 |
| Serial configuration | 4800 baud, 8N1 |

The Raspberry Pi exposes other serial devices. Do not change the UART device or pin configuration without checking the active configuration and GPIO mapping.

The UART is used for active serial communication. Its transmitted and received bytes must not automatically be interpreted as proof of a PS28 response: echo, bus activity, and actual responses need to be distinguished.

## 6. Passive SmartSpeaker Bus Monitor

The passive sniffer observes the bus independently through GPIO16, physical pin 36.

| Parameter | Value |
|---|---|
| GPIO | GPIO16 |
| Physical pin | 36 |
| Capture method | GPIO edge events |
| Baud-rate assumption | 4800 |
| Serial framing | 8N1 |
| Direction | Passive observation; no transmission |

The sniffer is implemented in `scripts/ps28_sniffer.py`. Its 3 ms idle-gap setting groups observed activity into bursts; this is a software grouping parameter, not proof of a protocol-defined message boundary.

Passive observations and active UART traffic must remain distinguishable in logs and documentation.

## 7. SmartSpeaker Bus Electrical Interface

The interface uses an SN74HC07N open-collector buffer to couple the Raspberry Pi UART to the Bose SmartSpeaker Bus.

The documented circuit uses a 3.3 V supply for the SN74HC07N. The detailed wiring documentation identifies the relevant bus connection, pull-up arrangement, series resistor, and decoupling capacitor.

Consult the [SmartSpeaker Bus documentation](smartspeaker-bus.md) and [Reference Wiring](hardware/reference-wiring.md) for the circuit details.

The electrical interface should be reproduced from the documented circuit and checked against the actual assembly. Do not substitute pin connections or component values without checking the circuit and device datasheet.

## 8. Wiring and Assembly

The physical build documentation is maintained separately:

- [Hardware Build Guide](hardware/build-guide.md) — components, assembly steps, and validation.
- [Reference Wiring](hardware/reference-wiring.md) — wiring diagram, GPIO assignments, and connector notes.
- [Enclosure Design](enclosure.md) — mechanical integration and enclosure details.

The Raspberry Pi audio interface and the external SmartSpeaker Bus adapter serve separate purposes. The existing Bose subwoofer and its internal electronics are not part of the modification.

## 9. Hardware Validation

The following checks are relevant when reproducing or changing the assembly:

- Confirm the Raspberry Pi UART device and GPIO mapping.
- Verify the Digi One audio output independently.
- Check the interface wiring against the reference diagram.
- Verify supply, ground, and signal connections against the circuit documentation.
- Confirm that the passive monitor remains receive-only and electrically compatible with the monitored signal.
- Test audio playback and SmartSpeaker Bus communication separately before performing an end-to-end test.

## 10. Current Status

The Raspberry Pi platform, INNO-MAKER Digi One audio path, active UART configuration, and separate GPIO16 passive-monitor approach are established parts of the project.

Audible playback through the PS28 has been demonstrated. SmartSpeaker Bus command interpretation and response attribution remain documented separately in the [SmartSpeaker Bus investigation](smartspeaker-bus.md) and the dated [PS28 findings report](../findings/2026-10-11-ps28-findings.md).

The detailed build guide and reference wiring document are the primary references for reproducing the physical adapter. Keep them synchronized with any hardware changes.
