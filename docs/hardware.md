# Hardware

## 1. Overview

Bose-Pi uses a Raspberry Pi 5 to replace the failed AV28 central console of a Bose Lifestyle 28 system.

The original Bose PS28 powered bass module and five satellite speakers remain in use. The Raspberry Pi provides AirPlay audio playback through an INNO-MAKER Digi One HAT and a separate electrical interface to the Bose SmartSpeaker Bus.

The hardware consists of three functional areas:

- Digital audio output.
- Active SmartSpeaker Bus communication.
- GPIO-based monitoring and controller input.

The existing PS28 is not opened or internally modified as part of this project.

## 2. Main Components

| Component | Purpose |
|---|---|
| Raspberry Pi 5 Model B, Revision 1.0 | Main computing platform |
| INNO-MAKER Digi One HAT | S/PDIF digital audio output |
| GeeekPi prototype breakout board | Base for the custom interface circuitry |
| SN74HC07N | Open-collector interface for SmartSpeaker Bus transmission |
| Bose PS28 powered bass module | Original Bose audio system |
| Five Bose satellite speakers | Original speaker installation |

The original Bose AV28 central console was destroyed by an indirect lightning strike and is no longer available.

## 3. Raspberry Pi Platform

The recorded development environment is:

- Operating system: Debian GNU/Linux 13 (trixie).
- Kernel: `6.18.50+rpt-rpi-2712`.
- Python: 3.13.5.
- PySerial: 3.5.
- GPIO access: Python `gpiod`, using the libgpiod 2.x API.

The exact software configuration and installed services are described in the software documentation.

## 4. Digital Audio Interface

The INNO-MAKER Digi One HAT provides the digital audio output to the Bose PS28.

The configured ALSA device is:

`iec958:sndallodigione`

The operational audio path is:

`AirPlay → Shairport Sync → ALSA → INNO-MAKER Digi One → S/PDIF → Bose PS28`

Audible playback through the PS28 has been verified.

The original RCA connector on the Digi One was removed. Two wires connect the S/PDIF output to removable jumper connections on the interface board.

Refer to the [Hardware Build Guide](hardware/build-guide.md) and [Reference Wiring](hardware/reference-wiring.md) for the physical implementation.

## 5. Active UART Interface

The Raspberry Pi communicates with the Bose SmartSpeaker Bus through UART0 and the SN74HC07N interface.

| Parameter | Configuration |
|---|---|
| Linux device | `/dev/ttyAMA0` |
| UART transmit | GPIO14, physical pin 8 |
| UART receive | GPIO15, physical pin 10 |
| Baud rate | 4800 |
| Data bits | 8 |
| Parity | None |
| Stop bits | 1 |
| Format | 8N1 |

The UART device and GPIO mapping are part of the tested hardware configuration. Do not substitute another serial device without checking the Raspberry Pi configuration and the actual wiring.

The SN74HC07N is supplied with 3.3 V in the documented interface circuit. Its open-collector output is used for the SmartSpeaker Bus transmit connection.

The complete electrical implementation, including the receiver path, pull-up, resistors, capacitors, and connector wiring, is defined by the hardware reference drawing.

## 6. Passive Monitoring and GPIO16

GPIO16, physical pin 36, is used for bus-related input and monitoring.

The project includes a passive sniffer in `scripts/ps28_sniffer.py`. It captures signal transitions and groups activity into bursts for inspection.

| Parameter | Configuration |
|---|---|
| GPIO | GPIO16 |
| Physical pin | 36 |
| Capture method | GPIO edge events |
| Baud-rate assumption | 4800 |
| Serial framing | 8N1 |
| Sniffer operation | Passive observation |

The sniffer's 3 ms idle-gap setting is a software parameter for grouping captured activity. It does not by itself establish a protocol-defined message boundary.

**GPIO16 resource constraint:** The active controller and the standalone passive sniffer both use GPIO16. Do not run them simultaneously if both attempt to claim the same GPIO line. The sniffer is a diagnostic tool and is not part of the active controller's systemd service.

Captured traffic must be distinguished from transmitted commands and from responses whose origin has not been independently established.

## 7. SmartSpeaker Bus Electrical Interface

The interface uses an SN74HC07N open-collector buffer to transmit UART data to the SmartSpeaker Bus.

The documented circuit includes:

- A 3.3 V supply for the SN74HC07N.
- A 100 nF decoupling capacitor across the IC supply pins.
- Additional 100 µF supply buffering.
- The documented bus pull-up and series-resistor arrangement.
- A separate UART receive path.
- A separate GPIO16 monitoring connection.

The exact pin assignments and component placement must be taken from the [Reference Wiring](hardware/reference-wiring.md) and [Hardware Build Guide](hardware/build-guide.md).

Do not connect a Raspberry Pi push-pull GPIO directly to the shared SmartSpeaker DATA line. Do not infer the complete circuit from the abbreviated component list in this overview.

## 8. PS28 Connection and Cable

The Raspberry Pi interface connects to the PS28 using a standard network cable.

**This cable is not an Ethernet connection.** It carries the project-specific SmartSpeaker Bus and digital audio signals.

The project wiring reference identifies the relevant PS28 connector contacts, including the SmartSpeaker Bus and the S/PDIF signal pair. TAP-related contacts remain unconnected.

Always verify connector orientation and continuity against the project wiring diagram before connecting the cable to the PS28. Do not rely on cable colours or a generic Ethernet pinout.

## 9. Hardware Validation

The following functions have been established on the project hardware:

- AirPlay audio playback through the INNO-MAKER Digi One and the Bose PS28.
- UART0 operation using `/dev/ttyAMA0` at 4800 baud, 8N1.
- The SN74HC07N open-collector transmit interface.
- Passive SmartSpeaker Bus observation through GPIO16.
- Operation of the custom interface with the normal SmartSpeaker mode.

When reproducing the hardware, check the component placement, power connections, connector orientation, and signal paths against the reference drawing before connecting the interface to the Bose equipment.

Test the audio and control paths independently before performing an end-to-end test.

## 10. Related Documentation

- [System Architecture](architecture.md)
- [Hardware Build Guide](hardware/build-guide.md)
- [Reference Wiring](hardware/reference-wiring.md)
- [SmartSpeaker Bus](smartspeaker-bus.md)
- [Control Software](control-software.md)
- [Operating Mode](operating-mode.md)
