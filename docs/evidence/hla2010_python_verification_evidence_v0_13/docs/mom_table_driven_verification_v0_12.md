# MOM table-driven exposure and verification slice v0.12

Version 0.12 moves the pure Python RTI away from hard-coded MOM report tables and toward a model derived from the active merged MIM/FOM catalog.

## Implemented in this slice

- `hla.fom.mom_catalog.MOMExposureModel` is built from `FOMCatalog` after the standard MIM is loaded.
- The model records MOM object classes, interaction classes, request/report pairs, RTI-send/RTI-receive direction, inherited parameters, declared parameters, required parameters, switch-choice parameters, and compatibility aliases.
- `PythonRTIBackend.current_mom_summary()` exposes `mom_interaction_matrix` and `mom_object_matrix` so tests and humans can inspect what the active FDD says.
- Strict MOM processing now has executable tests for missing required parameters, invalid boolean payloads, and attempts by a federate to send RTI-report interactions.
- The generated negative-path matrix covers every RTI-received MOM leaf interaction.

## Current catalog counts

| Item | Count |
|---|---:|
| MOM object classes | 3 |
| MOM interaction classes | 84 |
| Request/report pairs | 13 |
| RTI-received MOM leaves | 53 |
| RTI-sent MOM leaves | 21 |
| Negative-matrix receive leaves | 53 |

## Focused test evidence

`tests/test_mom_catalog_validation_v012.py` covers:

1. catalog-driven MOM exposure and validation matrix shape;
2. exact MIM parameter names in a MOM report payload;
3. strict missing-required-parameter reporting;
4. strict invalid boolean payload reporting;
5. rejection/reporting when a federate tries to send an RTI report interaction.

Full validation result in this runtime: `66 passed, 2 skipped`.

## Known limits

This is still a development/reference RTI. MOM reports are now catalog-shaped, but not every specialized MOM report payload has complete normative contents. The negative matrix is generated for all RTI-received leaves, but exhaustive parameterized execution is planned for a later slice.
