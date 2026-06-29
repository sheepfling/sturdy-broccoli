# 2025 Python RTI 100 Percent Worklist

Use this note when the question is:

- what exact rows still block an honest `100%` outcome for the `2025` Python
  RTI lane?
- what denominator should the repo use?
- which rows are real direct-support targets versus explicit exclusions or
  umbrella decomposition candidates?

This note is the concrete execution companion to
[`PLN-004_python_rti_100_percent_compliance_plan.md`](PLN-004_python_rti_100_percent_compliance_plan.md).

## Recommended Metric Rule

Use this metric split:

1. `100% dispositioned` across all tracked `2025` rows
2. `100% covered` across active normative non-retired non-umbrella rows
3. separate reporting for:
   - `duplicate/umbrella`
   - `retired/legacy-only`
   - bounded backend-resolution or route surfaces

Current canonical 2025 requirement catalog counts:

- total tracked rows: `691`
- directly `covered`: `645`
- `duplicate/umbrella`: `22`
- `retired/legacy-only`: `24`

That means the current recommended active denominator is:

- active normative non-retired non-umbrella rows: `645`
- current direct coverage on that denominator: `645 / 645 = 100%`

Do not report `691 / 691 covered` unless the repo deliberately funds:

- standalone proof decomposition for the `22` umbrella rows
- explicit compatibility or migration proof for the `24` retired rows

## Row-Class Decision Rule

Treat the remaining `46` non-covered rows in one of two ways:

1. keep them outside the direct-support denominator with explicit policy and
   owner docs
2. deliberately convert them into direct-support targets and add narrower
   executable proof for each row

Recommended current rule:

- keep framework and callback/configuration/binding umbrella rows as
  non-standalone rows unless leadership wants literal `691 / 691 covered`
- keep retired or legacy-only rows excluded unless leadership wants a formal
  compatibility or migration program

## Current Non-Covered Row Inventory

### `duplicate/umbrella` rows: `22`

These are currently owned by:

- [`../requirements/ieee-1516-2025/framework_rules.md`](../requirements/ieee-1516-2025/framework_rules.md)
- [`../requirements/ieee-1516-2025/callback_binding_deltas.md`](../requirements/ieee-1516-2025/callback_binding_deltas.md)

#### Framework umbrella rows: `10`

These `10` rows are already owned by
[`../requirements/ieee-1516-2025/framework_rules.md`](../requirements/ieee-1516-2025/framework_rules.md)
as non-standalone umbrella rows.
Under the current honest-closeout reading, they are maintained boundary rows,
not active direct-support targets.

