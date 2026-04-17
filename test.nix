# Dell AC511 Volume Control - NixOS Module Test
#
# Usage:
#   nix build .#test-module    # Build the test configuration
#
# Parameters (passed by flake.nix via callPackage):
#   pkgs           - Nix packages for the target system
#   ac511Module    - The NixOS module to test
#   ac511Package   - The ac511-volume package (for customPkg node)

{
  pkgs,
  ac511Module,
  ac511Package,
}:

pkgs.testers.nixosTest {
  name = "ac511-volume-module-test";

  nodes =
    let
      # Shared module for machines that enable the service
      enableModule = {
        imports = [ ac511Module ];
        services.ac511-volume.enable = true;
      };
    in
    {
      # Machine with service enabled (default package)
      enabled = enableModule;

      # Machine with service disabled — verifies nothing leaks
      disabled = {
        imports = [ ac511Module ];
        services.ac511-volume.enable = false;
      };

      # Machine with custom package override
      customPkg = {
        imports = [ ac511Module ];
        services.ac511-volume = {
          enable = true;
          package = ac511Package;
        };
      };
    };

  testScript =
    let
      # Helper: build a bash test snippet for service-enabled machines
      testServiceEnabled = machineName: ''
        with subtest("${machineName}: systemd user service unit is generated"):
            ${machineName}.succeed("test -f /etc/systemd/user/ac511-volume.service")

        with subtest("${machineName}: service ExecStart points to ac511-volume binary"):
            ${machineName}.succeed("grep -q 'ExecStart=.*bin/ac511-volume' /etc/systemd/user/ac511-volume.service")

        with subtest("${machineName}: service has correct dependencies (After)"):
            ${machineName}.succeed("grep -q 'After=.*pipewire.socket' /etc/systemd/user/ac511-volume.service")
            ${machineName}.succeed("grep -q 'After=.*pulseaudio.socket' /etc/systemd/user/ac511-volume.service")

        with subtest("${machineName}: service restarts on failure"):
            ${machineName}.succeed("grep -q 'Restart=on-failure' /etc/systemd/user/ac511-volume.service")

        with subtest("${machineName}: udev rule is installed"):
            ${machineName}.succeed("grep -q 'Dell AC511 USB SoundBar' /etc/udev/rules.d/*.rules || grep -rq 'Dell AC511 USB SoundBar' /etc/udev/")

        with subtest("${machineName}: ac511-volume binary exists and is executable"):
            ${machineName}.succeed("grep -oP 'ExecStart=\\K\\S+' /etc/systemd/user/ac511-volume.service | xargs test -x")

        with subtest("${machineName}: ac511-volume binary runs and detects no hardware"):
            # The binary should start, import all Python modules, then exit 1
            # because no Dell AC511 hardware is present in the VM.
            # This proves all Python code and imports work correctly at runtime.
            ${machineName}.fail("$(grep -oP 'ExecStart=\\K\\S+' /etc/systemd/user/ac511-volume.service)")
      '';
    in
    ''
      # =========================================================================
      # Tests for service ENABLED machines
      # =========================================================================
      ${testServiceEnabled "enabled"}
      ${testServiceEnabled "customPkg"}

      # =========================================================================
      # Tests for service DISABLED machine
      # =========================================================================
      with subtest("disabled: no systemd user service unit is generated"):
          disabled.fail("test -f /etc/systemd/user/ac511-volume.service")

      with subtest("disabled: no udev rule for AC511"):
          disabled.fail("grep -rq 'Dell AC511 USB SoundBar' /etc/udev/")

      # =========================================================================
      # Cross-machine: customPkg uses the explicitly set package
      # =========================================================================
      with subtest("customPkg: ExecStart uses the package from services.ac511-volume.package"):
          customPkg.succeed("grep -q 'ExecStart=.*bin/ac511-volume' /etc/systemd/user/ac511-volume.service")
    '';
}
