# Retired and Legacy Mapping Rows

Source: IEEE 1516.1-2010 to IEEE 1516.1-2025 / IEEE 1516.2-2025 differential
rows that remain `retired/legacy-only` in the canonical 2025 requirement
catalog.

These rows are not active 2025 obligations for the repo's main Python RTI lane.
They exist to keep legacy 2010 spellings and schema tokens from being
miscounted as missing 2025 functionality. The current runtime owner for the
native 2025 behavior is `hla-backend-python1516-2025`. `hla-backend-shim` remains a
compatibility wrapper and is not the runtime owner for these retired rows.

## Owner Surface

- canonical owner doc: `docs/requirements/ieee-1516-2025/retired_legacy_mapping.md`
- primary shard: `unit-foundation`
- widen to: only when the retired mapping changes generated audits or
  downstream projection artifacts
- typical view tags: `2025-core`, `setup-preflight`

## Final Claim Rule

- these rows stay `retired/legacy-only`, not active 2025 support obligations
- do not count candidate 2025 replacements as proof that the retired row itself
  is implemented
- do not promote a retired row to `covered` unless the repo deliberately adds a
  compatibility or migration mode and proves that exact scope directly
- the purpose of this doc is exclusion discipline, not runtime proof expansion

Default final stance:

- this bucket is already in its intended final repo-owned state as an explicit
  exclusion boundary
- no additional runtime proof is required for the repo to keep these rows out
  of active 2025 normative coverage
- future work is optional and should happen only if the repo deliberately opens
  a new compatibility or migration program with its own bounded claim and tests

## Federate Interface Legacy API Rows

| ID | Legacy 2010 spelling | Candidate 2025 replacement |
| --- | --- | --- |
| HLA2025-FI-RET-001 | `disableAttributeRelevanceAdvisorySwitch` | `setAttributeRelevanceAdvisorySwitch` / `getAttributeRelevanceAdvisorySwitch` |
| HLA2025-FI-RET-002 | `disableAttributeScopeAdvisorySwitch` | `setAttributeScopeAdvisorySwitch` / `getAttributeScopeAdvisorySwitch` |
| HLA2025-FI-RET-003 | `disableInteractionRelevanceAdvisorySwitch` | `setInteractionRelevanceAdvisorySwitch` / `getInteractionRelevanceAdvisorySwitch` |
| HLA2025-FI-RET-004 | `disableObjectClassRelevanceAdvisorySwitch` | `setObjectClassRelevanceAdvisorySwitch` / `getObjectClassRelevanceAdvisorySwitch` |
| HLA2025-FI-RET-005 | `enableAttributeRelevanceAdvisorySwitch` | `setAttributeRelevanceAdvisorySwitch` / `getAttributeRelevanceAdvisorySwitch` |
| HLA2025-FI-RET-006 | `enableAttributeScopeAdvisorySwitch` | `setAttributeScopeAdvisorySwitch` / `getAttributeScopeAdvisorySwitch` |
| HLA2025-FI-RET-007 | `enableInteractionRelevanceAdvisorySwitch` | `setInteractionRelevanceAdvisorySwitch` / `getInteractionRelevanceAdvisorySwitch` |
| HLA2025-FI-RET-008 | `enableObjectClassRelevanceAdvisorySwitch` | `setObjectClassRelevanceAdvisorySwitch` / `getObjectClassRelevanceAdvisorySwitch` |
| HLA2025-FI-RET-009 | `getAvailableDimensionsForClassAttribute` | `getAvailableDimensionsForObjectClass` / `getAvailableDimensionsForInteractionClass` |
| HLA2025-FI-RET-010 | `releaseMultipleObjectInstanceName` | `releaseMultipleObjectInstanceNames` |
| HLA2025-FI-RET-011 | `reserveMultipleObjectInstanceName` | `reserveMultipleObjectInstanceNames` |

## OMT Legacy Schema Rows

