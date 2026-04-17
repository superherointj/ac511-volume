# Dell AC511 USB SoundBar Volume Control

A userspace daemon that enables the **volume knob** on the **Dell AC511 USB SoundBar** under **Linux**.

## The Problem

The Dell AC511 SoundBar has a rotary volume knob that sends USB HID events. While audio works out of the box, the volume knob doesn't control system volume on Linux because:

1. The knob's HID events are interpreted as keyboard events (not volume keys)
2. Desktop environments only listen for volume keys from the system keyboard

## The Solution

This daemon auto-detects the Dell AC511 input device, reads volume knob events, and adjusts audio backend volume using the native API:
- **PipeWire**
- **PulseAudio**
- **ALSA**

## NixOS Usage

```nix
{
  inputs.ac511-volume.url = "github:superherointj/ac511-volume";

  outputs = { self, nixpkgs, ac511-volume }: {
    nixosConfigurations.yourhost = nixpkgs.lib.nixosSystem {
      modules = [
        ac511-volume.nixosModules.ac511-volume
        { services.ac511-volume.enable = true; }
      ];
    };
  };
}
```

## License

MIT