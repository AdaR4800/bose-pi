# Software State Machine

## 1. Purpose

The Bose-Pi software combines network audio playback, UART communication, and a custom interface to the Bose SmartSpeaker Bus.

The state machine is intended to coordinate these components without confusing audio-service availability, UART readiness, and successful communication with the Bose hardware.

This document describes the current working control design.

## 2. Verified Components

The following components have been established during development:

- The Raspberry Pi 5 provides the computing platform.
- Shairport Sync 5.5.2 provides the AirPlay-compatible audio service.
- ALSA routes audio to the INNO-MAKER Digi One.
- The Digi One provides the S/PDIF digital audio output.
- The UART configuration used for bus investigation is `/dev/ttyAMA0`, GPIO14 TX and GPIO15 RX.
- The passive sniffer is configured for 4800 baud, 8N1, and can decode complete data bursts.

These results establish individual parts of the system. They do not prove that the complete Bose control protocol or final state machine has been implemented.

## 3. State-Machine Responsibilities

The control logic must keep the following responsibilities separate:

1. Application initialization and configuration.
2. Hardware-interface readiness.
3. UART initialization and communication handling.
4. SmartSpeaker Bus protocol processing.
5. Audio-service readiness.
6. Error reporting and recovery.

The final implementation makes transitions explicit and provide useful diagnostic information when a component is unavailable.

## 4. Operational States

The following states are a design model. They are not a claim that every state already exists in the software.

| State | Intended responsibility / Status |
|---|---|
| `INIT` | Load configuration and initialize application components. |
| `BOSE_OFF` | Shut down PS28 to the point where only bus communication is still active  |
| `MUTE_SENT` | Mute all speakers. |
| `STOP_PENDIMG` | When Pose-Pi is not selected for Airplay by any Apple device |
| `AIRPLAY_ACTIVE` | play music |
| `IDLE` | No AirPlay playback but ready to play. |
| `BUS_ERROR` | Record an error that prevents the affected operation from continuing normally. |

The following figure shows the states graphically, as well as their transitions.



## 5. Hardware Detection

Hardware detection is a separate responsibility from passive bus monitoring.

A GPIO input has been considered for detecting the presence of the Bose connection. Its electrical polarity, active level, pull-up or pull-down arrangement, and precise meaning must be established from the actual circuit and verified through testing.

The passive sniffer on GPIO16 observes bus signal transitions. It does not, by itself, establish whether the Bose hardware is present or operational.

Detecting an electrical connection or observing bus activity must not be treated as proof that the Bose protocol is working.


## 6. UART and Bus Handling

The active UART interface used for bus investigation is `/dev/ttyAMA0` at 4800 baud, 8N1.

The passive sniffer is a separate observation path. It captures bus signal edges through GPIO16 and reconstructs bytes without transmitting commands.

The following events must be treated as distinct:

1. **Transmission:** The Raspberry Pi sends bytes through its UART transmit path.
2. **UART reception:** Bytes are received through the UART receive path. Depending on the electrical interface and bus behaviour, these may include transmitted data echoed back by the bus.
3. **Passive observation:** The GPIO16 sniffer records bus activity independently of the UART.
4. **Protocol response:** A sequence is identified as a response only when supported by repeatable observations and sufficient evidence to distinguish it from an echo or unrelated bus traffic.

Receiving bytes after a transmission does not, by itself, prove that the Bose PS28 generated a response. Likewise, a matching byte sequence does not establish its sender or protocol meaning.

For example, the observation of `01 00 00 01` during transmission and `01 00 00 01 00` in the UART receive data does not establish that the final `00` is a PS28 response.

Further investigation should correlate UART transmit data, UART receive data, and passive sniffer observations, including their timing. Any conclusions about echo behaviour, response timing, or protocol semantics must be based on repeatable measurements.

Protocol communication must remain separate from passive monitoring. The state machine must not report successful Bose communication merely because the UART opened successfully or bytes were received.

## 7. Audio-Service Handling

The configured audio path is:

`AirPlay 2 → Shairport Sync 5.5.2 → ALSA → INNO-MAKER Digi One → S/PDIF`

Audio-service readiness should be managed independently from SmartSpeaker Bus readiness.

A running audio service does not prove that the Bose subwoofer is ready to reproduce audio. Conversely, a detected Bose connection does not prove that the audio service is available.

## 8. Error Handling

Potential error conditions include:

- Configuration or initialization failure.
- UART initialization failure.
- Missing or unavailable hardware.
- Bus communication timeout.
- Unexpected or invalid protocol data.
- Audio-service startup failure.

The implementation should record the affected component and relevant diagnostic information.

Recovery and retry behaviour must be based on the actual protocol requirements and should avoid uncontrolled retry loops.

## 9. Validation Strategy

The control design should be validated in stages:

1. Verify application initialization.
2. Verify the configured audio service independently.
3. Verify UART initialization.
4. Validate passive bus capture.
5. Investigate protocol messages against the real Bose hardware.
6. Validate any required active communication.
7. Confirm state transitions under normal and failure conditions.
8. Test the complete startup and playback sequence.

Each test must distinguish direct observations from interpretations.

## 10. Current Status

The Raspberry Pi audio-output path and the UART sniffer configuration have been established.

The complete Bose SmartSpeaker bus protocol, the required initialization sequence, the final behavior during hardware detection, and the complete state machine transitions could be validated even further. Currently, everything is working without errors and could be investigated further.

The state machine is considered complete for now, since its implementation and transitions match the results of repeatable tests.
