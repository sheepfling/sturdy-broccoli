# hla-backend-shim

`hla-backend-shim` provides the current in-repo RTI backend for the IEEE
1516.1-2025 Python API package.

Historically this lane started as a deliberately small, spec-shaped shim while
the 2025 surface was being stood up. In the current repo it is the active
Python implementation lane for `rti1516_2025`, and the verification work in
this workspace treats it as a real executable backend rather than a stub.

It is not a 2010 backend and it is not a vendor adapter. The longer-term
architectural goal is to keep shim concerns and RTI concerns separable enough
that this lane can either justify promotion as the real 2025 Python RTI or be
cleanly split into a narrower shim plus a dedicated 2025 RTI backend later.

For the current evidence-based decision point, see
[`docs/plans/2025_python_rti_backend_audit.md`](../../docs/plans/2025_python_rti_backend_audit.md)
and
[`docs/python_rti_backend.md`](../../docs/python_rti_backend.md).
