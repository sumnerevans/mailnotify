{
  description = "mailnotify";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    (flake-utils.lib.eachDefaultSystem (system:
      let pkgs = import nixpkgs { system = system; };
      in rec {
        packages.mailnotify = pkgs.buildGoModule {
          pname = "mailnotify";
          version = "unstable-2023-12-14";
          src = self;

          propagatedBuildInputs = [ pkgs.libnotify ];

          vendorHash = "sha256-Mj1vte+bnDmY/tn6+GXX9IwIKgy9J4QvoIP/pLcID6E=";
        };
        defaultPackage = packages.mailnotify;

        devShells.default = pkgs.mkShell {
          packages = with pkgs; [ libnotify go gotools gopls yq ];
        };
      }));
}
