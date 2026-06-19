# FOM Reading Map

Use this page when you need the shortest path to the repo's FOM artifacts and
their current support boundary.

## Start Here

- bundled repo-owned FOMs:
  - `packages/hla-rti1516e/src/hla/rti1516e/resources/foms/`
  - `packages/hla-fom-target-radar/src/hla/foms/target_radar/resources/foms/`
- imported public example baseline:
  - [`../third_party/fom_baseline/README.md`](../third_party/fom_baseline/README.md)
  - [`../third_party/fom_baseline/SOURCE_INDEX.md`](../third_party/fom_baseline/SOURCE_INDEX.md)
- edition/classification inventory:
  - [`fom-examples/fom_inventory.json`](fom-examples/fom_inventory.json)
  - [`fom-examples/fom_inventory.md`](fom-examples/fom_inventory.md)
- workbench contract:
  - [`fom_workbench.md`](fom_workbench.md)
- validation front door:
  - [`fom_validate.md`](fom_validate.md)

## Current Split

- repo-owned baseline:
  - small curated modules that back examples, parser tests, and default
    round-trip coverage
- third-party public baseline:
  - upstream XML corpora preserved under `third_party/fom_baseline/upstream/`
  - no federate simulations or behavior claims attached
  - family-aware parse/load coverage plus FedPro JSON envelope round-trip

## Edition Classes

Use [`fom-examples/fom_inventory.json`](fom-examples/fom_inventory.json) as the
source of truth for:

- `edition_class`: `2010` | `2025` | `cross-edition`
- `load_mode`: `standalone` | `base-plus-extension` | `ordered-family`
- `baseline_kind`: `repo-owned` | `third-party`
- `scenario_family`

Current intent:

- `2010`:
  - XMLs that are explicitly 2010/Evolved-era baseline artifacts
- `2025`:
  - XMLs that are explicitly 2025-only prototype or test artifacts
- `cross-edition`:
  - XMLs that remain 2010-shaped on disk but are intentionally exercised by
    both 2010 and 2025 route/test flows

## Canonical Checks

- parser/load coverage:
  - `python3 -m pytest -q tests/factories/test_fom_omt_parsing.py`
  - `python3 -m pytest -q tests/factories/test_public_fom_baseline.py`
- bundled round-trip artifact flow:
  - `./tools/fom-roundtrip 2010`
  - `./tools/fom-roundtrip 2025`
- bundled validation flow:
  - `./tools/fom-validate DemoFOMmodule.xml`
  - `./tools/fom-validate packages/hla-rti1516-2025/src/hla/rti1516_2025/resources/foms/Proto2025_Base.xml --edition 2025 --strict-identification`
  - `./tools/fom-validate --family rpr-normative`
  - `./tools/fom-validate DemoFOMmodule.xml TargetRadarFOMmodule.xml --html`

## Notes

- Some imported families are not valid standalone one-file parse units.
- The public baseline manifest records the required family load order.
- For the imported baseline we currently prove:
  - ordered family parse/load
  - FedPro JSON envelope round-trip for the original XML payload
- We do not currently claim:
  - full serializer-normalization parity for every imported corpus
  - runnable example federate scenarios for those third-party FOMs
