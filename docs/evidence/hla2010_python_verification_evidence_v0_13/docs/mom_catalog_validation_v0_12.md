# v0.12 MOM catalog validation and verification planning

Section anchors: IEEE 1516.1-2010 §11.1-§11.6 and Annex G.

## What changed

v0.12 moves MOM exposure closer to a table-driven implementation.  The pure Python RTI now builds a `MOMExposureModel` from the active merged `FOMCatalog`, which includes the bundled `HLAstandardMIM.xml` plus any joined FOM modules.  That model now drives object attributes, interaction parameters, RTI send/receive direction, request/report pairing, parameter aliases, required/optional parameter rules, at-least-one switch rules, and generated negative-case planning.

The FOM parser now records OMT `dataType` designators for attributes and parameters.  MOM validation uses those datatypes when available, with small name-based fallbacks for extension/development FOMs.

## Spec-linked behavior added

| Area | Section anchor | v0.12 behavior |
|---|---:|---|
| MOM constructs predefined in FDD | §11.1 | The runtime model is derived from the active FDD/MIM catalog, not only from hand-coded constants. |
| MOM object exposure | §11.2 | MOM object rules include inherited/declarative attributes and datatype metadata. |
| MOM interaction direction | §11.3 | Leaf `HLAadjust`, `HLArequest`, and `HLAservice` classes are RTI-received; leaf `HLAreport` classes are RTI-sent. Strict mode rejects federate-sent report classes. |
| Normal MOM administration | §11.4.1 | RTI reports are filtered to exactly the report parameters in the active MIM rule. Strict incoming validation checks unknown, missing, duplicate, choice, bad-encoding, and bad-handle cases. |
| Service reporting conflict | §11.5 | `HLAsetServiceReporting` is handled as its own MIM interaction and uses the service-reporting subscription conflict rule. |
| MOM tables / Annex G | §11.6 / Annex G | The catalog matrix and negative matrix are generated from the bundled standard MIM and kept as verification assets. |

## Current metrics

| Metric | Value |
|---|---:|
| MOM object classes modeled | 3 |
| MOM interaction classes modeled | 84 |
| Request/report pairs detected | 13 |
| RTI-received leaf MOM interactions | 53 |
| RTI-sent leaf MOM interactions | 21 |
| Planned strict negative MOM cases | 269 |
| Test result after this slice | 66 passed, 2 skipped |

## New negative-path coverage

The new `tests/test_mom_catalog_validation_v012.py` checks that:

1. the standard MIM drives the catalog names and datatypes, including `HLAsetServiceReporting` and `HLAreportingState`;
2. `HLArequestMIMdata` produces a report containing exactly the MIM-defined `HLAMIMdata` parameter;
3. strict mode reports and raises for a missing required MOM parameter;
4. strict mode reports and raises for a malformed boolean payload while leaving state unchanged;
5. strict mode rejects a federate-sent `HLAreportServiceInvocation` interaction.

## Verification asset plan

The machine-readable plan is in `analysis/verification_asset_plan_v0_12.json`.  The most important next verification assets are:

1. a Table 15/Table 17 NULL-response conformance suite for every MOM request/report pair;
2. a Table 4/5/6/7 parity extractor that compares the bundled MIM/FOM catalog with the MOM tables in the specification;
3. a service-action crosswalk showing every `HLAmanager.HLAfederate.HLAservice.*` leaf and whether it maps to a Python RTI service handler;
4. a vendor RTI comparison run through JPype/Py4J using the same MOM tests;
5. save/restore + MOM state tests covering §11.4.2 allowed MOM interactions during save/restore.

## Honest status

This is meaningful progress toward compliance, but it is not a certified RTI.  The strongest parts of this slice are catalog-driven MOM naming, report filtering, direction validation, and strict parameter validation.  The weakest parts remain full NULL-response semantics, all service-action mappings, full MOM DDM region behavior, and real-vendor Java RTI comparison.
