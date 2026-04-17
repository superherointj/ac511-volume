# Dell AC511 Volume Control - Implementation Specification

## Architecture Overview

```
/dev/input/eventX  -->  ac511_volume  -->  [wpctl|pactl|amixer]
       |                  |                    |
   HID events          Event parsing         Audio backend
   (volume knob)      & volume control      (PipeWire/PulseAudio/ALSA)
```

## Component Specification

### 1. Python Package: `ac511_volume`

**Location:** `src/ac511_volume/`

**Responsibility:** All Python code for the daemon.

#### Main Module (`src/ac511_volume/main.py`)

Daemon entry point and orchestration:
- Device detection via `/proc/bus/input/devices`
- Event parsing (struct unpack of input_event)
- Volume adjustment via backends (imported from `ac511_volume.backends`)
- `main()` function as the entry point
- Exits with code 1 when device not found (enables automated testing)

#### Backends (`src/ac511_volume/backends/`)

Abstract interface for audio volume control:

```python
class AudioBackend:
    def find_sink(self) -> Optional[Any]
    def get_volume(self, sink_id: Any) -> float
    def set_volume(self, sink_id: Any, volume: float) -> None
```

**PipeWire (`pipewire.py`):**
- Binary: `wpctl`
- Find sink: Parse `wpctl status` for "Sound Bar" + "Analog"/"Stereo"
- Get volume: `wpctl get-volume <sink_id>`
- Set volume: `wpctl set-volume <sink_id> <volume>`

**PulseAudio (`pulseaudio.py`):**
- Binary: `pactl`
- Find sink: Parse `pactl list short sinks` for "AC511" or "SoundBar"
- Get volume: `pactl get-sink-volume <sink_id>`
- Set volume: `pactl set-sink-volume <sink_id> <vol>%`

**ALSA (`alsa.py`):**
- Binary: `amixer`, `aplay`
- Find sink: Parse `aplay -l` for card number, return `hw:{num}`
- Get volume: `amixer -D hw:{num} sget PCM`
- Set volume: `amixer -D hw:{num} sset PCM <vol>%`

**Auto-Detection (`backends/__init__.py`):**
1. Check `/run/user/1000/pipewire-0` exists -> PipeWire
2. Else check `pactl --version` -> PulseAudio
3. Else check `amixer --version` -> ALSA

#### Entry Points

- **`src/ac511_volume/__init__.py`**: Package init, exposes `main`
- **`src/ac511_volume/__main__.py`**: Supports `python -m ac511_volume`
- **`src/ac511_volume/main.py`**: `main()` function + `if __name__ == "__main__"` guard for direct execution
- **`pyproject.toml`** `[project.scripts]`: `ac511-volume = "ac511_volume.main:main"`

### 2. NixOS Module

**Location:** `ac511-volume-module.nix` (root)

**Module signature:** `{ lib, config, pkgs, ... }:` — standard NixOS module args only, no `self`.

**Options:**
```nix
services.ac511-volume = {
  enable = mkOption { type = bool; default = false; };
  package = mkOption { type = package; };  # no default — provided by flake wrapper
}
```

**Configuration when enabled (`mkIf cfg.enable`):**
1. Udev rule: `SUBSYSTEM=="input", ATTRS{name}=="Dell AC511 USB SoundBar", MODE="0444"`
2. Systemd user service (`systemd.user.services.ac511-volume`) using NixOS schema

**Service (NixOS schema):**
```nix
{
  description = "Dell AC511 USB SoundBar Volume Control";
  after = [ "pipewire.socket" "pulseaudio.socket" ];
  partOf = [ "graphical-session.target" ];
  wantedBy = [ "graphical-session.target" ];
  path = [ pkgs.wireplumber pkgs.pulseaudio pkgs.alsa-utils ];
  serviceConfig = {
    Type = "simple";
    ExecStart = "${cfg.package}/bin/ac511-volume";
    Restart = "on-failure";
    RestartSec = "5s";
    Environment = [ "PYTHONUNBUFFERED=1" ];
  };
}
```

**Note:** The `path` attribute takes a list of packages and adds their `bin` directories to the service's PATH. This is simpler than manually constructing PATH via `Environment`. The script auto-detects the first available backend (PipeWire → PulseAudio → ALSA) so all three packages are needed for portability.

### 3. NixOS VM Test

**Location:** `test.nix` (root)

