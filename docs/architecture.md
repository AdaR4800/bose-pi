# System Architecture

## 1. Overview

Bose-Pi aims to restore the essential functionality of a Bose Lifestyle AV18 speaker system using a Raspberry Pi and a custom hardware interface.

The design separates digital audio generation from control-bus communication.

## 2. Main Components

### Raspberry Pi 5

The Raspberry Pi acts as the central computing platform. It is intended to handle audio services, control logic, and communication with the Bose system.

### INNO-MAKER Digi One HAT

The Digi One HAT provides the S/PDIF digital audio output used to feed the Bose subwoofer.

The original RCA connector was removed to support a compact hardware assembly.

### Custom SmartSpeaker Bus Interface

A custom interface board provides the electrical connection between the Raspberry Pi and the Bose SmartSpeaker Bus.

The interface is built on a prototype breakout board and is intended to keep the bus circuitry separate from the software running on the Raspberry Pi.

### Bose Lifestyle AV18 Speaker System

The original central receiver was destroyed and is no longer available. The surviving system consists of one subwoofer and five satellite speakers.

## 3. Signal Paths

The architecture contains two distinct paths.

**Digital audio path**

AirPlay audio source → Raspberry Pi audio processing → INNO-MAKER Digi One HAT → S/PDIF → Bose subwoofer → satellite speakers.

**Control path**

Raspberry Pi → UART interface → custom electrical interface → Bose SmartSpeaker Bus.

The audio and control paths serve different purposes and must be investigated and validated independently.

## 4. Software Architecture

The software is intended to separate the following responsibilities:

- Audio service management.
- UART communication.
- SmartSpeaker Bus protocol handling.
- State-machine-based control logic.
- Detection of relevant hardware conditions.

The precise interfaces between these components will be documented as the implementation develops.

## 5. Design Principles

- Preserve the existing Bose speaker installation.
- Reproduce only the functionality required by this single-system setup.
- Prefer experimentally verified behaviour over assumptions.
- Keep hardware interfacing separate from protocol and application logic.
- Document test results and distinguish verified features from planned functionality.

## 6. Development Status

This document describes the intended architecture. Individual components and interactions must be considered implemented only when supported by the project's test results.

Further details will be documented in the SmartSpeaker Bus, state-machine, and hardware documentation.
