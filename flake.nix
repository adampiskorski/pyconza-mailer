{
  description = "Python dev shell with uv + g++";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }: let
    pkgs = import nixpkgs { system = "x86_64-linux"; };
  in {
    devShells.default = pkgs.mkShell {
      buildInputs = [
        pkgs.python315
        pkgs.uv
        pkgs.gcc            # provides g++ and friends
        pkgs.make
        pkgs.pkg-config
        pkgs.openssl
        pkgs.zlib
      ];
      shellHook = ''
        export UV_PYTHON=${pkgs.python315}/bin/python3.15
        export UV_NO_MANAGED_PYTHON=1
      '';
    };
  };
}
