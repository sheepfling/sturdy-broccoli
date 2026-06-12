# CERTI Docs

Vendor-owned CERTI runtime and parity notes live here.

This package owns:
- CERTI runtime integration and plugin code under `src/hla2010_rti_certi/`
- package-owned verification/preflight policy in `src/hla2010_rti_certi/testing_policy.py`
- CERTI-specific operator notes for `./tools/certi-easy`
- package-owned split-package and real-runtime wrapper tests in
  `tests/test_rti_certi_split_package.py`,
  `tests/vendors/test_certi_real_backend_exchange_matrix.py`,
  `tests/vendors/test_certi_real_backend_ownership_matrix.py`, and
  `tests/vendors/test_certi_real_backend_time_matrix.py`

- [certi_section8_runbook.md](certi_section8_runbook.md): operator runbook for compare and smoke flows
- [certi_runtime_limitations.md](certi_runtime_limitations.md): current upstream-vs-patched runtime gaps
- [certi_spec_traceability.md](certi_spec_traceability.md): clause-level CERTI evidence summary
- [certi_negotiated_ownership_findings.md](certi_negotiated_ownership_findings.md): negotiated-ownership investigation notes
