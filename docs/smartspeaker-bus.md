# Bose SmartSpeaker Bus

## 1. Purpose

The Bose SmartSpeaker Bus is the control communication interface between the original Bose Lifestyle receiver and the associated speaker system.

For Bose-Pi, the objective is to understand and implement the subset of this interface required to operate a single existing Bose speaker system without its original central receiver.

The implementation does not aim to reproduce every feature of the original Bose communication architecture.

## 2. Research Sources

The investigation uses several sources of information:

- Bose service documentation and circuit diagrams available online.
- Publicly available Bose patent material describing aspects of the SmartSpeaker Bus hardware and communication architecture.
- Community reverse-engineering work, including Kenneract's Bose-Reverse-Engineering repository.
- Experimental observations and repeatable tests performed as part of Bose-Pi.

Patent descriptions and observations from other Bose installations are treated as useful references, not as proof that every implementation detail is identical on the hardware investigated here.

## 3. Separate Audio and Control Paths

The receiver-to-subwoofer connection serves two distinct purposes.

### 3.1 Digital Audio

The audio path uses an S/PDIF-based digital interface.

Bose-Pi generates digital audio using an INNO-MAKER Digi One HAT and feeds it to the Bose system.

### 3.2 Control Communication

The SmartSpeaker Bus provides a separate control communication path.

The Raspberry Pi requires an appropriate electrical interface to communicate with this bus. The custom interface hardware is documented separately in the hardware documentation.

## 4. Protocol Investigation

The protocol investigation focuses on:

- Electrical characteristics of the bus.
- Serial communication parameters.
- Captured bytes and frame interpretation.
- Differences between patent descriptions and observed hardware behaviour.
- The minimum communication required for the intended single-system setup.

Kenneract's reverse-engineering work reports differences between documented behaviour and observations from real hardware, including baud-rate differences.

Consequently, protocol parameters must be supported by measurements or successful tests on the relevant hardware rather than copied uncritically from a patent or another implementation.

## 5. UART Development Environment

The development platform used for the initial serial experiments was a Raspberry Pi 5 running Debian GNU/Linux 13 (trixie).

The recorded environment included:

- Raspberry Pi 5 Model B, Revision 1.0.
- Linux kernel 6.18.50+rpt-rpi-2712.
- Python 3.13.5.
- PySerial 3.5.

The serial configuration and GPIO assignments are documented in the project development notes. They should be checked against the current configuration before being treated as final deployment settings.

## 6. UART Loopback Testing

A UART loopback test was used to validate the Raspberry Pi's serial transmit and receive path.

The received sequence matched the transmitted sequence.

This established that the tested UART path could transmit and receive data correctly under the loopback test conditions. It did not, by itself, establish successful communication with the Bose SmartSpeaker Bus.

## 7. Baud Rate

A baud rate of 4800 baud is the current working hypothesis for the Bose SmartSpeaker Bus, based on the measurements made during this project.

The investigation also considered 19200 baud during the Raspberry Pi UART experiments.

These two values must not be confused: testing a UART at a particular baud rate is not sufficient evidence that the Bose bus uses that rate.

The final protocol configuration must be supported by successful communication tests with the Bose hardware.

## 8. Electrical Interface

The Raspberry Pi GPIO interface operates at 3.3 V logic levels.

The SmartSpeaker Bus requires an appropriate electrical interface between the Raspberry Pi and the Bose hardware. A custom circuit using an SN74HC07 open-collector buffer is part of the planned interface architecture.

The circuit design, supply voltage, pull-up arrangement, and verified electrical characteristics belong in the hardware documentation. They must be based on the component data sheet and the actual circuit implementation.

The Raspberry Pi GPIO pins must not be connected directly to an electrically incompatible bus.

## 9. Software Design

The software implementation is intended to separate:

- UART access.
- Byte capture and decoding.
- Protocol handling.
- State-machine logic.
- Hardware and service status.

Captured data should remain distinguishable from interpreted protocol messages. This separation makes it easier to revisit assumptions when new measurements become available.

The detailed state machine is documented separately in `state-machine.md`.

## 10. Current Findings and Limitations

The following findings have been established during development:

- The Bose connection contains separate digital-audio and control paths.
- The Raspberry Pi UART loopback test succeeded (after correcting the jumper wiring).
- A baud rate of 4800 baud is the current working hypothesis for the Bose bus.
- Patent descriptions and real-hardware observations may differ.

These findings do not, by themselves, establish that the complete Bose SmartSpeaker protocol has been implemented.

Further protocol details should be added only when supported by captured data, documentation, or repeatable hardware tests.
