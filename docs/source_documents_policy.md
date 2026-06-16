# Source Documents Policy

This page records the handling rules for the source material preserved in the
repository.

Policy notes:

- keep the canonical unpacked standards bundle in `specs/ieee-1516-2010/`
- keep the retained PDF archive in `docs/reference/`
- keep generated verification packets, matrices, and reports under `analysis/`
  so they stay out of the tracked seed
- keep reproducible code generation under package-local `_generated/`
  directories or `build/generated/` so source-derived files can be regenerated
  instead of committed
- avoid duplicating the same archive in multiple repo-local locations
- treat bibliographic and archive-reference material as non-normative source
  context unless another tracked artifact cites it as normative evidence
- review IEEE licensing and redistribution requirements before publishing or
  redistributing the repository

Extraction note:

- the Python source tracks section anchors through `hla.rti1516e.spec_refs` and
  related docstrings
- generated verification packets and matrices are intentionally excluded from
  the clean repo seed
- `hla.rti1516e.raw_api` is retained source-derived metadata; new generated
  standard API code should go into the package-local `_generated/` bucket above

Use this page when you want the policy story rather than the inventory.
