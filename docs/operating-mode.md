# Operating Mode

## Normal use

1. Keep the Raspberry Pi powered and connected to the home network (by LAN or WLAN).
2. Select the Bose-Pi AirPlay receiver from an iPhone or Mac.
3. Start music. The controller sends the PS28 playback setup commands.
4. Stop playback when finished. Shairport Sync remains running and available for the next AirPlay session.

No manual controller start is required; `bose-control.service` starts at boot.

## State transitions

### AirPlay START

The controller cancels any pending STOP timer and sends these frames in order:

| Name | Frame | Tested purpose |
|---|---|---|
| ANTI_MUTE | `01 00 01 00` | Restore audible state / clear mute |
| FIVE_CHANNEL | `05 00 05 00` | Select the tested five-speaker mode |

As a result of this sequence, the music is played through the Bose system, and the five-channel command causes sound to be heard from all the speakers.

### AirPlay STOP

The controller starts a monotonic timer from the STOP event.

| Time from STOP | Action | Frame |
|---:|---|---|
| 0 s | Enter STOP_PENDING | — |
| 5 s | Send MUTE | `02 00 78 7A` |
| 10 s total | Send POWER_OFF | `01 00 80 81` |

POWER_OFF is sent 10 seconds after STOP, not 10 seconds after MUTE.

The MUTE frame is documented in community reverse-engineering material and is used in the tested installation. POWER_OFF was confirmed to stop audio abruptly while AirPlay continued running. The final integration test confirmed that the entire process worked as intended and that AirPlay remained available.

## Cancellation behaviour

If a new START event arrives during the STOP delay, the controller clears the STOP timestamp and resets both timer flags. It then schedules ANTI_MUTE and FIVE_CHANNEL. This prevents a pending STOP timer from being applied to the new playback session.

## Logging

Live view:

```bash
sudo journalctl -u bose-control.service -f
```

Typical sequence:

```text
AirPlay-Ereignis: STOP; Zustand: STOP_PENDING
Timer: MUTE fällig nach 5.0 s
Bose-Bus: sende MUTE: 02 00 78 7A
Bose-Bus: MUTE übertragen
Timer: POWER_OFF fällig nach 10.0 s
Bose-Bus: sende POWER_OFF: 01 00 80 81
Bose-Bus: POWER_OFF übertragen
```

Stop the log display with `Ctrl+C`; this does not stop the service.
