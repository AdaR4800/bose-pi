# Control Software and Services

## Runtime components

| Component | Purpose |
|---|---|
| `shairport-sync.service` | AirPlay receiver and audio playback |
| `bose-control.service` | Reads AirPlay events and controls the PS28 |
| `bose_bus.py` | Central UART transport and bus-availability check |
| `bose_control.py` | Event processing, timers, command scheduling, GPIO state |
| `bose-playback-start` | Creates an AirPlay START event |
| `bose-playback-stop` | Creates an AirPlay STOP event |

The installed files are under `/home/robert/bose-control/`. The event queue is `/home/robert/bose-control/events/queue`. The controller log is `/home/robert/bose-control/logs/bose-control.log`, and messages are also available through the systemd journal.

## systemd unit

The working service definition is:

```ini
[Unit]
Description=Bose PS28 Controller
After=local-fs.target
Wants=local-fs.target

[Service]
Type=simple
User=robert
WorkingDirectory=/home/robert/bose-control
ExecStart=/usr/bin/python3 /home/robert/bose-control/bose_control.py
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

The service has been enabled and tested after reboot. The authoritative installed copy is `/etc/systemd/system/bose-control.service`.

## Service checks

Check both services:

```bash
systemctl is-active bose-control.service
systemctl is-active shairport-sync.service
```

Expected output for each: `active`.

Inspect controller logs:

```bash
sudo journalctl -u bose-control.service -n 50 --no-pager
```

Follow logs live:

```bash
sudo journalctl -u bose-control.service -f
```

Restart only the controller:

```bash
sudo systemctl restart bose-control.service
```

The controller does not manage the Shairport Sync service. AirPlay remains advertised while the PS28 is muted or has received the POWER_OFF command.

## AirPlay event flow

The Shairport Sync hooks write event files to the controller queue. The controller processes them in filename order and removes them after processing. The START and STOP hooks are independent of the UART transport.

On START, the controller clears the STOP timestamp and timer flags, clears stale pending commands, and queues ANTI_MUTE followed by FIVE_CHANNEL.

On STOP, the controller clears pending START commands and records a monotonic timestamp. MUTE is due 5 seconds after STOP; POWER_OFF is due 10 seconds after STOP in total.

## Operational caution

A log entry saying `... übertragen` means the frame was handed to the serial transport successfully according to the current software's write checks. It is not, by itself, a protocol-level acknowledgement from the PS28. The completed installation has additionally been tested by listening and by confirming that AirPlay remains available after the STOP sequence.
