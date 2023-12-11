{pkgs}: {
  deps = [
    pkgs.postgresql
    pkgs.openssl
  ];
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.postgresql
    ];
  };
}
