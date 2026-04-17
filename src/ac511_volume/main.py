"""
Dell AC511 Soundbar Volume Control
Automatically detects the AC511, audio backend, and controls volume.
Portable across different hosts and audio systems.
"""

import os
import struct
import subprocess
import sys
import re
import time

# EV_KEY event type
EV_KEY = 0x01

# Volume key codes (from linux/input.h)
KEY_VOLUMEUP = 114
KEY_VOLUMEDOWN = 115

# Volume step (percentage as decimal)
VOLUME_STEP = 0.02  # 2%

# Device name to search for
DEVICE_NAME = "Dell AC511"

# input_event struct format
EVENT_FORMAT = 'llHHI'
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)


# ============================================================================
# Audio Backend Detection
# ============================================================================

from ac511_volume.backends import detect_backend


# ============================================================================
# Device Detection
# ============================================================================

def find_ac511_event_device():
    """Find the /dev/input/eventX for Dell AC511."""
    try:
        with open("/proc/bus/input/devices", "r") as f:
            content = f.read()

        lines = content.split('\n')
        device_found = False
        for line in lines:
            if DEVICE_NAME in line:
                device_found = True
            elif device_found and "Handler" in line:
                match = re.search(r'event(\d+)', line)
                if match:
                    event_num = match.group(1)
                    device_path = f"/dev/input/event{event_num}"
                    if os.path.exists(device_path):
                        return device_path
                device_found = False
    except Exception as e:
        print(f"Error finding device: {e}")
    return None


# ============================================================================
# Main
# ============================================================================

def volume_adjust(backend, sink_id, delta):
    """Adjust volume by delta."""
    try:
        current = backend.get_volume(sink_id)
        new_vol = max(0.0, min(1.0, current + delta))
        print(f"  Vol: {current:.0%} -> {new_vol:.0%}")
        backend.set_volume(sink_id, new_vol)
    except Exception as e:
        print(f"  Error: {e}")


def main():
    print("Dell AC511 Soundbar Volume Control")
    print("=" * 50)

    # Auto-detect device
    device = find_ac511_event_device()
    if not device:
        print(f"Error: Could not find {DEVICE_NAME} input device!")
        print("Make sure the soundbar is connected.")
        sys.exit(1)
    print(f"Input device: {device}")

    # Auto-detect audio backend
    backend, backend_name = detect_backend()
    if not backend:
        print("Error: No audio backend found (PipeWire/PulseAudio/ALSA)")
        sys.exit(1)
    print(f"Audio backend: {backend_name}")

    # Find sink with retry (PipeWire may not have enumerated it yet on boot)
    sink_id = None
    max_retries = 10
    retry_delay = 1.0  # seconds
    for attempt in range(max_retries):
        sink_id = backend.find_sink()
        if sink_id:
            break
        if attempt < max_retries - 1:
            print(f"  Sink not found, retrying in {retry_delay:.1f}s... (attempt {attempt + 1}/{max_retries})")
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 1.5, 10)  # exponential backoff, cap at 10s
        else:
            print(f"Error: Could not find AC511 SoundBar sink after {max_retries} attempts!")
            sys.exit(1)
    print(f"Sink: {sink_id}")

    print("\nTurn the volume knob to adjust volume")
    print("(Press Ctrl+C to stop)\n")

    try:
        with open(device, 'rb') as fd:
            while True:
                data = fd.read(EVENT_SIZE)
                if len(data) < EVENT_SIZE:
                    break

                _, _, event_type, event_code, value = struct.unpack(EVENT_FORMAT, data)

                if event_type == EV_KEY and value == 1:
                    if event_code == KEY_VOLUMEUP:
                        print("[VOL UP]", end=" ")
                        volume_adjust(backend, sink_id, VOLUME_STEP)
                    elif event_code == KEY_VOLUMEDOWN:
                        print("[VOL DOWN]", end=" ")
                        volume_adjust(backend, sink_id, -VOLUME_STEP)

    except PermissionError:
        print(f"Permission denied. Run: sudo chmod 666 {device}")
    except KeyboardInterrupt:
        print("\nStopped.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