**Framework:** `pkgs.testers.nixosTest` (legacy `makeTest` interface)

**Test nodes (3 VMs):**

| Node | Purpose |
|------|---------|
| `enabled` | Service enabled with default package |
| `disabled` | Service disabled — verifies nothing leaks |
| `customPkg` | Service enabled with explicit package override |

**All enabled nodes receive `ac511Module` as a parameter** (passed via flake.nix) — the test is self-contained and does not reference `self.nixosModules`.

**Subtests (18 total across 3 machines):**

For each enabled machine (`enabled`, `customPkg`):
1. Systemd user service unit file exists at `/etc/systemd/user/ac511-volume.service`
2. ExecStart points to `bin/ac511-volume`
3. After dependencies include `pipewire.socket` and `pulseaudio.socket`
4. Restart is set to `on-failure`
5. Udev rule containing "Dell AC511 USB SoundBar" is installed in `/etc/udev/`
6. Binary from ExecStart path is executable
7. Binary actually runs and exits with code 1 (no hardware in VM — proves all Python imports resolve)

For disabled machine:
1. No systemd user service unit file
2. No udev rule for AC511

Cross-machine:
1. `customPkg` ExecStart uses the explicitly set package

## File Structure

```
project/                        # Nix project (root)
├── flake.nix                   # Flake: packages, nixosModules, default = test
├── package.nix                 # Python package derivation
├── ac511-volume-module.nix     # NixOS module (pure, standard args only)
├── test.nix                    # NixOS VM test (3 nodes, 18 subtests)
├── README.md                   # Project overview and usage
├── LICENSE                     # MIT license
├── src/                        # Python project
│   ├── pyproject.toml          # Python package metadata
│   ├── test_backends.py        # Integration tests
│   └── ac511_volume/           # Main package
│       ├── __init__.py         # Package init
│       ├── __main__.py         # python -m support
│       ├── main.py             # main() + if __name__ guard
│       └── backends/           # Audio backend implementations
│           ├── __init__.py     # Auto-detection
│           ├── base.py         # AudioBackend abstract class
│           ├── pipewire.py     # PipeWire implementation
│           ├── pulseaudio.py   # PulseAudio implementation
│           └── alsa.py         # ALSA implementation
└── specs/
    ├── requirements.md
    └── implementation.md
```

## Nix Packaging

**Package (`package.nix`):**
- Uses `pkgs.python3.pkgs.buildPythonApplication`
- `src = ./src` (the Python project)
- `pyproject = true` (setuptools/build from pyproject.toml)
- `nativeBuildInputs = [ setuptools ]`
- `checkPhase` runs `python3 test_backends.py`
- Creates `bin/ac511-volume` console script via pyproject.toml entry point

**Flake (`flake.nix`):**
- `packages.x86_64-linux.ac511-volume` → the Python package
- `packages.x86_64-linux.test-module` → NixOS VM test (also `default`)
- `nixosModules.ac511-volume` → wraps the raw module and sets default package via `mkDefault`

**Key design decisions:**
- The raw module (`ac511-volume-module.nix`) uses only standard NixOS args (`lib`, `config`, `pkgs`) — no `self` dependency
- The `package` option has no default in the raw module — it's set by the flake wrapper via `nixpkgs.lib.mkDefault`
- This makes the module importable from any flake without `_module.args` hacks
- `nixosModules` wraps the raw module with `{ imports = [...]; services.ac511-volume.package = mkDefault ...; }` — NOT `callPackage` (which adds `.override` attributes)

## Design Principles

1. **`src/` is pure Python** — no Nix code, no shebangs, just the library/application
2. **Shebang belongs in packaging** — `pyproject.toml` entry point + `buildPythonApplication` handles wrapper creation
3. **`main()` has `if __name__` guard** — allows both `python -m ac511_volume` and direct execution
4. **Nix at root, Python in src/** — clear separation of concerns
5. **Module uses NixOS systemd schema** — flat attributes (`description`, `after`, `wantedBy`, `serviceConfig`), not raw INI-style sections (`Unit`, `Service`, `Install`)
6. **Binary exits 1 on missing hardware** — enables VM testing to verify all Python imports resolve at runtime
7. **Module is pure NixOS** — standard args only (`lib`, `config`, `pkgs`), no flake-specific `self` — importable from any flake without `_module.args` hacks
