# Public FOM Baseline

This directory is the repo-local baseline for third-party public FOM XML
corpora that we use for parser/load and FedPro JSON transport coverage.

Scope:

- actual upstream XML modules only
- no federate simulations
- no scenario claims beyond parse/load and transport round-trip coverage

Current families:

- `rpr-normative`: HLAGenerator RPR FOM 2.0 normative annex modules
- `netn-merged`: NETN merged HLA Evolved XML baseline
- `portico-samples`: Portico IEEE 1516e MIM plus small sample FOM modules

Support boundary:

- some families are not valid standalone one-file parse units
- the baseline therefore records an explicit file order for family-aware load
- tests prove that ordered family load succeeds and that the original XML payload
  round-trips through the FedPro gRPC JSON envelope

Canonical files:

- manifest: `third_party/fom_baseline/manifest/public_fom_baseline_sources.json`
- edition inventory: `docs/fom-examples/fom_inventory.json`
- edition inventory view: `docs/fom-examples/fom_inventory.md`
- refresh script: `scripts/fetch_public_fom_baseline.py`
- upstream XML root: `third_party/fom_baseline/upstream/`
- tests: `tests/factories/test_public_fom_baseline.py`
