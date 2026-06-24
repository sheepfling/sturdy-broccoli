# Retired and Legacy Mapping Rows

Source: IEEE 1516.1-2010 to IEEE 1516.1-2025 / IEEE 1516.2-2025 differential
rows that remain `retired/legacy-only` in the harmonization ledger.

These rows are not active 2025 obligations for the repo's main Python RTI lane.
They exist to keep legacy 2010 spellings and schema tokens from being
miscounted as missing 2025 functionality. The current runtime owner for the
native 2025 behavior is `hla-backend-python1516-2025`. `hla-backend-shim` remains a
compatibility wrapper and is not the runtime owner for these retired rows.

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
