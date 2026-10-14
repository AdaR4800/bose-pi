# Control Software

## 1. Overview

Bose-Pi uses separate software components for AirPlay playback, SmartSpeaker Bus communication, playback control, and passive bus monitoring.

The controller processes AirPlay START/STOP events and implements the complete playback control sequence.

On START, the controller sends ANTI_MUTE followed by FIVE_CHANNEL. On STOP, it schedules MUTE after five seconds and POWER_OFF after ten seconds in total. A new START cancels the pending STOP sequence.

The complete control sequence, including automatic MUTE and POWER_OFF, has been verified on the actual Bose Lifestyle 28 system.

## 2. Runtime Components


| Component | Responsibility |
|---|---|
| `shairport-sync.service` | AirPlay receiver and digital audio playback |
| `bose-control.service` | Runs the Bose controller as a systemd service |
| `controller/bose_control.py` | Processes playback events, monitors GPIO16, manages states and timers, and coordinates control actions |
| `controller/bose_bus.py` | UART interface for SmartSpeaker Bus availability checks and command transmission |
| `Shairport Sync hook scripts (installed on the Raspberry Pi)` | Generate playback START/STOP events; the hook scripts are not included in this repository |
| `scripts/ps28_sniffer.py` | Passive SmartSpeaker Bus sniffer |
| `controller/tests/bus_availability_test.py` | Standalone diagnostic for bus availability and audio input status |
| `controller/tests/bus_input_status_test.py` | Standalone diagnostic for audio input status |
| `controller/tests/bus_status_test.py` | Standalone diagnostic for bus status |


The controller and the passive sniffer have different responsibilities. The controller performs active bus communication; the sniffer observes bus traffic for diagnostic purposes.

## 3. Hardware and Software Configuration

The documented development environment is Debian GNU/Linux 13 (trixie), running on a Raspberry Pi 5 Model B.

The active UART configuration is:

| Parameter | Value |
|---|---|
| Device | `/dev/ttyAMA0` |
| TX | GPIO14, physical pin 8 |
| RX | GPIO15, physical pin 10 |
| Baud rate | 4800 |
| Data bits | 8 |
| Parity | None |
| Stop bits | 1 |
| Framing | 8N1 |

The GPIO interface uses Python `gpiod`. GPIO16, physical pin 36, is used for the documented bus-related input.

The controller and the standalone passive sniffer must not simultaneously claim the same GPIO line exclusively.

## 4. SmartSpeaker Bus Availability

The controller checks SmartSpeaker Bus availability at startup through
`BoseBus.check_availability()` in `controller/bose_bus.py`.

Request:

```text
0B 00 00 0B
```

The availability check validates the received response against the expected
request echo, response prefix, and XOR checksum.

In the tested setup, a valid response is received when the PS28 is switched
on. When the PS28 is switched off, no valid response is detected.

This is a startup availability check, not periodic polling.

The standalone diagnostic scripts in `controller/tests/` can be used for
manual troubleshooting. They must not be run while the controller service
is active because both use `/dev/ttyAMA0`.


## 5. Playback Control and State Machine

The controller responds to AirPlay START and STOP events.

### START sequence

When a new playback session starts:

1. Any pending STOP sequence is cancelled.
2. The controller sends the ANTI_MUTE command.
3. The controller sends the FIVE_CHANNEL command.
4. The controller updates its playback state and records the event.

The tested command frames are:

```text
01 00 01 00
05 00 05 00
```

### STOP sequence

When playback stops:

1. The controller enters the pending-stop sequence.
2. After five seconds, it sends MUTE.
3. After ten seconds in total, it sends POWER_OFF.
4. The controller updates its state and records the events.

The tested command frames are:

```text
02 00 78 7A
01 00 80 81
```

### Restart during the STOP sequence

If a new START event arrives before the pending STOP sequence finishes, the pending timers are cancelled. The controller then executes the START sequence.

This prevents delayed MUTE or POWER_OFF commands from interrupting a new playback session.

The timer intervals are measured from the STOP event: MUTE at five seconds and POWER_OFF at ten seconds in total.

## 6. Controller States

The controller's state machine represents the availability of the Bose system and the playback control sequence.

