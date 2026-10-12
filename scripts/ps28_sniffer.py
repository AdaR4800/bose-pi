
#!/usr/bin/env python3
"""Passive Bose PS28 SmartSpeaker bus sniffer.
GPIO16, 4800 baud, 8N1. Captures complete bursts, then decodes.
Never transmits on the bus.
"""

import gpiod
import time

CHIP = "/dev/gpiochip0"
GPIO = 16
BAUD = 4800

BIT_NS = 1_000_000_000 / BAUD
FRAME_NS = int(10 * BIT_NS)
START_SAMPLE = int(0.5 * BIT_NS)
DATA_FIRST_SAMPLE = int(1.5 * BIT_NS)
STOP_SAMPLE = int(9.5 * BIT_NS)

BURST_IDLE_NS = 3_000_000
WAIT_S = 0.001


def falling(event):
    return event.event_type == gpiod.EdgeEvent.Type.FALLING_EDGE


def rising(event):
    return event.event_type == gpiod.EdgeEvent.Type.RISING_EDGE


def level_at(edges, timestamp):
    level = 1
    for event in edges:
        if event.timestamp_ns > timestamp:
            break
        level = 1 if rising(event) else 0
    return level


def decode_byte(edges, start):
    if level_at(edges, start + START_SAMPLE) != 0:
        return None

    value = 0
    for bit in range(8):
        sample = start + DATA_FIRST_SAMPLE + bit * int(BIT_NS)
        if level_at(edges, sample):
            value |= 1 << bit

    if level_at(edges, start + STOP_SAMPLE) != 1:
        return None

    return value


def decode_burst(edges):
    falling_edges = [event for event in edges if falling(event)]
    decoded = []
    minimum_start = None

    for event in falling_edges:
        start = event.timestamp_ns

        if minimum_start is not None and start < minimum_start:
            continue

        value = decode_byte(edges, start)
        if value is None:
            continue

        decoded.append((start, value))
        minimum_start = start + STOP_SAMPLE

    return decoded


def print_burst(edges):
    decoded = decode_burst(edges)
    previous = None

    for timestamp, value in decoded:
        extra = ""

        if previous is not None:
            delta = timestamp - previous
            if delta > int(1.5 * FRAME_NS):
                extra = f"  IDLE {(delta - FRAME_NS) / 1000:.1f} us"

        print(f"{timestamp:016d}  RX  {value:02X}{extra}", flush=True)
        previous = timestamp


def main():
    print("PS28 SmartSpeaker Bus Sniffer")
    print("--------------------------------")
    print(f"GPIO       : {GPIO}")
    print(f"Baud       : {BAUD}")
    print("Format     : 8N1")
    print("Direction  : RX only / passive")
    print("Decoder    : complete-burst")
    print()
    print("Waiting for UART frames ...")
    print("Press Ctrl-C to stop.")
    print()

    chip = gpiod.Chip(CHIP)
    line = chip.request_lines(
        consumer="ps28-sniffer",
        config={
            GPIO: gpiod.LineSettings(
                direction=gpiod.line.Direction.INPUT,
                edge_detection=gpiod.line.Edge.BOTH,
                bias=gpiod.line.Bias.DISABLED,
            )
        },
    )

    burst = []
    last = None

    try:
        while True:
            if line.wait_edge_events(WAIT_S):
                for event in line.read_edge_events():
                    if last is not None and event.timestamp_ns - last >= BURST_IDLE_NS:
                        print_burst(burst)
                        burst = []

                    burst.append(event)
                    last = event.timestamp_ns

            elif (
                burst
                and last is not None
                and time.monotonic_ns() - last >= BURST_IDLE_NS
            ):
                print_burst(burst)
                burst = []
                last = None

    except KeyboardInterrupt:
        print()
        if burst:
            print_burst(burst)
        print("Sniffer stopped.")

    finally:
        line.release()
        chip.close()


if __name__ == "__main__":
    main()
