# Source Documents Policy

This page records the handling rules for the source material preserved in the
repository.

Policy notes:

- keep the canonical unpacked standards bundle in `specs/ieee-1516-2010/`
- keep the retained PDF archive in `docs/reference/`
- keep generated verification packets, matrices, and reports under `analysis/`
  so they stay out of the tracked seed
- keep reproducible code generation under `hla2010/generated/` or
  `build/generated/` so source-derived files can be regenerated instead of
  committed
- avoid duplicating the same archive in multiple repo-local locations
- treat bibliographic and archive-reference material as non-normative source
  context unless another tracked artifact cites it as normative evidence
- review IEEE licensing and redistribution requirements before publishing or
  redistributing the repository

Extraction note:

- the Python source tracks section anchors through `hla2010.spec_refs` and
  related docstrings
- generated verification packets and matrices are intentionally excluded from
  the clean repo seed
- `hla2010/raw_api.py` is the last source-derived compatibility file that still
  lives in the tracked package root; new generated code should go into the
  generated-code bucket above

Use this page when you want the policy story rather than the inventory.
