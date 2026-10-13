# Reference Wiring and Connector Notes

This document accompanies [`build-guide.md`](../hardware/build-guide.md) and the project's wiring image.

![Bose Pi reference wiring diagram](../images/bose-pi-reference-wiring.jpg)

## Wiring principles

- The standard network cable between the adapter and PS28 carries project-specific signals. It is **not an Ethernet link**.
- GPIO14 is UART0 TX; GPIO15 is UART0 RX; GPIO16 is the separate passive sniffer input.
- The SN74HC07N provides the open-collector transmit stage for SmartSpeaker DATA.
- The INNO-MAKER Digi One RCA connector has been removed. Two wires from the S/PDIF output are connected through removable jumpers on the interface HAT.
- The reference drawing routes the S/PDIF pair to positions 7 and 8.
- TAP is excluded. TAP-related contacts remain unconnected.

## SN74HC07N key pins

| Pin | Signal |
|---:|---|
| 1 | Input from GPIO14 / UART TX |
| 2 | Open-collector output to SmartSpeaker DATA |
| 7 | GND |
| 14 | 3.3 V supply |

The unused gate inputs are tied to GND; their outputs are left unconnected. Fit 100 nF directly across pins 14 and 7. The drawing also includes 100 µF supply buffering.

## Connector orientation

The drawing is the authoritative reference for this project's current physical wiring. When documenting or rebuilding the cable, include a clear view of the actual connector orientation and verify continuity with a meter. Do not rely on cable colours or generic Ethernet pinout diagrams.

## Photo: Digi One connector

![INNO-MAKER Digi One modification](../images/inno-maker-digi-one-audio-mod.jpg)

The photo shows the plug-in connection of the two S/PDIF cables (which were soldered onto the INNO-MAKER Digi One in place of the RCA plug) to the plug-in circuit board containing the SN74HC07N and the plug-in interface for the RJ45 jack. Preserve the verified pair mapping from the actual board and reference wiring.
