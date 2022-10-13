{
    inputs = {
        nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
        utils.url = "github:numtide/flake-utils";
    };

    outputs = {self, nixpkgs, utils}: let
      out = system: let
          system = "x86_64-linux";
          pkgs = nixpkgs.legacyPackages."${system}";
        in {
            devShell = pkgs.mkShell {
                buildInputs = with pkgs; [
                  jetbrains.pycharm-community
                  python38
                  python3Packages.ipython
                  python3Packages.pip
                ];
            };

            # defaultPackage = with pkgs.poetry2nix; mkPoetryApplication {
            #     projectDir = ./.;
            #     preferWheels = true;
            # };

            # defaultApp = utils.lib.mkApp {
            #     drv = self.defaultPackage."${system}";
            # };

        };
      in with utils.lib; eachSystem defaultSystems out;

}
