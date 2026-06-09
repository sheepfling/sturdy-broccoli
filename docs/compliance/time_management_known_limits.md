# Time Management Known Limits

- Pure Python RTI is the reference implementation for the closeout matrix.
- Pitch and CERTI rows remain `NOT_TESTED` in the generated backend comparison unless their external runtimes are available and their vendor matrix commands are run.
- FQR is intentionally grant-bound: it does not drain all queued TSO messages when GALT or the earliest deliverable message limits the grant.
- The closeout matrix is source-test traceability, not a substitute for vendor certification.
