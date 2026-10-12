# Bose SmartSpeaker Bus

## 1. Purpose

Bose-Pi investigates the control communication between the original Bose Lifestyle receiver and the associated speaker system.

The objective is to understand and implement the functionality required to operate one surviving Bose speaker installation without its original central receiver.

The project does not attempt to reproduce every feature of the original Bose communication architecture.

## 2. Research Sources

The investigation draws on:

- Publicly available Bose service documentation and circuit diagrams.
- Bose patent material describing aspects of the SmartSpeaker Bus hardware and communication architecture.
- Community reverse-engineering work, including Kenneract's Bose-Reverse-Engineering repository.
- Measurements, serial captures, and repeatable experiments performed during Bose-Pi development.

Patent descriptions and findings from other installations provide useful reference material. They are not automatically treated as proof of the behaviour of the hardware investigated here.

## 3. Separate Signal Paths

The receiver-to-subwoofer connection carries two distinct types of signals.

### 3.1 Digital Audio

The audio path uses an S/PDIF-based digital interface.

Bose-Pi generates digital audio using an INNO-MAKER Digi One HAT. The Raspberry Pi audio configuration uses Shairport Sync and ALSA to provide the digital output.

### 3.2 SmartSpeaker Bus

The SmartSpeaker Bus is a separate control communication path.

Bose-Pi investigates this interface independently from the audio path. Correct digital audio output alone does not establish that the required control protocol is working.

## 4. Serial Configuration

The current working configuration for the bus investigation is:

| Parameter | Value |
|---|---|
| Raspberry Pi | Raspberry Pi 5 |
| UART device | `/dev/ttyAMA0` |
| TX | GPIO14, physical pin 8 |
| RX | GPIO15, physical pin 10 |
| Baud rate | 4800 |
| Data bits | 8 |
| Parity | None |
| Stop bits | 1 |
| Framing | 8N1 |

The baud rate reflects the current findings from the Bose-Pi investigation. It is not interchangeable with the baud rates used during unrelated UART experiments.

## 5. Passive Sniffer

The passive sniffer observes the SmartSpeaker Bus independently of the active UART transmit path.

The current implementation uses:

| Parameter | Value |
|---|---|
| Raspberry Pi input | GPIO16 |
| Physical pin | 36 |
| GPIO interface | libgpiod 2.x |
| Baud-rate assumption | 4800 |
| Serial framing | 8N1 |
| Direction | Receive-only / passive |

The sniffer captures GPIO edge events and reconstructs UART bytes from the observed signal transitions. It groups captured edges into bursts and attempts to decode complete UART frames.

The active UART interface remains separate:

- TX: GPIO14, physical pin 8.
- RX: GPIO15, physical pin 10.
- Device: `/dev/ttyAMA0`.

This separation is important when analysing a shared, bidirectional bus. The active UART records serial data received through its RX input, while the passive sniffer independently observes the electrical activity on GPIO16.

Neither capture method alone establishes the sender or protocol meaning of every received byte. In particular, an apparent response must be distinguished from physical echo, delayed traffic, or other bus activity.

The sniffer is an observation tool. It does not transmit commands and does not, by itself, demonstrate successful control of the Bose system.

## 6. Observed Data

The following byte sequence has been used during passive-sniffer validation:

`55 00 FF A5 0B`

This sequence is recorded as captured data. Its protocol meaning has not been established by the capture alone.

A separate observation recorded during development is:

- Transmitted sequence: `01 00 00 01`
- Received sequence: `01 00 00 01 00`

The received data contains the transmitted four-byte sequence followed by an additional byte, `00`.

The available observation does not establish whether the additional byte represents a PS28 response, a consequence of bus timing or capture boundaries, or another aspect of the communication.

### Required Follow-Up

To classify this observation reliably, further experiments should record:

1. The transmitted bytes and their timestamps.
2. The UART receive data and timing.
3. The independent GPIO16 monitor capture.
4. The timing between the end of transmission and subsequent bus activity.
5. Whether the same result occurs in repeatable tests.

