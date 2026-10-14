# Control Software

## 1. Overview

Bose-Pi uses separate software components for AirPlay playback, SmartSpeaker Bus availability checks, controller state observation, and passive bus monitoring.

The documented controller is currently an **observation-only implementation**. It reads GPIO16, checks SmartSpeaker Bus availability once at startup, and records the resulting state. It does not send Bose control commands, execute playback timers, or perform periodic bus polling.

Successful manual tests of Bose commands are documented separately in [SmartSpeaker Bus](smartspeaker-bus.md). They must not be confused with automatic controller functionality.

## 2. Runtime Components

| Component | Responsibility |
|---|---|
| `shairport-sync.service` | AirPlay receiver and digital audio playback |
| `bose-control.service` | Runs the observation-only controller |
| `bose_control.py` | Reads GPIO16 and maintains the observed controller state |
| `bus_availability.py` | Queries the PS28 status over UART at startup |
| `bose-playback-start` | Shairport Sync hook for playback-session selection events |
| `bose-playback-stop` | Shairport Sync hook for playback-session deselection events |
| `ps28_sniffer_v2.py` | Existing passive SmartSpeaker Bus sniffer, maintained separately |

The hook scripts currently provide event logging. They do not activate Bose control commands through the scheduler.

## 3. Hardware and Software Configuration

The documented development environment is Debian GNU/Linux 13 (trixie), running on a Raspberry Pi 5 Model B.

The active UART configuration is:

| Parameter | Value |
|---|---|
| Device | `/dev/ttyAMA0` |
| TX | GPIO14, physical pin 8 |
| RX | GPIO15, physical pin 10 |
| Baud rate | 4800 |
| Framing | 8N1 |

The controller uses the Python `gpiod` API v2 to read GPIO16 through `/dev/gpiochip4`.

GPIO16 is configured as an input. The controller accepts a changed level only after it has remained stable for 200 ms.

## 4. SmartSpeaker Bus Availability

The module `bus_availability.py` performs a system-status query at controller startup.

Request:

```text
0B 00 00 0B
```

The availability check verifies the echoed request, the expected response prefix, and the XOR checksum of the response. The serial read uses a bounded timeout.

Observed results in the tested setup:

- PS28 switched on: a valid response is detected.
- PS28 switched off: no valid response is detected.

The availability check runs at startup. The current controller does not repeat it periodically.

## 5. Controller State Observation

The controller recognises the following states:

| State | Meaning in the current implementation |
|---|---|
| `BOSE_UNAVAILABLE` | GPIO16 is stably LOW |
| `AVAILABLE_IDLE` | GPIO16 is stably HIGH and the startup availability check succeeded |
| `AIRPLAY_ACTIVE` | Defined state; not entered by the current observation-only implementation |
| `STOP_PENDING` | Defined state; no STOP timer is executed |
| `MUTED_IDLE` | Defined state; no automatic mute command is sent |
| `BOSE_OFF` | Defined state; no automatic power-off command is sent |
| `BUS_ERROR` | Defined state; not currently used as a controller transition |

A HIGH GPIO16 level alone does not establish bus availability. The current implementation also requires a successful startup availability check before entering `AVAILABLE_IDLE`.

The state names describe the current implementation and its defined extension points. They must not be interpreted as proof that all listed states are reachable or that their associated control behaviour is implemented.

See [State Machine](state-machine.md) for the state and transition documentation.

## 6. Controller Service

The installed systemd unit is:

`/etc/systemd/system/bose-control.service`

The documented service runs the controller as user `robert` from `/home/robert/bose-control/`.

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

The service status confirms whether the process is running. It does not by itself prove that the PS28 is responding or that audio is audible.

## 7. AirPlay Playback

Shairport Sync provides AirPlay playback and sends digital audio through ALSA to the INNO-MAKER Digi One HAT.

The documented configuration includes:

- Binary: `/usr/local/bin/shairport-sync`
- Configuration: `/etc/shairport-sync.conf`
- Service: `shairport-sync.service`
- AirPlay name: `Bose Pi`
- ALSA output: `iec958:sndallodigione`
- Output rate: 48 kHz
- Output format: `S16_LE`
- Volume control: `ignore_volume_control = "no"`

The START and STOP hooks record AirPlay session-selection events. Such an event does not necessarily prove that music is currently audible.

Check the playback service:

```bash
systemctl is-active shairport-sync.service
```

The AirPlay audio path has been tested successfully through the INNO-MAKER Digi One and the Bose PS28.

## 8. Passive Sniffer

The existing passive sniffer is maintained separately from the controller.

The reference files used during development are:

```text
ps28_sniffer_v1_reference.py
ps28_sniffer_v2.py
```

The sniffer observes bus activity through GPIO16. It is not an active controller and does not establish the meaning of captured bytes merely by recording them.

Do not run the sniffer concurrently with another process that exclusively claims GPIO16. Likewise, avoid running multiple programs that access UART0 simultaneously unless the test is specifically designed for that arrangement.

## 9. Manual Command Tests

The following commands have been tested on the actual PS28 installation:

| Frame | Observed behaviour |
|---|---|
| `07 00 10 17` | Selects the tested S/PDIF input |
| `01 00 01 00` | Restores audible output in the tested setup |
| `05 00 05 00` | Audio was reported from all speakers after the command |
| `01 00 80 81` | Stops Bose audio output while AirPlay remains available |

These are manual test results. The current controller does not send these commands automatically.

For the evidence and limitations associated with these tests, see [SmartSpeaker Bus](smartspeaker-bus.md).

## 10. Current Functional Boundary

The current software provides:

- AirPlay playback through the digital audio path.
- A bounded startup query for SmartSpeaker Bus availability.
- GPIO16 level observation with a 200 ms stability interval.
- State logging for `BOSE_UNAVAILABLE` and `AVAILABLE_IDLE`.
- Logging of AirPlay session-selection events.

The current software does **not** provide:

- Automatic Bose mute or power-off commands.
- Automatic START/STOP-driven Bose control.
- Executed five-second or ten-second playback timers.
- Periodic SmartSpeaker Bus polling.
- A fully implemented state machine covering all defined states.

These limitations describe the current implementation, not the capabilities of the hardware interface.

## Related Documentation

- [System Architecture](architecture.md)
- [Hardware](hardware.md)
- [SmartSpeaker Bus](smartspeaker-bus.md)
- [Operating Mode](operating-mode.md)
- [State Machine](state-machine.md)
