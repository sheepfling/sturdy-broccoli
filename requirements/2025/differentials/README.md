# HLA 1516.1-2025 differential packets

This directory contains the 2025-vs-2010 differential packets that seed the
2025 requirements backlog and Python RTI implementation plan.

## Files

- `HLA_1516_2025_vs_2010_Differential_Set.csv`: 1,162 row surface
  comparison across OMT service utilization, Java API, MIM, XML/OMT, and
  related requirement surfaces.
- `HLA_1516_2025_vs_2010_Code_Reuse_Disposition.csv`: 22 row code reuse
  disposition guide for deciding whether 2010 code should move into common
  core, stay behind version adapters, become a 2025-only module, or remain
  legacy-only.

## Import summary

Differential rows by `reuse_action`:

| Reuse action | Rows |
| --- | ---: |
| Carry forward | 664 |
| Add | 214 |
| Modify | 120 |
| Carry forward with reference update | 94 |
| Retire or map | 52 |
| Map existing requirement | 6 |
| Modify exception requirement | 6 |
| Map existing XML requirement | 4 |
| Retire or replace | 1 |
| Modify binding references | 1 |

Differential rows by high-volume `service_group`:

| Service group | Rows |
| --- | ---: |
| MIM | 373 |
| XML/OMT | 328 |
| Java RTIambassador | 190 |
| Support Services | 68 |
| Java FederateAmbassador | 60 |
| Federation Management | 34 |
| Object Management | 33 |
| Time Management | 25 |
| Ownership Management | 18 |
| Declaration Management | 16 |

Code reuse disposition rows:

| Disposition | Rows |
| --- | ---: |
| Reuse with adapter or light edits | 6 |
| Keep separate 2025 module | 5 |
| Keep separate version adapter | 4 |
| Retire or legacy-only | 4 |
| Reuse directly in common core | 3 |

## Initial implementation slice

The first executable 2025 runtime slice is federation discovery:

- `listFederationExecutions` / `reportFederationExecutions`
- `listFederationExecutionMembers` / `reportFederationExecutionMembers`
- `reportFederationExecutionDoesNotExist`

This slice is 2025-native because member discovery is a new 2025 federation
management surface, while federation execution listing is a same-name behavior
that can carry forward with updated package and data-record bindings.

The shim implementation is intentionally not a conformance claim for the full
RTI. Unsupported 2025 services still raise an explicit `RTIinternalError` until
their requirement and behavior tests are added.
