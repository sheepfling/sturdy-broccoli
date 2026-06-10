# Local Verification Notes

Environment and caveats from the latest local verification run:

- The combined `seed_suite.sh` wrapper retries a transient `SIGKILL` once for each stage before failing.
- The real runtime matrix was verified locally with:
  - `HLA2010_CERTI_PREFIX=/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/.local/certi/patched/install`
  - `HLA2010_CERTI_BUILD_ROOT=/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/.local/certi/patched/build`
  - `HLA2010_PITCH_HOME=/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/third_party/pitch/PITCH-prti1516e-manual`
  - `HLA2010_PITCH_USER_HOME=/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/.local/pitch/user-home`
- The sandbox initially blocked local socket binds for CERTI; rerunning with escalated permissions allowed the matrix to complete successfully.
- The sandbox also blocked access to the Docker Desktop socket for the Docker-backed Pitch route; rerunning with escalated permissions allowed the vendor matrix to complete successfully.

Use this page when you want the operational caveats and environment pins.
