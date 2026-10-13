# Hardware Build Guide

This guide documents the reference Bose-Pi adapter for a Bose Lifestyle 28 system with AV28 console and PS28 bass module. It is intended to let another builder reproduce the external adapter without opening or modifying the Bose bass module.

> **Mandatory design constraint: normal SmartSpeaker mode only. TAP mode is not used.** Do not connect the TAP contacts or send TAP mode-entry commands.

## 1. What the adapter does

The Raspberry Pi provides two separate functions:

1. Receives AirPlay audio and outputs digital audio through the INNO-MAKER Digi One to the PS28 S/PDIF input.
2. Provides the Bose SmartSpeaker Bus control interface through UART and an SN74HC07N open-collector buffer.

The target installation uses a standard network cable between the adapter and the PS28's normal system connector. The cable carries project-defined Bose signals; it is not used for Ethernet networking and must not be connected to a network switch.

The adapter is designed to preserve the original subwoofer electronics and existing speaker wiring.

## 2. Bill of materials

| Item | Qty. | Notes |
|---|---:|---|
| Raspberry Pi 5 | 1 | Main controller and AirPlay receiver |
| INNO-MAKER Digi One | 1 | S/PDIF audio output |
| SN74HC07N, DIP-14 | 1 | Open-collector buffer for SmartSpeaker DATA |
| 100 nF capacitor | 1 | Local supply decoupling at the SN74HC07N |
| 100 µF capacitor | 1 | Additional supply buffering, as shown in the reference diagram |
| 1 kΩ resistor | 1 | Series resistor in the receiver path, as shown in the reference diagram |
| Prototype HAT / perfboard | 1 | Holds the interface circuitry and removable jumpers |
| Jumper wires and connectors | As needed | Removable connections, including the audio pair |
| RJ45 breakout board, 8-pin | 1 | Connector for the cable between Bose-Pi and PS28 |
| Standard network cable | 1 | Multi-conductor cable; not Ethernet networking |
| Suitable Raspberry Pi power supply | 1 | Must support the Pi and attached HATs |

## 3. Reference wiring diagram

Use [Reference Wiring](reference-wiring.md) together with the drawing below. The current drawing is the project reference; the earlier drawing is retained for development history.

![Bose-Pi reference wiring](../images/bose-pi-reference-wiring.jpg)

Always use the latest reference drawing when assembling or modifying the adapter.

## 4. Raspberry Pi signal assignments

| Raspberry Pi signal | Purpose |
|---|---|
| GPIO14 / UART0 TX | Transmit data into the SN74HC07N input |
| GPIO15 / UART0 RX | Receive SmartSpeaker Bus data through the documented receiver path |
| GPIO16 | Separate passive bus sniffer input |
| 3.3 V | SN74HC07N supply |
| GND | Common signal reference |

These assignments reflect the current project configuration. UART0 must be routed to GPIO14/15, and the Linux serial console must not transmit boot or login text on the bus.

Verify the active UART configuration on the actual Raspberry Pi before connecting the Bose equipment.

The GPIO16 passive sniffer is a separate receive-only observation path. It must not be confused with the active UART interface.

## 5. Assemble the SN74HC07N interface

The SN74HC07N is a hex buffer with open-collector outputs. The project uses it so the Raspberry Pi can pull the shared DATA line LOW without actively driving the line HIGH.

| SN74HC07N pin | Connection |
|---|---|
| 14 | Raspberry Pi 3.3 V |
| 7 | GND |
| 1 | GPIO14 / UART TX |
| 2 | SmartSpeaker DATA bus |

Assembly requirements:

- Place the 100 nF decoupling capacitor directly between pins 14 and 7.
- Fit the 100 µF capacitor with the correct polarity if an electrolytic type is used.
- Tie unused gate inputs to GND, as shown in the reference drawing. Leave their outputs unconnected.
- The documented circuit uses a 3.3 V bus pull-up. Do not add another pull-up without a demonstrated electrical reason.
- Do not connect a Raspberry Pi push-pull GPIO directly to the shared SmartSpeaker DATA line.

The known circuit documentation identifies R25 as a 10 kΩ pull-up and R650 as a 510 Ω component in the signal path. Preserve the documented arrangement; do not assume that these components are interchangeable or that their functions can be inferred from resistance values alone.

The GPIO15 receiver path includes the documented 1 kΩ series resistor. The separate GPIO16 passive-sniffer path must follow the reference drawing and the known-good physical build.

**Do not infer missing connections from this abbreviated pin table alone.** Use the reference wiring drawing for the complete circuit.

## 6. Modify the INNO-MAKER Digi One audio output

The reference build removes the Digi One's original RCA connector and solders two wires to the corresponding S/PDIF output points. Those wires are routed to removable jumper connections on the Raspberry Pi interface HAT.


