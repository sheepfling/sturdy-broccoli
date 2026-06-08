# Requirements Hierarchy

This document is the canonical hierarchy view for the three standards tracked in
this repo:

- `IEEE 1516-2010`: framework and rules
- `IEEE 1516.1-2010`: RTI services and MOM behavior
- `IEEE 1516.2-2010`: OMT schema language and FOM/MIM interchange

Use the hierarchy in this order:

`L1 capability -> L2 feature -> L3 requirement -> positive test, negative test, or planned proof`

The source-of-truth rows still live in `requirements/*.csv`. This page is the
reader-facing index that groups them into capability trees.

## Verification Features

| L1 capability | L2 feature | L3 requirement scope | Test or proof anchor |
| --- | --- | --- | --- |
| Verification package | Requirements and traceability ledgers | `ASSET-CONFORMANCE-MATRIX-001`, `ASSET-REQUIREMENTS-LEDGER-001`, `ASSET-VERIFICATION-TRACEABILITY-001` | `tests/verification/test_service_conformance_matrix_v013.py`, `tests/verification/test_requirements_ledger_v013.py` |
| Verification package | Vendor parity packet | `ASSET-VENDOR-PARITY-PACKET-001` | `tests/scenarios/test_vendor_parity_artifacts.py`, `docs/vendor_parity_artifacts.md` |
| Verification package | Promoted evidence packets | `docs/evidence/*` imported packets | `docs/evidence/README.md`, `docs/evidence/packet_index.md` |

## HLA1516

| L1 capability | L2 feature | L3 requirement scope | Test or proof anchor |
| --- | --- | --- | --- |
| Framework rules | Framework concepts | `HLA1516-FW-001` | `docs/verification/verification_plan.md` |
| Framework rules | Federation and federate rules | `HLA1516-RULE-001` | Planned clause extraction from framework sources |
| Framework rules | Object model concepts | `HLA1516-OBJ-001` | Cross-links into `HLA1516.1` object services and `HLA1516.2` OMT rows |
| Framework rules | Time concepts | `HLA1516-TIME-001` | Cross-links into `HLA1516.1-TM-*` rows |

## HLA1516.1

| L1 capability | L2 feature | L3 requirement scope | Test or proof anchor |
| --- | --- | --- | --- |
| Federation management | Lifecycle services and callbacks | `HLA1516.1-FM-*` | `tests/backends/test_python_backend_federation_extended.py`, `tests/verification/test_requirements_ledger_v013.py` |
| Declaration management | Publication and subscription state | `HLA1516.1-DM-*` | Clause 5 rows plus backend and scenario tests |
| Object management | Discovery update remove and transportation behavior | `HLA1516.1-OM-*` derived slices | `tests/scenarios/test_target_radar_scenario.py`, `tests/backends/*object*` |
| Ownership management | Acquisition divestiture and query behavior | `HLA1516.1-OWN-*` | `tests/backends/test_python_backend_object_ownership_extended.py` |
| Time management | Regulation constrained advance and query behavior | `HLA1516.1-TM-*` | `tests/time/*`, `tests/verification/test_requirements_ledger_v013.py` |
| Data distribution management | Regions dimensions and overlap filtering | `HLA1516.1-DDM-*` | `tests/backends/test_python_backend_time_ddm_extended.py` |
| Support services | Name-handle lookups dimensions ordering transportation and advisory switches | `HLA1516.1-SUP-*` | `tests/backends/test_python_backend_support_services.py` |
| MOM behavior | MOM objects interactions reports and service reporting | `HLA1516.1-MOM-*` | `tests/mom/*`, `tests/verification/test_mom_observer_slice_v013.py`, `tests/verification/test_mom_negative_matrix_executable_v013.py` |

## HLA1516.2

| L1 capability | L2 feature | L3 requirement scope | Test or proof anchor |
| --- | --- | --- | --- |
| OMT schema language | Model identification | `HLA1516.2-ID-*` | Planned parser verification |
| OMT schema language | Object classes | `HLA1516.2-OC-4.2-*` | `tests/factories/test_fom_time_factories.py`, `tests/scenarios/test_startup_sync_fom_java_translation_v09.py` |
| OMT schema language | Interaction classes | `HLA1516.2-IC-4.3-*` | `tests/factories/test_fom_time_factories.py`, `tests/scenarios/test_startup_sync_fom_java_translation_v09.py` |
| OMT schema language | Attributes and parameters | `HLA1516.2-ATTR-4.4-*`, `HLA1516.2-PARAM-4.5-*` | `tests/factories/test_fom_time_factories.py` |
| OMT schema language | Dimensions and time tables | `HLA1516.2-DIM-4.6-*`, `HLA1516.2-DT-4.7-*` | `tests/factories/test_fom_time_factories.py`, `tests/time/test_mom_mim_time_v10.py` |
| OMT schema language | Synchronization tables | `HLA1516.2-SYNC-4.9-001` through `-005` | Planned `fom_parser` / `fom_validator` / `xml_serializer` slice |
| OMT schema language | Transportation tables | `HLA1516.2-TRANS-4.10-001` through `-006` | Planned `fom_parser` / `fom_validator` slice |
| OMT schema language | Update rate designators | `HLA1516.2-URATE-4.11-001` through `-005` | Planned `fom_parser` / `fom_validator` slice |
| OMT schema language | Switch metadata | `HLA1516.2-SWITCH-4.12-001` through `-003` | Planned `fom_parser` / `fom_validator` slice |
| OMT schema language | Datatype system | `HLA1516.2-DT-4.13-001` through `-054` | Planned `fom_parser` / `fom_validator` / `fom_merger` / `xml_serializer` slice |
| OMT schema language | Notes tables | `HLA1516.2-NOTE-4.14-001` through `-003` | Planned parser and serializer fidelity slice |
| FOM and MIM interchange | Standard MIM inclusion and MOM exposure | `HLA1516.2-MIM-D-001` | `tests/time/test_mom_mim_time_v10.py`, `tests/time/test_mom_mim_and_time_semantics_v010.py` |
| FOM module merging | Supported merge subset | `HLA1516.2-OMT-7-001`, `HLA1516.2-OMT-7-002` | Current coarse merge rows in `requirements/hla1516_2_priority_omt.csv` |
| FOM module merging | Detailed merge rules | `HLA1516.2-MERGE-7.0-001` through `-008` | `tests/scenarios/test_startup_sync_fom_java_translation_v09.py`, `tests/backends/test_python_backend_federation_extended.py`, remaining rows planned |
| XML interchange | Schema and semantic round-trip conformance | `HLA1516.2-XML-ANNEX-001` through `-005` | Planned schema validation and serializer slice |