Until these observations are correlated, the final `00` must not be classified as a confirmed PS28 response.

Captured bytes, inferred message boundaries, sender classification, and protocol interpretation must remain separate in the project records.

## 7. Patent Descriptions and Real Hardware

The publicly available patent material describes a communication architecture with capabilities beyond the requirements of the Bose-Pi single-system installation.

For example, the patent material discusses master-initiated polling and the reporting of changes made at a speaker back to the central unit.

Bose-Pi focuses on the subset of functionality required by the surviving installation. Features that are unnecessary for this use case are not automatically included in the implementation scope.

Community reverse-engineering work has also reported differences between patent descriptions and observed hardware behaviour, including baud-rate differences.

For this reason, protocol parameters and message semantics must be based on the relevant hardware and repeatable observations.

## 8. Electrical Interface

The Raspberry Pi 5 uses 3.3 V GPIO logic. The SmartSpeaker Bus interface uses an SN74HC07N open-collector buffer to couple the UART transmit signal to the shared bus.

### 8.1 Current Circuit Configuration

The current project design specifies the following connections:

| Component or signal | Connection |
|---|---|
| SN74HC07N pin 14 (VCC) | Raspberry Pi 3.3 V |
| SN74HC07N pin 7 (GND) | Raspberry Pi GND |
| SN74HC07N input | Raspberry Pi UART TX, GPIO14 |
| SN74HC07N open-collector output | Bose PS28 J1 pin 1, SmartSpeaker Bus |
| Bose PS28 J1 pin 1 | 1 kΩ series resistor to Raspberry Pi UART RX, GPIO15 |
| Decoupling capacitor | 100 nF between SN74HC07N VCC and GND |

Unused buffer inputs must be held at defined logic levels (connected to GND). Unused outputs are left unconnected.

### 8.2 Bus Pull-Up

The current analysis of the Bose circuit diagram identifies a 10 kΩ pull-up resistor, R25, connected to the Bose-side 3.3 V supply. A 510 Ω resistor, R650, is also identified in the Bose-side SmartSpeaker signal path.

The Raspberry Pi interface must not introduce a 5 V pull-up onto the Bose bus. The intended design uses the Bose-side pull-up to establish the bus HIGH level.

These component references describe the current project findings and should be checked against the relevant circuit diagram and physical hardware.

### 8.3 Shared Bus and Signal Observation

The SmartSpeaker Bus is treated as a shared, bidirectional communication line.

The UART transmit signal drives the bus through the open-collector buffer. The UART receive input observes the bus through the specified series resistor. GPIO16 provides an independent passive observation path.

This arrangement supports investigation of transmitted data, physical bus activity, possible TX echo, and potential PS28 responses.

### 8.4 Verification and Safety

Before connecting or operating the interface, verify the assembled circuit against the schematic and component data sheet. Confirm the supply voltage, grounding, signal connections, and bus voltage levels.

The exact electrical behaviour and protocol response must be established through measurements and repeatable tests. A received byte alone does not prove that the PS28 generated a valid response.

## 9. Software Responsibilities

The software design separates:

- UART access.
- Passive data capture.
- Byte and burst decoding.
- Protocol interpretation.
- Control-state management.
- Hardware and service diagnostics.

This separation allows the protocol model to evolve as additional evidence becomes available.

The proposed software control model is described in [state-machine.md](state-machine.md).

## 10. Current Findings

The current investigation establishes the following working basis:

- Digital audio and control communication are separate paths.
- The UART configuration for the bus investigation is 4800 baud, 8N1.
- The passive sniffer can decode complete data bursts.
- Captured byte sequences are available for further protocol analysis.
- Some message interpretations remain provisional.

The complete initialization sequence, message semantics, required responses, and final control behaviour remain to be validated against the actual Bose hardware.

## 11. Reporting Further Findings

Future protocol findings should record:

1. The hardware and software configuration used.
2. The direction of observation, where known.
3. The exact captured or transmitted bytes.
4. The conditions under which the observation occurred.
5. Whether the result was repeatable.
6. Which conclusions are measured facts and which remain interpretations.