Assembly notes:

1. Identify the two S/PDIF output points on the exact Digi One board revision.
2. Remove the RCA connector without damaging nearby pads or traces.
3. Solder two insulated wires to the same electrical output points used by the original connector.
4. Provide strain relief and insulation so the wires cannot short to the board or move during handling.
5. Route the wires to the HAT's removable jumper connections.
6. Check continuity and the absence of shorts before connecting the audio pair to the Bose cable.

The PS28 input is described in the referenced Bose documentation as a transformer-coupled differential S/PDIF interface. Preserve the intended signal pair and mapping. Do not arbitrarily connect either signal wire to ground.

## 7. Cable and Bose connector

Use a standard network cable between the Bose-Pi adapter and the PS28's normal system connector. In this project it is only a convenient multi-conductor cable; the signals are not Ethernet.

The project reference drawing identifies the following logical connections:

- SmartSpeaker DATA to the open-collector interface and documented receive paths.
- Signal ground/reference as shown in the drawing.
- The two S/PDIF output wires to the designated audio contacts, shown as positions 7 and 8 in the reference diagram.
- TAP-related contacts remain unconnected.

**Use the latest project wiring diagram as the build reference.**

Connector contact numbering depends on viewing orientation. Do not determine pin numbers from cable colours, a generic Ethernet pinout, or a connector viewed from the opposite side. Check continuity end-to-end before connecting the cable to the PS28.

## 8. Serial configuration

The documented SmartSpeaker serial settings are:

| Parameter | Value |
|---|---|
| Baud rate | 4800 |
| Data bits | 8 |
| Parity | None |
| Stop bits | 1 |
| Framing | 8N1 |
| Electrical interface | Shared open-collector DATA bus |
| Documented pull-up | 3.3 V |

UART configuration example:

```python
import serial

ser = serial.Serial(
    port="/dev/ttyAMA0",
    baudrate=4800,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=0,
)
```

The device path must match the verified system configuration. This example configures the UART; it is not a complete implementation of the Bose protocol.

Control software should use the commands and timing behaviour established by project measurements and documented findings.

## 9. Pre-power checks

Before attaching the adapter to the PS28:

- [ ] Confirm SN74HC07N pin 14 is at 3.3 V and pin 7 is GND.
- [ ] Confirm the 100 nF capacitor is fitted close to the IC supply pins.
- [ ] Confirm the 100 µF capacitor polarity, if applicable.
- [ ] Confirm unused SN74HC07N gate inputs are tied to GND.
- [ ] Confirm GPIO14 TX reaches IC pin 1 and IC pin 2 reaches SmartSpeaker DATA.
- [ ] Confirm the documented pull-up and receiver resistor paths match the reference drawing.
- [ ] Confirm GPIO15 receive and GPIO16 passive-sniffer paths match the reference build.
- [ ] Confirm the Digi One audio pair has no short to ground or to the supply rails.
- [ ] Confirm the cable is wired to the project-defined signals, not Ethernet.
- [ ] Confirm TAP contacts are not connected.
- [ ] Confirm no Raspberry Pi GPIO is exposed to an unsafe voltage.
- [ ] Check cable continuity and connector orientation before connecting to the PS28.

## 10. First start and validation

1. Start the Raspberry Pi with the passive sniffer enabled.
2. Observe the bus without transmitting and preserve the capture.
3. Check the observed idle level and serial timing.
4. Enable the established SmartSpeaker control implementation.
5. Test the Digi One S/PDIF audio path separately.
6. Test the complete AirPlay-to-PS28 audio path.
7. Record the software revision, wiring revision, test result, and relevant captured bytes in the project evidence log.

Do not change a known-good sniffer or transmitter merely to imitate another implementation. Preserve working behaviour and change it when repeatable measurements justify the change.

Successful audible playback and the observed control-command sequence are documented in the [PS28 findings report](../findings/2026-10-11-ps28-findings.md).

## 11. Operating mode: no TAP

Bose-Pi uses normal SmartSpeaker mode exclusively. TAP is not part of the build, startup, operation, troubleshooting, or recovery procedure.

Leave the TAP contacts unconnected and do not send TAP mode-entry commands.

## 12. Service documentation references

Record references to the original Bose documents rather than copying full copyrighted service-manual pages into this repository:

- *PS18/28/35 Troubleshooting Guide*, section 2.4, “Serial data interface, SmartSpeaker and TAP”, page 13.
- Schematic SD267086, sheet 1 of 8.
- Earlier comparison schematic SD254175, sheet 1 of 8.

The repository should include the project's own wiring drawing and photographs, with source attribution and a clear separation between manufacturer-documented facts and project measurements.