| Requirement ID | Service or check | Current role | Backend resolution now | Current closeout reading | To make it direct `covered` |
| --- | --- | --- | --- | --- | --- |
| `HLA2025-FR-001` | `Federation FOM` | `framework-umbrella` | direct `python1516_2025` runtime plus FOM/OMT tooling; no alternate backend owner | re-audited on `2026-06-26`; maintained FOM/OMT umbrella boundary | prove it as a standalone framework row instead of a child-OMT summary |
| `HLA2025-FR-002` | `Federate-held object state` | `framework-umbrella` | direct `python1516_2025` runtime owner; hosted route evidence only where linked child rows use it | re-audited on `2026-06-26`; maintained federate-owned object-state umbrella boundary | prove it as a standalone rule instead of an object-service summary |
| `HLA2025-FR-003` | `RTI-mediated FOM data exchange` | `framework-umbrella` | direct `python1516_2025` runtime plus bounded hosted FedPro route proof; not a second RTI lane | re-audited on `2026-06-26`; maintained RTI-mediated exchange umbrella boundary | prove it as a standalone rule instead of a child FI summary |
| `HLA2025-FR-004` | `FI-conformant RTI interaction` | `framework-umbrella` | direct `python1516_2025` runtime owner plus wrapper-only Java/C++ binding surfaces | re-audited on `2026-06-26`; maintained FI-surface umbrella boundary | prove it as a standalone rule instead of a child FI summary |
| `HLA2025-FR-005` | `Single-owner instance attributes` | `framework-umbrella` | direct `python1516_2025` runtime owner; other backends remain separate vendor-resolution questions | re-audited on `2026-06-26`; maintained ownership cardinality umbrella boundary | prove it as a standalone rule instead of an ownership-service summary |
| `HLA2025-FR-006` | `Federate SOM` | `framework-umbrella` | documentation and tooling owner over the main `python1516_2025` lane; no standalone backend claim | re-audited on `2026-06-26`; maintained SOM documentation umbrella boundary | prove it as a standalone rule instead of a documentation or child summary |
| `HLA2025-FR-007` | `SOM-declared data exchange capability` | `framework-umbrella` | direct `python1516_2025` runtime plus scenario proof; no alternate backend owner | re-audited on `2026-06-26`; maintained SOM data-exchange umbrella boundary | prove it as a standalone rule instead of a child FI or scenario summary |
| `HLA2025-FR-008` | `SOM-declared ownership capability` | `framework-umbrella` | direct `python1516_2025` runtime owner; hosted replay only where child ownership rows cite it | re-audited on `2026-06-26`; maintained SOM ownership umbrella boundary | prove it as a standalone rule instead of an ownership child summary |
| `HLA2025-FR-009` | `SOM-declared update conditions` | `framework-umbrella` | direct `python1516_2025` runtime owner; wrapper or hosted evidence is only secondary if linked child rows require it | re-audited on `2026-06-26`; maintained update-condition umbrella boundary | prove it as a standalone rule instead of an update-condition child summary |
| `HLA2025-FR-010` | `Local time management` | `framework-umbrella` | direct `python1516_2025` runtime plus bounded hosted FedPro replay; not an alternate backend owner | re-audited on `2026-06-26`; maintained local-time umbrella boundary | prove it as a standalone rule instead of a child time-management summary |

Latest investigated no-convert result for the framework-umbrella class:

- on `2026-06-26`, the full framework slice was re-audited against its owner
  doc, canonical requirement catalog, child-row map, and executable anchors
- the current result is to keep those rows as `duplicate/umbrella`
- they should not be treated as the next direct-support backlog unless the
  repo deliberately wants literal `691 / 691 covered`
- use
  [`2025_python_rti_umbrella_decomposition_worklist.md`](2025_python_rti_umbrella_decomposition_worklist.md)
  for the exact child-row map and no-convert rationale

#### Callback/configuration/binding delta rows: `12`

These `12` rows are already owned by
[`../requirements/ieee-1516-2025/callback_binding_deltas.md`](../requirements/ieee-1516-2025/callback_binding_deltas.md)
as non-standalone umbrella rows.
Under the current honest-closeout reading, they are maintained boundary rows,
not active direct-support targets.

