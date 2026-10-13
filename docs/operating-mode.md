# Operating Mode and Serial Interface

## Mandatory mode selection

**Bose Pi uses the normal Bose SmartSpeaker mode only. TAP mode is not used.**

TAP is not required for normal startup, control, playback, troubleshooting or recovery. The TAP-related contacts are left unconnected. No TAP mode-entry command may be sent by the project software.

## SmartSpeaker serial interface

| Parameter | Value |
|---|---|
| Baud rate | 4800 |
| Data bits | 8 |
| Parity | None |
| Stop bits | 1 |
| Frame | 8N1 |
| Electrical arrangement | Bidirectional open-collector DATA line |
| Documented pull-up | 3.3 V |

The Bose service documentation describes the SmartSpeaker and TAP serial interfaces separately. Their framing must not be confused. The SmartSpeaker path uses 8N1; TAP is outside this project's scope.

## Hardware interface

- Raspberry Pi GPIO14 / UART0 TX drives the input of the SN74HC07N.
- SN74HC07N open-collector output connects to SmartSpeaker DATA.
- Raspberry Pi GPIO15 / UART0 RX receives the bus.
- GPIO16 is reserved for the separate passive sniffer path.
- Common ground and voltage levels must match the reference wiring.

## Evidence discipline

A serial byte capture is evidence that bytes were observed; it does not by itself prove the semantic meaning of those bytes or that a byte is a response from the PS28. Record raw captures, direction, timing, test conditions and the exact software revision. Label protocol interpretations as hypotheses until repeatable tests support them.

Do not add periodic keepalives, retries, or extra command sequences merely because another implementation does so. Add them only when the project's own evidence demonstrates they are required.
