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
- optional local SISO DataFiles corpus:
  - `artifacts/siso_downloads/`
  - `python3 scripts/generate_siso_inventory.py`
- dedicated schema-validation baseline:
  - `third_party/fom_schema_baseline/`
  - `./tools/fom-schema-baseline`
- schema-positive audit:
  - `./tools/fom-schema-audit`
- high-value SISO audit:
  - `./tools/fom-siso-audit`
- high-value SISO showcase:
  - `./tools/fom-siso-showcase`
- runtime-backed SISO showcase:
  - [`fom_siso_runtime_showcase.md`](fom_siso_runtime_showcase.md)
- RPR-specific standards feedback log:
  - [`rpr_siso_feedback_log.md`](rpr_siso_feedback_log.md)
- RPR datatype normalization note:
  - [`rpr_type_normalization_notes.md`](rpr_type_normalization_notes.md)
- edition/classification inventory:
  - [`fom-examples/fom_inventory.json`](fom-examples/fom_inventory.json)
  - [`fom-examples/fom_inventory.md`](fom-examples/fom_inventory.md)
  - [`fom-examples/proto2025-v0.1/README.md`](fom-examples/proto2025-v0.1/README.md)
  - inventory and report surfaces now also carry `edition_scope`
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
- local SISO DataFiles corpus:
  - discovered from `artifacts/siso_downloads/` when present
  - automatically folded into `inventory_records()`, validation families, workbench snapshots, and parser stress runs
  - generated inventory files live next to the downloads when you run `python3 scripts/generate_siso_inventory.py`
  - default stress/workbench scope is trimmed to the high-value families: RPR 2.0, RPR 3.0, Space FOM, standard MIM, and U-FOM

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

Scope labels used across reports:

- `2010 only`
- `2025 only`
- `both`
- `cross-edition / ambiguous`
- `schema-only / support-only`

## Canonical Checks

- parser/load coverage:
  - `python3 -m pytest -q tests/factories/test_fom_omt_parsing.py`
  - `python3 -m pytest -q tests/factories/test_public_fom_baseline.py`
- bundled round-trip artifact flow:
  - `./tools/fom-roundtrip 2010`
  - `./tools/fom-roundtrip 2025`
- public baseline stress flow:
  - `./tools/fom-stress`
  - `./tools/fom-stress --refresh-baseline`
  - the report now annotates each family with a stress lane such as `modular-load-merge`, `roundtrip-stress`, or `runtime-federate-scenarios`
- bundled validation flow:
  - `./tools/fom-validate DemoFOMmodule.xml`
  - `./tools/fom-validate packages/hla-rti1516-2025/src/hla/rti1516_2025/resources/foms/Proto2025_Base.xml --edition 2025 --strict-identification`
  - `./tools/fom-validate --family rpr-normative`
  - `./tools/fom-validate DemoFOMmodule.xml TargetRadarFOMmodule.xml --html`
- schema-positive validation flow:
  - `./tools/fom-schema-baseline`
- schema-positive audit flow:
  - `./tools/fom-schema-audit`
- high-value SISO audit flow:
  - `./tools/fom-siso-audit`
- high-value SISO showcase flow:
  - `./tools/fom-siso-showcase`
  - [`fom_siso_showcase.md`](fom_siso_showcase.md)

## Notes

- Some imported families are not valid standalone one-file parse units.
- The public baseline manifest records the required family load order.
- For the imported baseline we currently prove:
  - ordered family parse/load
  - FedPro JSON envelope round-trip for the original XML payload
- For the optional SISO corpus we prove the same parser/load and round-trip behaviors when the downloads are present locally.
- The repo now distinguishes test intent explicitly:
  - `template-fail-fast`
  - `modular-load-merge`
  - `roundtrip-stress`
  - `schema-lane`
  - `runtime-federate-scenarios`
  - `showcase-packets`
- The showcase surface turns the strongest of those packets into a presentable narrative with workbench-backed custom load sets and expected outcome buckets.
- RPR complaints and clarification requests that should flow back to SISO
  belong in [`rpr_siso_feedback_log.md`](rpr_siso_feedback_log.md), not as
  silent family-specific assumptions in generic parser/runtime code.
- Parser architecture and the proposed “stop using RPR-owned type labels for
  generic structure” substitutions are documented in
  [`rpr_type_normalization_notes.md`](rpr_type_normalization_notes.md).
- We do not currently claim:
  - full serializer-normalization parity for every imported corpus
  - runnable example federate scenarios for every third-party FOM packet