| Requirement ID | Service or check | Current role | Backend resolution now | Current closeout reading | To make it direct `covered` |
| --- | --- | --- | --- | --- | --- |
| `HLA2025-FI-CB-001` | `Callback model selection` | `delta-umbrella` | direct `python1516_2025` runtime owner plus bounded hosted route replay | maintained non-standalone callback/configuration umbrella row | split or prove it as a direct callback-model row |
| `HLA2025-FI-CB-002` | `Evoke Callback` | `delta-umbrella` | direct `python1516_2025` runtime owner; Java/C++ are wrapper-only route surfaces | maintained non-standalone callback/control umbrella row | split or prove it as a direct callback row |
| `HLA2025-FI-CB-003` | `Evoke Multiple Callbacks` | `delta-umbrella` | direct `python1516_2025` runtime owner; Java/C++ are wrapper-only route surfaces | maintained non-standalone callback/control umbrella row | split or prove it as a direct callback row |
| `HLA2025-FI-CB-004` | `Enable/Disable Callbacks` | `delta-umbrella` | direct `python1516_2025` runtime owner plus bounded hosted route replay | maintained non-standalone callback/control umbrella row | split or prove it as a direct callback-control row |
| `HLA2025-FI-CB-005` | `Federate Resigned callback` | `delta-umbrella` | direct `python1516_2025` runtime owner plus hosted replay where linked child proof uses it | maintained non-standalone callback/reporting umbrella row | split or prove it as a direct callback row |
| `HLA2025-FI-CB-006` | `Federation execution member reporting` | `delta-umbrella` | direct `python1516_2025` runtime owner plus hosted replay where linked child proof uses it | maintained non-standalone callback/reporting umbrella row | split or prove it as a direct reporting row |
| `HLA2025-FI-CB-007` | `Directed interaction callback parameterization` | `delta-umbrella` | direct `python1516_2025` runtime plus bounded hosted FedPro route parity; not a second backend owner | re-audited on `2026-06-26`; maintained directed-interaction umbrella boundary | split or prove it as a direct callback-parameter row |
| `HLA2025-FI-CB-008` | `Flush Queue Grant callback` | `delta-umbrella` | direct `python1516_2025` runtime owner plus hosted replay where linked child proof uses it | maintained non-standalone time-callback umbrella row | split or prove it as a direct time callback row |
| `HLA2025-FI-CFG-001` | `Configuration and additional settings result` | `delta-umbrella` | direct `python1516_2025` runtime owner; hosted route only carries bounded request-shape replay | re-audited on `2026-06-26`; maintained configuration umbrella boundary | split or prove it as a direct configuration row |
| `HLA2025-FI-AUTH-001` | `Authorization credentials` | `delta-umbrella` | direct `python1516_2025` runtime owner; hosted route only carries bounded request-shape replay | re-audited on `2026-06-26`; maintained authorization umbrella boundary | split or prove it as a direct authorization row |
| `HLA2025-BIND-FEDPRO-001` | `FedPro protocol split` | `delta-umbrella` | bounded hosted FedPro route over `hla-backend-python1516-2025`; not an independent RTI owner | re-audited on `2026-06-26`; maintained bounded hosted-route umbrella boundary | split or prove it as a direct hosted-protocol row |
| `HLA2025-BIND-JAVA-CPP-001` | `Java/C++ binding split` | `delta-umbrella` | wrapper-only Java/C++ binding surfaces over the direct `python1516_2025` runtime; no alternate RTI owner | re-audited on `2026-06-26`; maintained binding-capability umbrella boundary | split or prove it as a direct binding row |

Latest investigated no-convert result for the delta-umbrella class:

- on `2026-06-26`, the callback-control slice, directed-interaction slice,
  configuration/auth slice, FedPro protocol slice, and Java/C++ binding slice
  were re-audited against their owner doc and executable anchors
- the current result is to keep those rows as `duplicate/umbrella`
- they should not be treated as the next direct-support backlog unless the
  repo deliberately wants literal `691 / 691 covered`
- use
  [`2025_python_rti_umbrella_decomposition_worklist.md`](2025_python_rti_umbrella_decomposition_worklist.md)
  for the exact child-row map and no-convert rationale

### `retired/legacy-only` rows: `24`

These are currently owned by:

- [`../requirements/ieee-1516-2025/retired_legacy_mapping.md`](../requirements/ieee-1516-2025/retired_legacy_mapping.md)

These `24` rows are already owned by
[`../requirements/ieee-1516-2025/retired_legacy_mapping.md`](../requirements/ieee-1516-2025/retired_legacy_mapping.md)
as explicit exclusion rows.
Under the current honest-closeout reading, they are maintained exclusion
boundaries, not active direct-support targets.

#### Federate Interface legacy API rows: `11`

| Requirement ID | Legacy spelling | Backend resolution now | To make it direct `covered` |
| --- | --- | --- | --- |
| `HLA2025-FI-RET-001` | `disableAttributeRelevanceAdvisorySwitch` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |
| `HLA2025-FI-RET-002` | `disableAttributeScopeAdvisorySwitch` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |
| `HLA2025-FI-RET-003` | `disableInteractionRelevanceAdvisorySwitch` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |
| `HLA2025-FI-RET-004` | `disableObjectClassRelevanceAdvisorySwitch` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |
| `HLA2025-FI-RET-005` | `enableAttributeRelevanceAdvisorySwitch` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |
| `HLA2025-FI-RET-006` | `enableAttributeScopeAdvisorySwitch` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |
| `HLA2025-FI-RET-007` | `enableInteractionRelevanceAdvisorySwitch` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |
| `HLA2025-FI-RET-008` | `enableObjectClassRelevanceAdvisorySwitch` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |
| `HLA2025-FI-RET-009` | `getAvailableDimensionsForClassAttribute` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |
| `HLA2025-FI-RET-010` | `releaseMultipleObjectInstanceName` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |
| `HLA2025-FI-RET-011` | `reserveMultipleObjectInstanceName` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |

