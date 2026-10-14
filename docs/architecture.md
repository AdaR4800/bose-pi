# System Architecture

## Overview

Bose-Pi restores a single Bose Lifestyle 28 / PS28 installation without the original AV28 console. A Raspberry Pi 5 provides AirPlay audio and the subset of SmartSpeaker Bus control needed for this installation.

Two independent paths are used: digital audio and system control.

## Audio path

```text
iPhone / Mac
  → AirPlay
  → Shairport Sync 5.5.2
  → ALSA: iec958:sndallodigione
  → INNO-MAKER Digi One
  → S/PDIF / TOSLINK
  → PS28
  → five satellite speakers
```

Shairport Sync stays running when playback stops. The controller does not stop or restart Shairport Sync as part of its normal STOP behaviour. Keeping the AirPlay service running means the receiver remains available after the PS28 receives POWER_OFF.

## Control path

```text
Python controller
  → /dev/ttyAMA0
  → Raspberry Pi UART0 (GPIO14 TX / GPIO15 RX)
  → SN74HC07N open-collector interface
  → PS28 J1 pin 1 SmartSpeaker Bus
```

UART configuration: 4800 baud, 8 data bits, no parity, one stop bit (8N1).

GPIO16 (physical pin 36) is used by the controller as an input with a 200 ms stability window. The separate passive sniffer also uses GPIO16; do not run the sniffer at the same time as the controller if both attempt to request that GPIO line. The passive sniffer source and Frame Decoder are retained as investigation tools and are not part of the active controller's systemd service.

## SmartSpeaker connector

| PS28 J1 pin (RJ45)| Function |
|---:|---|
| 1 | SmartSpeaker Bus |
| 2 | GND |
| 3 | TAP RX, unused |
| 6 | TAP TX, unused |
| 7 | S/PDIF signal |
| 8 | S/PDIF return / GND |

The physical PS28 connection uses a standard network cable. The cable carries the pin assignments above; it is not an Ethernet network connection!

## Controller responsibilities

- Read AirPlay START/STOP event files from `/home/robert/bose-control/events/queue`.
- Check that the PS28 bus is responding at startup.
- Read GPIO16 with a 200 ms stability window.
- On START, cancel pending STOP actions and queue the playback commands.
- On STOP, start the delayed MUTE and POWER_OFF sequence.
- Log state changes and command transmission attempts.
- Run independently of the Shairport Sync process.

## Reliability principles

- Keep audio and control paths separate.
- Keep the passive sniffer receive-only.
- Do not infer command success from the fact that a serial write completed; confirm the result through repeatable listening/operational tests.
- Do not stop Shairport Sync as part of the PS28 power-off sequence.
- Keep the current hardware wiring and the tested command sequences unchanged unless a deliberate new experiment is being documented.
