{ pkgs ? import <nixpkgs> {} }: with pkgs;
pkgs.mkShell {
  nativeBuildInputs = [
    gobject-introspection
    python3Packages.setuptools
    wrapGAppsHook
  ];

  buildInputs = [
    libnotify
  ];

  propagatedBuildInputs = with python3Packages; [
    cairo
    pkg-config
    poetry
    (python38.withPackages (ps: with ps; [
      pygobject3
      pycairo
      watchdog
    ]))
  ];

  # hook for gobject-introspection doesn't like strictDeps
  # https://github.com/NixOS/nixpkgs/issues/56943
  strictDeps = false;
}

