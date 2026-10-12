# Software State Machine

## 1. Purpose

The Bose-Pi software needs a predictable way to manage the relationship between the Raspberry Pi, the SmartSpeaker Bus interface, and the audio service.

An explicit state machine is intended to make startup, hardware detection, communication handling, and error recovery easier to understand and test.

This document describes the proposed control model. It does not claim that all states and transitions have already been implemented.

## 2. Design Goals

The state machine should:

- Keep hardware detection separate from audio-service management.
- Avoid transmitting protocol messages before the communication interface is ready.
- Handle the absence of the Bose system without uncontrolled retries.
- Make errors and recovery paths explicit.
- Provide enough diagnostic information to understand why a transition occurred.

## 3. Proposed States

The following states provide an initial conceptual model. Their exact names and transition conditions may change as the implementation develops.

| State | Purpose |
|---|---|
| `INITIALIZING` | Initialize software components and configuration. |
| `WAITING_FOR_HARDWARE` | Wait for the required hardware conditions to be satisfied. |
| `INTERFACE_READY` | Prepare the UART and electrical interface for communication. |
| `COMMUNICATING` | Perform the bus operations supported by the current implementation. |
| `AUDIO_READY` | Indicate that the audio service is available according to the implemented readiness checks. |
| `ERROR` | Record a failure that prevents normal operation. |

These states are a starting point for the design, not a claim that every state has already been implemented or experimentally validated.

## 4. Hardware Detection

The software architecture considers a GPIO input as a possible means of detecting whether the Bose connection is present.

The electrical polarity, active level, pull-up or pull-down arrangement, and precise meaning of this signal must be defined from the actual circuit and validated on the hardware.

Hardware presence must not automatically be treated as proof that the SmartSpeaker Bus protocol is working.

## 5. UART and Bus Communication

Before bus communication is enabled, the software should initialize the selected UART and its configuration.

The UART loopback test established that the tested transmit and receive path could exchange bytes successfully after correcting the test wiring.

Loopback success does not establish that the Bose protocol is operational. Communication with the Bose hardware requires separate validation.

The bus handler should eventually distinguish between:

- Successful transmission.
- Received data.
- Protocol-level responses, where applicable.
- Communication timeouts.
- Unexpected or invalid data.

The actual message formats and response requirements must be derived from verified protocol observations.

## 6. Audio Service Management

The intended system uses an AirPlay-compatible audio service on the Raspberry Pi.

The state machine should manage audio-service readiness separately from bus communication. A running service does not necessarily mean that the Bose system is ready, and a detected Bose connection does not necessarily mean that audio streaming is available.

The exact startup sequence and dependencies remain to be defined and tested.

## 7. Error Handling and Recovery

Potential error conditions include:

- UART initialization failure.
- Missing or unavailable hardware.
- Communication timeout.
- Unexpected protocol data.
- Audio-service startup failure.

The implementation should record useful diagnostic information and avoid uncontrolled retry loops.

Recovery behaviour should be added only after the expected hardware and protocol behaviour is sufficiently understood.

## 8. Testing Strategy

The state machine should be tested incrementally.

1. Verify software initialization without the Bose system connected.
2. Verify hardware detection against the actual electrical interface.
3. Verify UART initialization and loopback independently.
4. Test communication with the Bose hardware.
5. Validate state transitions using repeatable observations.
6. Test audio-service startup and failure handling.
7. Test the complete system from startup to audio playback.

Each test should distinguish between what was directly observed and what was inferred.

## 9. Current Status

This document defines an initial design model. The final state definitions, GPIO behaviour, transition rules, and audio-service dependencies must be reconciled with the actual implementation before being described as complete.
