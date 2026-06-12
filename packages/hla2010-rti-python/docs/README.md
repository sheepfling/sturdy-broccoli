# Python RTI Docs

Package-owned notes for the pure in-memory Python RTI backend live here.

- Use `./tools/python verify` for the repo-green verification lane.
- Shared scenario bodies live in `hla2010-verification-harness`; Python backend
  tests should stay thin wrappers over those shared scenarios.
- Backend-specific implementation and policy code lives under
  `src/hla2010_rti_python/`, including `testing_policy.py` for package-owned
  verification profile helpers.
- Split-package and backend policy guards live in
  `tests/test_rti_python_split_package.py` and `tests/test_python_matrix_policy.py`.