| ID | Legacy 2010 schema token | Candidate 2025 replacement |
| --- | --- | --- |
| HLA2025-OMT-RET-001 | `conveyProducingFederate` | revised 2025 convey/reporting behavior through switch and service-reporting rows |
| HLA2025-OMT-RET-002 | `disableAttributeRelevanceAdvisorySwitch` | `setAttributeRelevanceAdvisorySwitch` |
| HLA2025-OMT-RET-003 | `disableAttributeScopeAdvisorySwitch` | `setAttributeScopeAdvisorySwitch` |
| HLA2025-OMT-RET-004 | `disableInteractionRelevanceAdvisorySwitch` | `setInteractionRelevanceAdvisorySwitch` |
| HLA2025-OMT-RET-005 | `disableObjectClassRelevanceAdvisorySwitch` | `setObjectClassRelevanceAdvisorySwitch` |
| HLA2025-OMT-RET-006 | `enableAttributeRelevanceAdvisorySwitch` | `setAttributeRelevanceAdvisorySwitch` |
| HLA2025-OMT-RET-007 | `enableAttributeScopeAdvisorySwitch` | `setAttributeScopeAdvisorySwitch` |
| HLA2025-OMT-RET-008 | `enableInteractionRelevanceAdvisorySwitch` | `setInteractionRelevanceAdvisorySwitch` |
| HLA2025-OMT-RET-009 | `enableObjectClassRelevanceAdvisorySwitch` | `setObjectClassRelevanceAdvisorySwitch` |
| HLA2025-OMT-RET-010 | `getAvailableDimensionsForClassAttribute` | `getAvailableDimensionsForObjectClass` / `getAvailableDimensionsForInteractionClass` |
| HLA2025-OMT-RET-011 | `lookahead` | `logicalTime` / `logicalTimeInterval` time representation fields |
| HLA2025-OMT-RET-012 | `removeobjectinstance` | `removeObjectInstance` capitalization and 2025 naming normalization |
| HLA2025-OMT-RET-013 | `timeStamp` | `logicalTime` / `logicalTimeInterval` or service-specific time arguments |

## Bounded Reading

- These 24 rows remain excluded from native 2025 normative coverage unless the
  repo intentionally adds a compatibility or migration mode and tests it.
- The active replacement behavior belongs to the native 2025 service, time, or
  OMT rows already carried by `hla-backend-python1516-2025`.
- The repo should not promote these rows to `covered` merely because a similar
  2025 service exists; promotion would require an explicit compatibility claim
  plus dedicated executable evidence.
- The current Python 2025 RTI may reject these legacy spellings as unsupported
  2025 service or schema names rather than aliasing them silently into native
  conformance.

## Latest Investigated Decision

The retired/legacy-only slice was re-audited on `2026-06-26` against the
current owner doc, canonical requirement rows, grouped projection rows, replacement
mapping notes, and companion closeout evidence artifacts for:

- `HLA2025-FI-RET-001` through `HLA2025-FI-RET-011`
- `HLA2025-OMT-RET-001` through `HLA2025-OMT-RET-013`

Decision:

- keep these rows as `retired/legacy-only`
- do not promote them to standalone `covered`

Reason:

1. the current differential packet, canonical requirement catalog, and grouped
   projection artifacts already establish that
   these are legacy 2010 spellings or schema tokens rather than active native
   2025 obligations
2. the candidate 2025 replacements are already carried by the native 2025 FI,
   time, switch, and OMT rows where applicable, so promoting the retired rows
   would blur replacement behavior with legacy-name compatibility
3. no repo-owned compatibility or migration mode was identified that would
   justify treating these legacy-only rows as directly implemented support
4. converting them now would overclaim compatibility semantics that the repo
   does not currently prove

Current evidence reviewed for this decision included:

- `requirements/2025/canonical_requirements.json`
- `requirements/2025/backend_resolution.json`
- `requirements/2025/harmonization/hla_2025_harmonization_worklist.csv`
- `requirements/2025/harmonization/hla_2025_requirement_coverage_rollup.json`
- `docs/requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md`
- `tests/requirements/test_2025_tail_backlog_evidence.py`

Operational effect:

- the retired slice remains a maintained explicit exclusion boundary
- the active closeout queue should advance only if the repo intentionally
  starts a compatibility or migration program for one or more legacy rows

## Exit Condition

Treat this bucket as closed for current closeout purposes when all of these are
true:

1. all 24 retired rows remain anchored to this owner doc and the row-level
   canonical requirement catalog
2. the final claim language keeps them explicit as exclusions rather than
   accidental coverage gaps
3. any future widening must happen through canonical requirement rows or the
   backend-resolution companion, never through grouped worklists, audit notes,
   or other downstream reporting views

Only reopen this bucket if the repo intentionally starts a compatibility or
migration program for one or more retired rows.