#### OMT legacy schema rows: `13`

| Requirement ID | Legacy schema token | Backend resolution now | To make it direct `covered` |
| --- | --- | --- | --- |
| `HLA2025-OMT-RET-001` | `conveyProducingFederate` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |
| `HLA2025-OMT-RET-002` | `disableAttributeRelevanceAdvisorySwitch` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |
| `HLA2025-OMT-RET-003` | `disableAttributeScopeAdvisorySwitch` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |
| `HLA2025-OMT-RET-004` | `disableInteractionRelevanceAdvisorySwitch` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |
| `HLA2025-OMT-RET-005` | `disableObjectClassRelevanceAdvisorySwitch` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |
| `HLA2025-OMT-RET-006` | `enableAttributeRelevanceAdvisorySwitch` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |
| `HLA2025-OMT-RET-007` | `enableAttributeScopeAdvisorySwitch` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |
| `HLA2025-OMT-RET-008` | `enableInteractionRelevanceAdvisorySwitch` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |
| `HLA2025-OMT-RET-009` | `enableObjectClassRelevanceAdvisorySwitch` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |
| `HLA2025-OMT-RET-010` | `getAvailableDimensionsForClassAttribute` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |
| `HLA2025-OMT-RET-011` | `lookahead` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |
| `HLA2025-OMT-RET-012` | `removeobjectinstance` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |
| `HLA2025-OMT-RET-013` | `timeStamp` | no active 2025 backend owner; explicit legacy-only exclusion | implement compatibility or migration behavior and test it directly |

Latest investigated no-convert result for the retired/legacy-only class:

- on `2026-06-26`, the full retired/legacy slice was re-audited against its
  owner doc, canonical requirement catalog, generated grouped projections, and
  finish-line evidence surfaces
- the current result is to keep those rows as `retired/legacy-only`
- they should not be treated as the next direct-support backlog unless the
  repo deliberately wants a real compatibility or migration program
- use [`../requirements/ieee-1516-2025/retired_legacy_mapping.md`](../requirements/ieee-1516-2025/retired_legacy_mapping.md)
  for the exact exclusion rationale and candidate 2025 replacement map

## Recommended Work Sequence

### Lowest-risk honest path

1. freeze the official metric as `100% covered on the 645 active normative
   non-retired non-umbrella rows`
2. keep the `46` rows above explicit and separate
3. update exports and executive summaries to carry both percentages

### Literal `691 / 691 covered` path

1. decompose or directly prove the `22` umbrella rows
2. implement and test compatibility or migration scope for the `24` retired
   rows
3. update owner docs, canonical catalogs or backend-resolution companions,
   finish-line packets, and exports together

## Vendor Update Rule

If any row above changes because the Python RTI lane grows:

1. inspect `Pitch`, `CERTI`, and `Portico` companion artifacts for the same
   family
2. refresh the generated backend and vendor disposition packets
3. keep vendor rows explicit when Python support broadens faster than vendor
   support

## Related Docs

- [PLN-004_python_rti_100_percent_compliance_plan.md](PLN-004_python_rti_100_percent_compliance_plan.md)
- [2025_requirement_by_requirement_audit.md](2025_requirement_by_requirement_audit.md)
- [requirements_completion_audit.md](requirements_completion_audit.md)
- [../requirements/ieee-1516-2025/framework_rules.md](../requirements/ieee-1516-2025/framework_rules.md)
- [../requirements/ieee-1516-2025/callback_binding_deltas.md](../requirements/ieee-1516-2025/callback_binding_deltas.md)
- [../requirements/ieee-1516-2025/retired_legacy_mapping.md](../requirements/ieee-1516-2025/retired_legacy_mapping.md)
