# Bose SmartSpeaker Bus

## 1. Overview

Bose-Pi communicates with the SmartSpeaker Bus of the Bose Lifestyle 28 PS28 powered bass module through a custom Raspberry Pi interface.

The interface uses UART0 and an SN74HC07N open-collector buffer for transmission. A separate GPIO input is used for passive bus monitoring.

The project uses normal SmartSpeaker operating mode only. TAP mode is excluded.

## 2. Serial Configuration

The tested serial configuration is:

| Parameter | Value |
|---|---|
| Linux device | `/dev/ttyAMA0` |
| Transmit | GPIO14, physical pin 8 |
| Receive | GPIO15, physical pin 10 |
| Baud rate | 4800 |
| Data bits | 8 |
| Parity | None |
| Stop bits | 1 |
| Format | 8N1 |

The passive sniffer uses GPIO16, physical pin 36, to observe bus activity.

The active UART and passive sniffer are separate functions. The sniffer is a diagnostic tool and must not be treated as the source of transmitted commands.

## 3. Electrical Interface

The transmit path uses an SN74HC07N open-collector buffer. Its output pulls the shared DATA line LOW; it does not actively drive the line HIGH.

The documented circuit includes a bus pull-up and a separate receiver path. The complete electrical connections are defined in the [Reference Wiring](hardware/reference-wiring.md).

Do not connect a Raspberry Pi push-pull GPIO directly to the shared DATA line.

## 4. Observed Traffic

The following byte sequences were observed or tested on the project hardware. The byte sequences are recorded as hexadecimal values, in transmission order.

| Bytes | Description |
|---|---|
| `55 00 FF A5 0B` | Captured traffic observed during bus monitoring |
| `0B 00 00 0B` | Tested query; response observed: `00 0C 00 F0 FC` |
| `0B 00 05 0E` | Tested query; response observed: `00 0C 00 10 1C` |
| `07 00 10 17` | Tested command |
| `01 00 01 00` | Tested command |
| `05 00 05 00` | Tested command |
| `01 00 80 81` | Tested command that stops Bose audio output while AirPlay remains available |

The table records measured or tested behaviour. It is not a complete protocol specification.

The meaning of an individual byte or field must not be inferred from the sequence alone. In particular, a captured response should not be attributed to a particular device unless its origin has been established by the test setup.

## 5. Queries and Responses

The two documented query/response pairs are:

```text
Query:    0B 00 00 0B
Response: 00 0C 00 F0 FC
```

```text
Query:    0B 00 05 0E
Response: 00 0C 00 10 1C
```

These pairs are useful reference observations for validating the electrical interface and serial capture.

They do not, by themselves, establish the complete meaning of the command fields, response fields, or checksum rules.

## 6. Tested Audio Behaviour

The following command has been tested on the actual installation:

```text
01 00 80 81
```

The observed result is that Bose audio output stops while AirPlay remains available.

The following command sequences have also been tested in the project setup:

```text
07 00 10 17
01 00 01 00
05 00 05 00
```

Their interpretation and use must follow the validated project implementation. This document does not assign additional protocol semantics beyond the recorded tests.

## 7. Passive Sniffer

The passive sniffer is located at:

`scripts/ps28_sniffer.py`

It uses GPIO16 and groups captured signal activity into bursts for inspection. The configured serial timing assumption is 4800 baud, 8N1.

The sniffer's idle-gap parameter is a software setting used for burst grouping. It is not proof of a protocol-defined frame boundary.

The sniffer is passive and is not the active UART controller.

Do not run it concurrently with another process that claims GPIO16 exclusively.

## 8. Operating Constraints

- Use normal SmartSpeaker mode only.
- Do not enter TAP mode.
- Do not connect TAP-related contacts.
- Do not connect a Raspberry Pi push-pull GPIO directly to the shared DATA line.
- Use the documented electrical interface.
- Distinguish observed bytes from interpreted protocol meanings.
- Do not assume that a response originated from the PS28 without sufficient evidence.

## 9. Related Documentation

- [System Architecture](architecture.md)
- [Hardware](hardware.md)
- [Reference Wiring](hardware/reference-wiring.md)
- [Control Software](control-software.md)
- [Operating Mode](operating-mode.md)
- [State Machine](state-machine.md)
