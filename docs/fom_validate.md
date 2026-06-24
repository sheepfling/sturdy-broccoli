# FOM Validate

Use this when you need one command that answers:

- does this XML load?
- is it schema-valid on the right edition path?
- does it pass the repo's semantic validator?
- what should I do next if it fails?

## Front Door

- `./tools/fom-validate DemoFOMmodule.xml`
- `./tools/fom-validate TargetRadarFOMmodule.xml`
- `./tools/fom-validate path/to/module.xml --edition 2025 --strict-identification`
- `./tools/fom-validate --family rpr-normative`
- `./tools/fom-validate DemoFOMmodule.xml TargetRadarFOMmodule.xml --html`
- `./tools/fom-schema-baseline`
- `./tools/fom-schema-audit`
- `./tools/fom-siso-audit`

Generated artifacts land under:

- `analysis/fom_validation/fom_validation_report.json`
- `analysis/fom_validation/fom_validation_report.md`
- `analysis/fom_validation/fom_validation_report.html` when `--html` is used

## What It Does

For each XML source the validator reports:

- effective validator path: `2010` or `2025`
- catalog classification when known: `2010`, `2025`, or `cross-edition`
- edition scope: `2010 only`, `2025 only`, `both`, `cross-edition / ambiguous`, or `schema-only / support-only`
- schema result
- parse result
- semantic validation result
- current verdict
- recommended next step

For each multi-module load set it also reports:

- explicit or family-backed load-set membership
- merged parse/merge result
- merged semantic result
- merged structure counts

This separates two ideas that are easy to confuse:

- catalog class:
  - where the XML sits in the repo inventory
- effective edition:
  - which validator path the tool actually used
- edition scope:
  - whether the source belongs to one edition, both editions, or is schema/support-only

That matters for cross-edition files like `TargetRadarFOMmodule.xml`.

## Typical Commands

Validate a repo-known 2010 XML by designator:

```bash
./tools/fom-validate DemoFOMmodule.xml
```

Validate a 2025 XML with stricter identification checks:

```bash
./tools/fom-validate \
  packages/hla-rti1516-2025/src/hla/rti1516_2025/resources/foms/Proto2025_Base.xml \
  --edition 2025 \
  --strict-identification
```

Validate multiple XMLs into one packet:

```bash
./tools/fom-validate DemoFOMmodule.xml TargetRadarFOMmodule.xml
```

Validate an inventory family using its default ordered/base load set:

```bash
./tools/fom-validate --family rpr-normative
```

Generate the local HTML report:

```bash
./tools/fom-validate --family proto2025-message-test --edition 2025 --html
```

Use an explicit 2025 schema:

```bash
./tools/fom-validate path/to/module.xml \
  --edition 2025 \
  --schema docs/requirements/ieee-1516-2025/encoding_auth_work_packet/09-standards-subset/IEEE1516-OMT-2025.xsd
```

## Verdicts

- `conforming`:
  - schema, parse, and semantic validation all passed on the active path
- `partially-conforming`:
  - current schema and parser checks passed, but the XML uses a narrower supported subset
- `nonconforming`:
  - schema and/or semantic validation failed
- `parse-failed`:
  - the XML could not be loaded into the repo-native model

## Load-Set Modes

- explicit load set:
  - you pass multiple XML sources directly on the command line
- family load set:
  - you pass `--family`, and the validator uses the inventory-backed default load set
  - `ordered-family` stays ordered
  - `base-plus-extension` automatically adds the shared base module

## Current Scope

2010 path:

- uses the existing 2010 schema + conformance assessment path
- reports partial-conformance when the repo still treats a feature as a narrower supported subset

2025 path:

- uses the supplied IEEE 1516.2-2025 OMT XSD
- runs the structured semantic validator after parse
- can enforce stricter identification-table checks with `--strict-identification`

Dedicated schema baseline:

- `./tools/fom-schema-baseline` validates the repo's positive XML/XSD pairs
- the baseline currently uses `EncodingSmokeTest-2025.xml` against `IEEE1516-DIF-2025.xsd`
- and `SchemaValidProbe-2025.xml` against `IEEE1516-OMT-2025.xsd`
- keep this lane separate from the parser/merge stress corpus

Schema audit:

- `./tools/fom-schema-audit` runs the positive cases through validator, JSON cycle, and workbench HTML
- it uses the same positive cases as the schema baseline, but exercises the full operator surface
- it also preserves the `Edition Scope` column in every report surface

SISO audit:

- `./tools/fom-siso-audit` runs the high-value SISO families through validator, JSON cycle, and workbench HTML
- it targets RPR 2.0, RPR 3.0, Link 16, Space FOM, standard MIM, and U-FOM when those downloads are present locally
- it also preserves the `Edition Scope` column in every report surface

SISO showcase:

- `./tools/fom-siso-showcase` turns the strongest Link 16, RPR 3.0, and Space FOM packets into a presentable artifact bundle
- it keeps explicit expected buckets such as `validate-clean` and `parse-fail-fast` so the demo story stays honest about template-only versus integrated packets
- it emits validator, JSON cycle, overview, and workbench artifacts for each included packet

## Read Next

- [fom_reading_map.md](fom_reading_map.md)
- [fom_workbench.md](fom_workbench.md)
- [fom-examples/fom_inventory.md](fom-examples/fom_inventory.md)
