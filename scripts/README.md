# Scripts

This directory holds the repo-local entrypoints for setting up and validating
the IEEE 1516.1-2010 workspace.

Core workflow:

- `bootstrap_python.sh` create or refresh the local Python virtualenv and
  install editable project dependencies
- `rebuild_certi.sh` configure, build, and install the repo-local CERTI source
  tree into `CERTI-build/` and `CERTI-install/`
- `bootstrap_all.sh` run both of the above in sequence
- `run_certi_local.sh` launch `rtig` or `rtia` against the repo-local CERTI
  install
- `run_pitch_local.sh` launch the extracted Pitch runtime if present

The remaining test and validation entrypoints should build on those helpers
instead of re-implementing environment detection.
