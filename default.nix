{ pkgs ? import <nixpkgs> { } }:
let
  hdlparse = pkgs.python2Packages.buildPythonPackage rec {
    pname = "hdlparse";
    version = "1.0.4";
    src = pkgs.fetchFromGitHub {
      owner = "kevinpt";
      repo = "hdlparse";
      rev = "be7cdab08a8c18815cc4504003ce9ca7fff41022";
      sha256 = "sha256-KJXl9lQY6xYJkaS41F8V1jGz5jhu0oPhb/lQVj/gj18="; # TODO
    };
  };
in
with pkgs;
python2Packages.buildPythonPackage rec {
  name = "symbolator";
  version = "1.0.2";
  src = ./.;
  nativeBuildInputs = [ wrapGAppsHook gobject-introspection ];

  propagatedBuildInputs = [
    pango
    hdlparse
    python2Packages.pygobject3
    python2Packages.pycairo
    python2Packages.setuptools
  ];

  meta = with lib; {
    description = "A component diagramming tool for VHDL and Verilog";
    longDescription = ''
      Symbolator is a component diagramming tool for VHDL and Verilog. It will parse HDL source files, extract components or modules and render them as an image.
    '';
    homepage = "http://kevinpt.github.io/symbolator";
    license = licenses.mit;
    platforms = lib.platforms.linux;
    mainProgram = "symbolator";
  };
}
