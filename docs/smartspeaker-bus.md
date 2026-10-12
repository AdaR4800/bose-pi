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

The following byte sequence has been used during sniffer validation:

`55 00 FF A5 0B`

The sequence is recorded as captured data. Its protocol meaning must be established independently.

A separate protocol observation recorded during development is:

- Transmitted sequence: `01 00 00 01`
- Received sequence: `01 00 00 01 00`

The final `00` has been interpreted as a possible response from the Bose system. This interpretation remains provisional until the sender, message framing, and protocol meaning are confirmed through repeatable tests.

These observations must not be treated as proof that the complete SmartSpeaker Bus protocol has been decoded.

## 7. Patent Descriptions and Real Hardware

The publicly available patent material describes a communication architecture with capabilities beyond the requirements of the Bose-Pi single-system installation.

For example, the patent material discusses master-initiated polling and the reporting of changes made at a speaker back to the central unit.

Bose-Pi focuses on the subset of functionality required by the surviving installation. Features that are unnecessary for this use case are not automatically included in the implementation scope.

Community reverse-engineering work has also reported differences between patent descriptions and observed hardware behaviour, including baud-rate differences.

For this reason, protocol parameters and message semantics must be based on the relevant hardware and repeatable observations.

## 8. Electrical Interface

The Raspberry Pi uses 3.3 V GPIO logic. An appropriate electrical interface is required between the GPIO and the Bose bus.

The Bose-Pi hardware design includes an SN74HC07 open-collector buffer as part of the interface investigation.

The actual circuit, supply voltage, pull-up arrangement, and resulting bus levels must be documented against the final schematic and component data sheet.

The GPIO must not be connected directly to a bus whose electrical characteristics have not been verified as compatible.

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
