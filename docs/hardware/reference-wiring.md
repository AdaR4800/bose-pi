# Reference Wiring and Connector Notes

This document accompanies the [Hardware Build Guide](build-guide.md) and the project's reference wiring diagram.

![Bose-Pi reference wiring diagram](../../images/bose-pi-reference-wiring.jpg)

## Wiring Principles

- The standard network cable between the adapter and the PS28 carries project-specific signals. It is **not an Ethernet link** and must not be connected to a network switch.
- GPIO14 is UART0 TX, GPIO15 is UART0 RX, and GPIO16 is the separate passive sniffer input.
- The SN74HC07N provides the open-collector transmit stage for SmartSpeaker DATA.
- The original RCA connector on the INNO-MAKER Digi One has been removed. Two wires from the S/PDIF output connect through removable jumpers on the interface HAT.
- The reference drawing routes the S/PDIF pair to positions 7 and 8.
- TAP is excluded. TAP-related contacts remain unconnected.

## SN74HC07N Key Pins

| Pin | Signal |
|---:|---|
| 1 | Input from GPIO14 / UART TX |
| 2 | Open-collector output to SmartSpeaker DATA |
| 7 | GND |
| 14 | 3.3 V supply |

The unused gate inputs are tied to GND; their outputs are left unconnected. Fit a 100 nF decoupling capacitor directly across pins 14 and 7. The reference drawing also includes 100 µF supply buffering.

The documented circuit uses a 3.3 V pull-up. Preserve the pull-up and receiver-path components as shown in the reference drawing. Do not infer additional connections from this pin summary alone.

## Connector Orientation

The wiring diagram is the reference for the project's current physical wiring. When documenting or rebuilding the cable, include a clear view of the actual connector orientation and verify continuity with a multimeter.

Do not rely on cable colours or generic Ethernet pinout diagrams. Contact numbering depends on the viewing orientation of the connector.

## INNO-MAKER Digi One Modification

![INNO-MAKER Digi One modification](../../images/inno-maker-digi-one-audio-mod.jpg)

The photograph shows the two S/PDIF wires soldered to the INNO-MAKER Digi One in place of the original RCA connector. The wires connect through removable jumper connections to the interface board containing the SN74HC07N and the RJ45 breakout connection.

Preserve the verified signal-pair mapping from the actual board and reference wiring. Do not arbitrarily connect either S/PDIF signal wire to ground.

## Verification Before Connecting the PS28

- Confirm continuity from the adapter to the corresponding PS28 connector contacts.
- Verify the S/PDIF pair mapping against the reference diagram.
- Check the SN74HC07N supply, ground, and signal connections.
- Confirm that the passive sniffer remains a separate receive-only path.
- Confirm that TAP-related contacts remain unconnected.
- Ensure the cable is not connected to Ethernet networking equipment.

The reference diagram and the actual known-good assembly take precedence over assumptions based on generic connector conventions.
