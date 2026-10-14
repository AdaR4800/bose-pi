# Reference Wiring and Connector Notes

This document describes the reference wiring for the Bose-Pi hardware interface used with a Bose Lifestyle 28 system consisting of the original AV28 console design and PS28 powered bass module.

The wiring diagram is the primary reference for the documented physical assembly. Use it together with the [Hardware Build Guide](build-guide.md).

## 1. Reference Wiring Diagram

![Bose-Pi reference wiring diagram](../images/bose-pi-reference-wiring.jpg)

The diagram shows the Raspberry Pi connections, SN74HC07N interface, INNO-MAKER Digi One S/PDIF output, and cable connection to the Bose PS28.

The interface has three distinct signal functions:

- UART transmission from GPIO14 through the SN74HC07N to the SmartSpeaker DATA line.
- UART reception through the documented receiver path.
- Passive observation through GPIO16.

The S/PDIF output pair is connected separately to the designated contacts on the PS28 connector.

## 2. Raspberry Pi Connections

| Raspberry Pi signal | Physical pin | Function |
|---|---:|---|
| GPIO14 / UART0 TX | 8 | Serial transmission |
| GPIO15 / UART0 RX | 10 | Serial reception |
| GPIO16 | 36 | Passive bus monitoring |
| 3.3 V | 1 or 17 | SN74HC07N supply |
| GND | As shown in the diagram | Common signal reference |

The documented UART configuration is `/dev/ttyAMA0`, 4800 baud, 8 data bits, no parity, and 1 stop bit (8N1).

The physical pin assignments and electrical connections must match the reference drawing.

## 3. SN74HC07N Connections

The SN74HC07N is used as an open-collector buffer for transmission to the shared SmartSpeaker DATA line.

| IC pin | Connection |
|---:|---|
| 1 | GPIO14 / UART0 TX |
| 2 | SmartSpeaker DATA |
| 7 | GND |
| 14 | 3.3 V supply |

The reference circuit also includes:

- A 100 nF decoupling capacitor across the IC supply pins.
- 100 µF supply buffering.
- The documented bus pull-up arrangement.
- The documented receiver path and 1 kΩ resistor.

Unused gate inputs are tied to GND, and their outputs are left unconnected.

Do not infer the complete circuit from this table. The reference drawing defines the intended physical wiring.

## 4. INNO-MAKER Digi One S/PDIF Connection

The original RCA connector on the INNO-MAKER Digi One was removed. Two wires from the S/PDIF output are connected to removable jumpers on the interface board.

![INNO-MAKER Digi One audio modification](../images/inno-maker-digi-one-audio-mod.jpg)

The two wires carry the S/PDIF signal pair. Preserve their verified mapping to the PS28 connector contacts as shown in the reference diagram.

Do not arbitrarily connect either S/PDIF signal to ground.

## 5. Cable and PS28 Connector

The adapter connects to the PS28 using a standard network cable and an 8-pin RJ45 breakout.

**The cable is not used for Ethernet networking.** It carries project-specific audio and SmartSpeaker Bus signals.

The reference drawing identifies the S/PDIF pair at connector positions 7 and 8. The SmartSpeaker Bus connection and signal reference are shown separately.

Connector numbering depends on viewing orientation. Before connecting the cable to the PS28:

1. Identify the connector orientation used in the drawing.
2. Check continuity between the adapter and the corresponding cable contacts.
3. Confirm that the signal pair and bus connections match the drawing.
4. Verify that no unintended short exists between signal, ground, and supply connections.

Do not rely on cable colours or a generic Ethernet pinout.

## 6. Operating Constraint

The project uses normal SmartSpeaker operating mode only.

TAP mode is excluded. TAP-related contacts remain unconnected, and no TAP mode-entry commands are used.

## 7. Related Documentation

- [Hardware Overview](../hardware.md)
- [Hardware Build Guide](build-guide.md)
- [System Architecture](../architecture.md)
- [SmartSpeaker Bus](../smartspeaker-bus.md)
