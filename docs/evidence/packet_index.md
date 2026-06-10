# Evidence Packet Index

Historical / provenance note:
This index is for preserved packet contents and audit work. Do not use it as
the first stop for current runtime or onboarding guidance.

This page indexes the unpacked evidence packets stored under `docs/evidence/`.

Canonical order:

1. packet README
2. packet contents summary
3. preserved archive source

Current packet:

- [hla2010_python_verification_evidence_v0_13/README.md](hla2010_python_verification_evidence_v0_13/README.md)
  verification packet with analysis matrices, traceability assets, and
  source-context copies from the supplied code drop

Contents summary:

- `analysis/` — generated API inventories, section traceability, service conformance matrices, negative-path matrices, and compliance-delta JSON
- `verification/` — generated verification plan, traceability CSVs, MOM negative matrices, and service conformance CSV
- `tests/` — executable pytest assets used to produce and validate the evidence
- `docs/` — human-readable notes from the v0.8-v0.13 development slices
- `hla2010/` and `tools/` — selected source modules and scripts used to produce the matrices
- `source_docs/` — manifests documenting the source standards and repo-seed scope

Archive source:

- `../../archives/verification/hla2010_python_verification_evidence_v0_13.zip`
