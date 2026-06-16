# Portico Requirement Disposition Policy

The generated Portico requirement-disposition artifacts are intentionally
explicit about the current verification boundary:

- applicable Portico rows are currently emitted as `classification-required`
  rather than `not-yet-tested`
- Portico does not yet have promoted package-owned real-runtime wrapper tests
  attached to the shared harness scenarios used by the Python, CERTI, and Pitch
  lanes
- Portico family/profile artifacts must not inherit CERTI or Pitch package docs
  as evidence

Current wrapper baseline:

- `tests/vendors/test_portico_real_backend_matrix.py` now provides the first
  package-owned optional real-runtime thin wrappers for the shared exchange and
  synchronization scenarios over `portico-jpype` and `portico-py4j`
- those wrappers are a prerequisite for future requirement promotion, but they
  do not by themselves justify moving generated rows out of
  `classification-required`

Current generated artifacts:

- `analysis/compliance/portico_requirement_disposition.md`
- `analysis/compliance/portico-jpype_requirement_disposition.md`
- `analysis/compliance/portico-py4j_requirement_disposition.md`

Promotion rule for future Portico rows:

- add a thin Portico backend wrapper that instantiates the backend and runs a
  shared harness scenario
- keep any Portico-specific findings or runtime notes in this package
- regenerate the compliance packet so the promoted row carries Portico-owned or
  backend-neutral evidence rather than inherited evidence from another backend
