{
  description = "Dell AC511 USB SoundBar volume control for Linux";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
      ];

      # The NixOS module with default package set
      ac511-module =
        {
          lib,
          config,
          pkgs,
          ...
        }:
        {
          imports = [ (import ./ac511-volume-module.nix) ];
          services.ac511-volume.package =
            lib.mkDefault
              self.packages.${pkgs.stdenv.hostPlatform.system}.ac511-volume;
        };
    in
    {
      packages = nixpkgs.lib.genAttrs supportedSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          ac511-pkg = pkgs.callPackage ./package.nix { };
        in
        {
          ac511-volume = ac511-pkg;
          test-module = pkgs.callPackage ./test.nix {
            ac511Module = ac511-module;
            ac511Package = ac511-pkg;
            pkgs = nixpkgs.legacyPackages.${system};
          };
          default = self.packages.${system}.ac511-volume;
        }
      );

      nixosModules.ac511-volume = ac511-module;
    };
}
