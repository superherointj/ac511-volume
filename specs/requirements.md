# Dell AC511 Volume Control - Requirements Specification

## Overview

Enable the Dell AC511 USB SoundBar volume knob to control system volume on Linux.

## Stakeholders

- **User**: Linux desktop user with Dell AC511 SoundBar connected
- **Developer**: Packager/Maintainer of the project

## User Requirements

### FR-1: Volume Control via Knob
The volume knob on the Dell AC511 SoundBar must adjust system volume when rotated.

**Acceptance Criteria:**
- Rotating the knob clockwise increases volume
- Rotating the knob counter-clockwise decreases volume
- Each detent of the knob changes volume by a small, perceptible amount (~2%)

### FR-2: Automatic Detection
The daemon must work without user configuration when the SoundBar is connected.

**Acceptance Criteria:**
- No manual installation of udev rules required
- No manual configuration of device paths required
- Works across different Linux distributions with different audio systems

### FR-3: Multi-Backend Support
The daemon must support common Linux audio systems.

**Acceptance Criteria:**
- Works with PipeWire (primary modern system)
- Works with PulseAudio (legacy system)
- Works with ALSA (fallback for minimal systems)

### FR-4: Permission Handling
The daemon must not require root privileges to function.

**Acceptance Criteria:**
- Runs as regular user
- Can access /dev/input/event* via udev rules or group membership
- Audio control via user-accessible APIs (wpctl, pactl, amixer)

### FR-5: NixOS Integration
The daemon must be installable via NixOS module.

**Acceptance Criteria:**
- Single NixOS option enables the service: `services.ac511-volume.enable = true`
- Module handles all setup (udev rules, systemd user service)
- Custom package can be specified: `services.ac511-volume.package`

### FR-6: Automated Testing
The NixOS module must have automated verification via NixOS VM tests.

**Acceptance Criteria:**
- Test verifies systemd user service unit is generated when enabled
- Test verifies no artifacts leak when disabled
- Test verifies the Python binary actually executes (all imports resolve)
- Test verifies udev rules are installed
- Test verifies custom package option works

## Non-Functional Requirements

### NFR-1: No External Python Dependencies
The main daemon must have zero Python dependencies beyond the standard library.

**Rationale:** Ensures reliable packaging across different Python environments.

### NFR-2: Single Executable
The volume control should be a single self-contained script.

**Rationale:** Simplifies deployment and debugging.

### NFR-3: Graceful Degradation
If audio hardware is not detected, the daemon must exit cleanly with exit code 1.

**Rationale:** Prevents confusing error states and allows automated testing.

### NFR-4: MIT License
The project must use the MIT license.

**Rationale:** Maximum compatibility and reusability.

## Out of Scope

- Kernel driver development (userspace solution is sufficient)
- Windows/macOS support
- Non-Dell USB audio devices
- Audio playback/recording functionality