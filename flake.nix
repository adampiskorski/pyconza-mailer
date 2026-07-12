{
  description = "Python dev shell with uv + g++";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    nixpkgs-python.url = "github:cachix/nixpkgs-python";
  };

  outputs = { self, nixpkgs, nixpkgs-python }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };
    pythonVersion = "3.15";
    myPython = pkgs.python315;
  in {
    devShells.${system}.default = pkgs.mkShell {
      buildInputs = [
        myPython
        pkgs.uv
        pkgs.gcc
        pkgs.cmake
        pkgs.pkg-config
        pkgs.openssl
        pkgs.zlib
        pkgs.libffi
        pkgs.opencode
      ];
      shellHook = ''
        export UV_PYTHON=${myPython}/bin/python${pythonVersion}
        export UV_NO_MANAGED_PYTHON=1
      '';
    };
  };
}
