# hla-backend-python2025

Main full Python RTI backend package for IEEE 1516.1-2025.

This package now owns the main full Python 2025 RTI runtime. Core 2025 backend
semantics execute from `hla.backends.python2025`, and the legacy
`hla-backend-shim` package remains as a compatibility wrapper for older route
and provider names.

Current status:

- discoverable as backend `python2025`
- executes the main full 2025 runtime directly
- must not delegate back to `hla.backends.shim.backend.create_shim_backend`
- is the promoted Python-owned 2025 RTI implementation lane in the repo

The remaining architectural work is to keep narrowing `hla-backend-shim`
toward wrapper-only concerns while preserving proof parity across the direct
and hosted 2025 routes.
