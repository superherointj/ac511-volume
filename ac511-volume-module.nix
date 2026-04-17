{
  lib,
  config,
  pkgs,
  ...
}:

let
  cfg = config.services.ac511-volume;
in
{
  options.services.ac511-volume = {
    enable = lib.mkOption {
      type = lib.types.bool;
      default = false;
      description = "Enable Dell AC511 USB SoundBar volume control daemon";
    };

    package = lib.mkOption {
      type = lib.types.package;
      description = "The ac511-volume package to use";
    };
  };

  config = lib.mkIf cfg.enable {
    # Allow any user to read the Dell AC511 input device
    # Note: actual device name is "Dell Dell AC511 USB SoundBar" (Dell duplicated)
    services.udev = {
      extraRules = ''
        SUBSYSTEM=="input", ATTRS{name}=="Dell Dell AC511 USB SoundBar", MODE="0444"
      '';
    };

    systemd.user.services.ac511-volume = {
      description = "Dell AC511 USB SoundBar Volume Control";
      after = [
        "pipewire.socket"
        "pulseaudio.socket"
      ];
      partOf = [ "graphical-session.target" ];
      wantedBy = [ "graphical-session.target" ];

      path = [
        pkgs.wireplumber
        pkgs.pulseaudio
        pkgs.alsa-utils
      ];

      serviceConfig = {
        Type = "simple";
        ExecStart = "${cfg.package}/bin/ac511-volume";
        Restart = "on-failure";
        RestartSec = "5s";
        Environment = [ "PYTHONUNBUFFERED=1" ];
      };
    };
  };
}
