# Software State Machine

## 1. Purpose

The Bose-Pi software combines network audio playback, UART communication, and a custom interface to the Bose SmartSpeaker Bus.

The state machine is intended to coordinate these components without confusing audio-service availability, UART readiness, and successful communication with the Bose hardware.

This document describes the current control design and distinguishes established component behaviour from transitions that still require validation.

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

The intended control logic must keep the following responsibilities separate:

1. Application initialization and configuration.
2. Hardware-interface readiness.
3. UART initialization and communication handling.
4. SmartSpeaker Bus protocol processing.
5. Audio-service readiness.
6. Error reporting and recovery.

The final implementation should make transitions explicit and provide useful diagnostic information when a component is unavailable.

## 4. Proposed Operational States

The following states are a design model. They are not a claim that every state already exists in the software.

| State | Intended responsibility |
|---|---|
| `INITIALIZING` | Load configuration and initialize application components. |
| `WAITING_FOR_HARDWARE` | Wait for required hardware conditions. |
| `INTERFACE_READY` | Prepare the UART and electrical interface. |
| `BUS_MONITORING` | Observe bus traffic where passive monitoring is enabled. |
| `BUS_COMMUNICATION` | Perform protocol operations supported by the implementation. |
| `AUDIO_READY` | Indicate that the configured audio service is available. |
| `ERROR` | Record an error that prevents the affected operation from continuing normally. |

The final state names and transitions must be reconciled with the actual source code and verified hardware behaviour.

## 5. Hardware Detection

A GPIO input has been considered for detecting the presence of the Bose connection.

Its electrical polarity, active level, pull-up or pull-down arrangement, and precise meaning must be established from the actual circuit.

Detecting the electrical presence of a connection must not be treated as proof that the Bose protocol is working.

## 6. UART and Bus Handling

The bus investigation uses `/dev/ttyAMA0` at 4800 baud, 8N1.

The passive sniffer is designed to observe traffic without actively transmitting commands.

Protocol communication must be kept separate from passive monitoring. Transmitting a command, receiving bytes, and interpreting a valid protocol response are distinct events.

The final state machine must not report successful Bose communication merely because the UART opened successfully or bytes were received.

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

The complete Bose SmartSpeaker Bus protocol, the required initialization sequence, the final hardware-detection behaviour, and the complete state-machine transitions remain to be validated.

The state machine should be considered complete only when its implementation and its documented transitions agree with repeatable test results.