| State | Meaning |
|---|---|
| `BOSE_UNAVAILABLE` | The Bose system is unavailable according to the controller's availability and input checks. |
| `AVAILABLE_IDLE` | The Bose system is available and no playback session is active. |
| `AIRPLAY_ACTIVE` | An AirPlay playback session is active. |
| `STOP_PENDING` | Playback has stopped and the delayed shutdown sequence is pending. |
| `MUTED_IDLE` | The MUTE stage has completed and the controller is waiting for the final shutdown stage. |
| `BOSE_OFF` | The POWER_OFF stage has completed. |
| `BUS_ERROR` | A bus communication error has been detected by the relevant error-handling path. |

A new START during `STOP_PENDING` cancels the pending shutdown sequence and returns the controller to active playback.

The state machine and its transitions are described in [State Machine](state-machine.md).

## 7. Controller Service

The systemd unit is:

`/etc/systemd/system/bose-control.service`

The documented installation runs the controller as user `robert` from `/home/robert/bose-control/`.

Check the service status:

```bash
systemctl is-active bose-control.service
```

Inspect recent logs:

```bash
sudo journalctl -u bose-control.service -n 50 --no-pager
```

Follow logs live:

```bash
sudo journalctl -u bose-control.service -f
```

Restart the controller:

```bash
sudo systemctl restart bose-control.service
```

A running service confirms that the process is active. It does not, by itself, prove that audio is audible or that the PS28 is responding correctly.

## 8. AirPlay Playback

Shairport Sync receives AirPlay audio and passes it to ALSA for output through the INNO-MAKER Digi One HAT.

The documented configuration includes:

- Binary: `/usr/local/bin/shairport-sync`
- Configuration: `/etc/shairport-sync.conf`
- Service: `shairport-sync.service`
- AirPlay name: `Bose Pi`
- ALSA output: `iec958:sndallodigione`
- Output rate: 48 kHz
- Output format: `S16_LE`
- Volume control: `ignore_volume_control = "no"`

The START and STOP hooks pass playback-session events to the controller.

A hook event represents a session-selection event. It is not necessarily proof that sound is currently audible.

The AirPlay audio path has been tested successfully through the INNO-MAKER Digi One and the Bose PS28.

## 9. Passive Sniffer

The passive SmartSpeaker Bus sniffer is maintained separately from the active controller.

The project sniffer uses GPIO16 to capture bus activity and group signal transitions into bursts for inspection. Its serial timing assumption is 4800 baud, 8N1.

The idle-gap setting is a software parameter for grouping captured activity. It is not proof of a protocol-defined frame boundary.

The sniffer is intended for observation and troubleshooting. It must not be run concurrently with another process that exclusively claims GPIO16.

## 10. Tested Manual Commands

The following commands have been tested on the actual PS28 installation:

| Frame | Observed behaviour |
|---|---|
| `07 00 10 17` | Selects the tested S/PDIF input |
| `01 00 01 00` | ANTI_MUTE; restores the tested playback path |
| `05 00 05 00` | FIVE_CHANNEL; tested with audible output from the speakers |
| `02 00 78 7A` | MUTE |
| `01 00 80 81` | POWER_OFF; stops Bose audio output while AirPlay remains available |

These frames are also used by the automatic playback control sequence where applicable.

Observed command behaviour is documented separately from the interpretation of the complete Bose protocol.

## 11. Functional Summary

The documented implementation provides:

- AirPlay playback through the digital audio path.
- Startup checking of SmartSpeaker Bus availability.
- START/STOP event handling.
- ANTI_MUTE followed by FIVE_CHANNEL on START.
- Automatic MUTE five seconds after STOP.
- Automatic POWER_OFF ten seconds after STOP.
- Cancellation of pending STOP timers when a new START occurs.
- Controller and playback event logging.
- Passive SmartSpeaker Bus monitoring as a separate diagnostic function.

The complete playback control sequence, including MUTE and POWER_OFF, has been verified on the actual hardware.

The implementation uses normal SmartSpeaker operating mode only. TAP mode is excluded.

## Related Documentation

- [System Architecture](architecture.md)
- [Hardware](hardware.md)
- [Hardware Build Guide](hardware/build-guide.md)
- [SmartSpeaker Bus](smartspeaker-bus.md)
- [Operating Mode](operating-mode.md)
- [State Machine](state-machine.md)
