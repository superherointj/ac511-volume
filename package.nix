{
  pkgs ? import <nixpkgs> { },
}:

pkgs.python3.pkgs.buildPythonApplication {
  pname = "ac511-volume";
  version = "1.0.1";

  src = ./src;

  pyproject = true;

  nativeBuildInputs = [
    pkgs.python3.pkgs.setuptools
  ];

  checkPhase = ''
    runHook preCheck
    PYTHONPATH=. python3 test_backends.py
    runHook postCheck
  '';

  meta = with pkgs.lib; {
    description = "Dell AC511 USB SoundBar volume control";
    homepage = "https://github.com/superherointj/ac511-volume";
    license = licenses.mit;
    maintainers = [ lib.maintainers.superherointj ];
    platforms = platforms.linux;
  };
}