## OMT Scope

- The supported OMT scope in this repo covers FOM modules, SOM modules, the standard MIM, and their merged FDD-style catalog representation.
- The supported interchange scope is the IEEE `1516.2-2010` XML object-model format consumed and emitted by `hla2010/fom.py`.
- The supported proof scope is bounded to parser, schema-validation, merge, and round-trip evidence that exists in the current repo.

## OMT Purpose

- The purpose of the repo's OMT layer is to preserve enough interoperable object-model structure for federates and RTIs to agree on shared object classes, interaction classes, attributes, parameters, datatypes, dimensions, and related metadata.
- The active parser and merge logic treat those object-model artifacts as the common documentation and interchange substrate between federation participants.

## OMT Background

- The OMT layer is implemented as one part of the wider HLA product set tracked in this repo, alongside framework rules in `IEEE 1516-2010` and RTI service behavior in `IEEE 1516.1-2010`.
- Object-model implementation decisions in this repo are intentionally traced from OMT artifacts into runtime capabilities, requirements ledgers, and verification evidence rather than being treated as standalone XML parsing only.

## Implementation Notes

- `mapped` rows are intentionally narrow. They only claim the current
  `hla2010/fom.py` subset and the executable tests that actually exist.
- If a requirement is only defensible through a boundary test, keep that
  boundary explicit rather than collapsing it into a broader parity claim.
- Verification assets such as `ASSET-VENDOR-PARITY-PACKET-001` are repo-level proof capabilities.
  They complement the standards rows, but they are not themselves standards-derived requirement IDs.
- `planned` rows are still useful: they tell you which package should own the work
  next (`fom_parser`, `fom_validator`, `fom_merger`, `mim_loader`,
  `xml_serializer`) and what proof shape is expected.
- The detailed clause rows are in [`requirements/hla1516_2_priority_omt.csv`](../../requirements/hla1516_2_priority_omt.csv).
- The bridge from requirement rows to code and tests is in [`requirements/traceability_matrix.csv`](../../requirements/traceability_matrix.csv).

## OMT Lexicon

The FOM/SOM lexicon is the repo's definitional bridge between OMT tables and executable object-model semantics.

Use these terms consistently in implementation and verification artifacts:

- `FOM module`: a federation object model XML module provided to federation creation or join flows.
- `SOM module`: a simulation object model XML module used for documentation and interface description.
- `MIM`: the standard management and initialization module bundled as `HLAstandardMIM.xml`.
- `Object model`: the generic IEEE 1516.2 container represented by the top-level `objectModel` XML element.
- `FDD`: the merged federation object model representation assembled from the active MIM and FOM modules.

When reading or writing requirement rows, use the lexicon with these expectations:

- Object-class definitions carry the documentation, validation, and traceability meaning of the OMT object tables.
- Interaction-class definitions carry the documentation, validation, and traceability meaning of the OMT interaction tables.
- Attribute definitions carry the documentation, validation, and traceability meaning of the OMT attribute tables.
- Parameter definitions carry the documentation, validation, and traceability meaning of the OMT parameter tables.

## Conformance Claim Boundary

This repo does not claim full IEEE 1516.2-2010 conformance.

The current OMT document conformance labels used in this repo are:

- `conforming`: schema-valid, semantically valid, and fully within the currently supported repo-native OMT subset.
- `partially conforming`: schema-valid and semantically valid, but uses features that the repo currently preserves or reports without executing full runtime semantics.
- `nonconforming`: schema-invalid or semantically invalid on the current parser and validator path.

These OMT document labels are separate from the requirements-harmonization labels used elsewhere in the catalog:

- `mapped`: directly implemented and backed by executable or generated proof.
- `partial`: intentionally narrower than the full standard statement, but backed by current parser, merge, runtime, or documentation evidence.
- `planned`: accepted catalog scope with no direct current proof yet.

- `mapped` requirement rows identify the implemented and executable OMT subset only.
- `planned` requirement rows identify unimplemented, partially implemented, or artifact-only future work.
- Parser and serializer claims are bounded by the implemented `hla2010/fom.py` subset, even when the XML schema contains more optional tables or richer metadata than the runtime currently consumes.

The current requirements-harmonization labels used in this repo are:

- `mapped`: directly implemented and backed by executable or generated proof.
- `partial`: intentionally narrower than the full standard statement, but backed by current parser, merge, runtime, or documentation evidence.
- `planned`: accepted catalog scope with no direct current proof yet.

The OMT verification suite currently includes these proof shapes:

- schema validation
- semantic validation
- reference validation
- merge validation
- parse/serialize round-trip validation

Where `serviceUtilization` is present in a SOM or FOM module, the parser captures it as structured metadata for conformance assessment and traceability.
