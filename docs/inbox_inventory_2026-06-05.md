# INBOX Inventory 2026-06-05

Scope: `hla-2010/INBOX`

## Summary

Four ZIP archives were present in `INBOX`. They were distinct by SHA-256 and
were classified into four buckets:

- standards/reference bundle
- repo seed code drop
- verification evidence packet
- third-party RTI/vendor installers

The repo was normalized so that:

- working standards/source material is canonical under `specs/ieee-1516-2010/`
- retained archives live under `docs/reference/`, `archives/`, or `third_party/`
- unpacked evidence lives under `docs/evidence/`
- `INBOX` is left as transient staging rather than long-term storage

## Archive Inventory

1. `hla-2010-specs.zip`
SHA-256: `1d806b28105cfed0c5c2d09757c6133cdf3f5e8b25be741bdce6bec4be1aaa55`
Classification: standards/reference PDFs
Promoted archive: `docs/reference/hla-2010-specs.zip`
Dedup note: not unpacked into `docs/reference/` because the canonical unpacked working copy already exists at `specs/ieee-1516-2010/`

2. `hla2010_python_repo_seed.zip`
SHA-256: `3f8c1714dadeb3eb80c6e731bffb6be52026675bc4080760328f5898695e2d68`
Classification: working Python HLA 2010 source drop
Promoted archive: `archives/source-drops/hla2010_python_repo_seed.zip`
Unpacked into repo root: `hla2010/`, `examples/`, `tests/`, `tools/`, `java_shims/`, `specs/ieee-1516-2010/`, and associated docs

3. `hla2010_python_verification_evidence_v0_13.zip`
SHA-256: `9b72c952d378a8906d7130da0c26206ea1aef6c4b7fbe09272f4ce03df7c6bde`
Classification: verification evidence packet
Promoted archive: `archives/verification/hla2010_python_verification_evidence_v0_13.zip`
Unpacked location: `docs/evidence/hla2010_python_verification_evidence_v0_13/`

4. `HLA_PITCH_linux.zip`
SHA-256: `1295f8ec22784ad9c8c31e078814975a518c7af3326f4e58521ace13e952af86`
Classification: third-party vendor bundle
Promoted archive: `third_party/pitch/HLA_PITCH_linux.zip`
Unpacked location: `third_party/pitch/HLA_PITCH_linux/`
Dedup note: removed extracted `__MACOSX/` metadata directory; this bundle duplicates the already-extracted Pitch runtime work performed in the sibling `hla-python` workspace

## Canonical Locations After Promotion

- Working Python HLA 2010 implementation:
  `hla2010/`
- Working standards/source bundle:
  `specs/ieee-1516-2010/`
- Verification evidence:
  `docs/evidence/hla2010_python_verification_evidence_v0_13/`
- Third-party Pitch installers:
  `third_party/pitch/`

## Follow-up

- If `hla-2010` becomes a standalone git repo, add an ignore policy for bulky
  extracted vendor payloads and generated evidence outputs before committing.
- If Portico is still required, add the actual Portico distribution separately;
  the Pitch bundle is not a Portico drop.
