# Python RTI Docs

Package-owned notes for the pure in-memory Python RTI backend live here.

- `src/hla2010_rti_python/` owns the backend implementation.
- `testing_policy.py` owns package-specific policy helpers.
- `./tools/python verify` is the repo-green verification lane.
- Shared scenario bodies live in `hla2010-verification-harness`; Python backend
  tests should stay thin wrappers over those shared scenarios.
- Split-package and backend policy guards live in
  `tests/test_rti_python_split_package.py` and `tests/test_python_matrix_policy.py`.

If you are connecting this backend through a transport host, read
[`../../../docs/networked_rti_python.md`](../../../docs/networked_rti_python.md).
