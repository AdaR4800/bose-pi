# Bose SmartSpeaker Bus

## Purpose

The SmartSpeaker Bus is the control path between the original Bose system controller and the PS28 powered speaker module. Bose-Pi implements only the small subset needed for this single-system installation; it does not attempt to reproduce the full original multiroom system.

## Physical and serial configuration

| Parameter | Working configuration |
|---|---|
| Raspberry Pi | Raspberry Pi 5 |
| UART device | `/dev/ttyAMA0` |
| TX | GPIO14, physical pin 8 |
| RX | GPIO15, physical pin 10 |
| Baud rate | 4800 |
| Framing | 8N1 |
| Interface | SN74HC07N open-collector buffer |
| PS28 bus pin | J1 pin 1 |
| Ground | PS28 J1 pin 2 |

The bus is a bidirectional single-wire line. The interface must preserve the Bose-side pull-up and must not introduce a 5 V pull-up onto the bus.

## SN74HC07N interface

The documented prototype wiring uses:

- SN74HC07N pin 14 (VCC) to 3.3 V.
- SN74HC07N pin 7 to GND.
- GPIO14 / UART TX to input 1A, pin 1.
- Output 1Y, pin 2, to PS28 J1 pin 1.
- PS28 J1 pin 1 to GPIO15 / UART RX through a 1 kΩ series resistor.
- A 100 nF decoupling capacitor between pins 14 and 7.
- A 100 µF buffer capacitor between VCC (3.3 V) and GND.  
- Unused gate inputs tied to GND; unused outputs left unconnected.

The physical interface and all wiring should be checked against the final project wiring diagram and the SN74HC07N data sheet before changes are made.

## Commands tested in the installation

All frames are four bytes. The last byte is the XOR of the first three bytes.

| Purpose | Frame | Evidence |
|---|---|---|
| Bus availability check | `0B 00 00 0B` | Controller received a valid availability response at startup |
| Restore / anti-mute | `01 00 01 00` | Confirmed by audible playback test |
| Five-channel mode | `05 00 05 00` | User confirmed sound from all five satellite speakers |
| MUTE | `02 00 78 7A` | Transmitted by the active STOP timer in the final test |
| POWER_OFF | `01 00 80 81` | Transmitted by the active STOP timer; audio stopped while AirPlay remained available |

The exact internal PS28 interpretation of every frame is not assumed beyond the behaviour observed in this installation.

## Passive sniffer

The separate sniffer observes GPIO16 and does not transmit. It is a diagnostic tool, not part of the systemd controller service. Do not change the sniffer or Frame Decoder as part of routine operation. Avoid requesting GPIO16 for the sniffer while the controller is running, because the controller also reserves that line.

## References

- Kenneract, [Bose-Reverse-Engineering — SmartSpeakerProtocol.md](https://github.com/Kenneract/Bose-Reverse-Engineering/blob/main/SmartSpeakerProtocol.md)
- Bose, [US8214447B2](https://patents.google.com/patent/US8214447B2/en)

Patent and community material is reference information. Hardware-specific conclusions in this document are based on the observed Bose-Pi installation.
