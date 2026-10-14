# Operating Mode

## 1. Normal Operation

Bose-Pi replaces the failed Bose AV28 central console with a Raspberry Pi 5 while retaining the Bose PS28 powered bass module and the existing satellite speakers.

During normal operation:

1. Keep the Raspberry Pi powered and connected to the home network.
2. Select **Bose Pi** as the AirPlay receiver on an iPhone or Mac.
3. Start music playback.
4. The controller sends the playback setup commands to the Bose SmartSpeaker Bus.
5. When playback stops, the controller executes the delayed MUTE and POWER_OFF sequence.
6. Shairport Sync remains running and available for the next AirPlay session.

The `bose-control.service` systemd service starts automatically at boot.

## 2. AirPlay START

When the controller receives a START event, it cancels any pending STOP sequence and sends the playback setup commands in the following order.

| Order | Command | Frame | Function |
|---:|---|---|---|
| 1 | ANTI_MUTE | `01 00 01 00` | Restores the audible state in the tested setup |
| 2 | FIVE_CHANNEL | `05 00 05 00` | Selects the tested five-channel playback mode |

The command sequence has been tested on the actual Bose Lifestyle 28 installation. Music playback is restored, with sound heard from all five satellite speakers in the tested configuration.

## 3. AirPlay STOP

When the controller receives a STOP event, it starts the delayed shutdown sequence.

The timer is measured from the original STOP event. POWER_OFF is sent ten seconds after STOP, not ten seconds after MUTE.

| Time from STOP | Controller action | Frame |
|---:|---|---|
| 0 seconds | Enter `STOP_PENDING` | — |
| 5 seconds | Send MUTE | `02 00 78 7A` |
| 10 seconds total | Send POWER_OFF | `01 00 80 81` |

The MUTE command silences the Bose output. The POWER_OFF command stops Bose audio output while AirPlay remains available.

The complete sequence has been verified on the actual hardware.

## 4. Cancellation on a New START

A new START event during the STOP sequence cancels the pending shutdown actions.

The controller clears the pending STOP timing state and resets the relevant timer flags. It then executes the START sequence:

1. Cancel the pending STOP sequence.
2. Send ANTI_MUTE.
3. Send FIVE_CHANNEL.
4. Return to active playback.

This prevents an outdated STOP timer from muting or powering off the Bose system during a new playback session.

## 5. Controller States

The relevant playback states are:

| State | Description |
|---|---|
| `BOSE_UNAVAILABLE` | The Bose system is not available according to the controller's availability checks. |
| `AVAILABLE_IDLE` | The Bose system is available and no playback session is active. |
| `AIRPLAY_ACTIVE` | An AirPlay playback session is active. |
| `STOP_PENDING` | Playback has stopped and the delayed shutdown sequence is running. |
| `MUTED_IDLE` | The MUTE stage has completed; POWER_OFF is still pending. |
| `BOSE_OFF` | The POWER_OFF stage has completed. |
| `BUS_ERROR` | A bus communication error has been detected by the relevant error-handling path. |

The controller's state machine is documented in [State Machine](state-machine.md).

## 6. Logging and Diagnostics

Follow the controller log in real time:

```bash
sudo journalctl -u bose-control.service -f
```

A typical STOP sequence produces messages similar to:

```text
AirPlay event: STOP; state: STOP_PENDING
Timer: MUTE due after 5.0 s
Bose Bus: sending MUTE: 02 00 78 7A
Bose Bus: MUTE transmitted
Timer: POWER_OFF due after 10.0 s
Bose Bus: sending POWER_OFF: 01 00 80 81
Bose Bus: POWER_OFF transmitted
```

The exact log wording depends on the installed software version.

Stop the live log display with `Ctrl+C`. This terminates the log display only; it does not stop the controller service.

Check whether the controller service is running:

```bash
systemctl is-active bose-control.service
```

Check recent log entries:

```bash
sudo journalctl -u bose-control.service -n 50 --no-pager
```

## 7. Operating Constraints

- Use normal SmartSpeaker mode only.
- TAP mode is excluded.
- Do not connect TAP-related contacts.
- Do not connect a Raspberry Pi push-pull GPIO directly to the shared SmartSpeaker DATA line.
- Keep the controller and passive sniffer from claiming the same GPIO line simultaneously.
- Keep the Raspberry Pi powered while using AirPlay.
- Do not stop `bose-control.service` as part of normal playback operation.

## 8. Related Documentation

- [System Architecture](architecture.md)
- [Hardware](hardware.md)
- [Hardware Build Guide](hardware/build-guide.md)
- [SmartSpeaker Bus](smartspeaker-bus.md)
- [Control Software](control-software.md)
- [State Machine](state-machine.md)
