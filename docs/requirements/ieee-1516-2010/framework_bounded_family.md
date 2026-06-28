# 2010 Framework Bounded Family

Use this page when the question is:

- which single document owns the remaining 2010 framework and architecture
  partial surface?
- why does the framework ledger still carry `partial` rows even though the repo
  already has strong executable evidence for declaration, object, ownership,
  time, DDM, MOM, and OMT-adjacent behavior?
- how should reviewers read those framework rows without pretending they are
  ordinary executable service gaps?

Short answer:

- the framework owner ledger is intentionally still partial
- the remaining rows are broad architectural, conceptual, SOM, and rationale
  statements that compress more than the current executable slices can honestly
  prove directly
- this page is the canonical bounded reading for those residual framework rows

## Owner Surface

- canonical owner doc:
  `docs/requirements/ieee-1516-2010/framework_bounded_family.md`
- canonical source owner:
  `requirements/2010/hla1516_framework_detailed_reconciliation.csv`
- broad bridge:
  `requirements/2010/traceability_matrix.csv`
- imported-master companion:
  `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`
- export and handoff surface:
  `docs/verification/requirement_compliance_exports.md`
- primary shard:
  - `unit-foundation`
- wider views only when needed:
  - `./tools/test-focus run backends`
  - `./tools/test-surface run unit-scenarios-light`
  - `./tools/test-surface run unit-fom-tooling`

## Final Claim Rule

- keep framework rows `partial` when the imported statement is broader than the
  directly isolated runtime, parser, or documentation evidence the repo
  actually owns today
- do not relabel these rows as executable service debt when their remaining gap
  is conceptual breadth, federate-local SOM framing, or rationale granularity
- do not promote a framework row to `mapped` merely because nearby Clause 5
  through Clause 10 service families are strongly covered
- widen any framework claim only by adding direct evidence for the broader
  architectural statement itself, not by inferring upward from clause-level
  tests

## Default Final Stance

- this owner note is the canonical final reading for the current `CAP-FW`
  family
- the framework ledger remains intentionally partial because its residual rows
  are broader than the directly executable proof surface
- the framework family is not blocked on plan prose or closeout packets; it is
  bounded by honest evidence scope
- future work should either add direct architectural witnesses or keep these
  rows partial with this explicit reading

## Exit Condition

Treat this bucket as closed for documentation ownership and closeout-surface
purposes unless one of these becomes true:

1. the repo adds direct architectural, federate-SOM, or rationale witnesses
   that justify promoting one or more current framework rows
2. the framework ledger stops being the right canonical location for these
   broad architectural statements
3. the row groupings below stop matching the real evidence clusters

If none of those happen, preserve the current bounded family reading and do not
reframe the residual framework rows as vague or unowned.

## Current Family Shape

The current owner ledger has `53` framework packet rows:

- `12 mapped`
- `41 partial`

The remaining `41 partial` rows cluster into stable categories:

- `12 FW_RULE_DETAIL`
- `21 DET`
- `8 partial`

## What The Categories Mean

### Framework rule detail rows

The `FW_RULE_DETAIL` rows are broad architecture statements such as:

- product-set scope and purpose
- RTI-owned versus federate-owned state separation
- RTI-mediated exchange responsibility
- standard interface framing
- SOM role and publish or subscribe architecture
- ownership, time, compliance, and rationale framing

Current evidence anchors those directions, but not every implied consequence of
those broad framework statements is directly isolated today.

### Detail rows

The `DET` rows break the framework rules into narrower supporting statements,
but many still remain broader than the current direct proof set. Typical
examples include:

- `HLA1516-FW-5_2-DET-001` through `HLA1516-FW-5_2-DET-003`
  because ownership and MOM tests prove the RTI-owned versus federate-owned
  split, but not every full framework implication
- `HLA1516-FW-5_3-DET-001` through `HLA1516-FW-5_3-DET-004`
  because exchange and declaration routing are directly exercised, but the
  broader federate-responsibility framing is still wider than the direct
  witnesses
- `HLA1516-FW-6_1-DET-001` through `HLA1516-FW-6_5-DET-002`
  because OMT parsing, SOM fixtures, publish or subscribe routing,
  ownership-transfer behavior, update-rate metadata, and time helpers are all
  present, while the federate-local SOM and capability statements remain
  broader than what those tests alone can claim exhaustively

### Umbrella framework rows

The `partial` rows such as `HLA1516-RULE-002`, `HLA1516-RULE-003`,
`HLA1516-RULE-004`, `HLA1516-RULE-006`, `HLA1516-RULE-007`,
`HLA1516-RULE-008`, `HLA1516-RULE-009`, and `HLA1516-RULE-010` are umbrella
rules that intentionally stay partial until the broader architectural claim has
direct owner-level evidence rather than only adjacent clause-level support.

## What Is Already Proved

The current repo directly proves substantial parts of the framework-adjacent
surface, including:

- RTI-owned versus federate-owned state distinctions through ownership and MOM
  witnesses
- RTI-mediated exchange and declaration-driven routing
- large portions of the standard federate-interface signature surface
- OMT and SOM parsing support on maintained fixtures
- publish or subscribe, ownership-transfer, and time-coordination behavior that
  these framework rows reference indirectly

Primary evidence anchors:

- `tests/verification/test_framework_rule_docs_v1_0.py`
- `tests/backends/test_python_backend_object_ownership_extended.py`
- `tests/backends/test_python_backend_time_ddm_extended.py`
- `tests/factories/test_fom_omt_parsing.py`
- `tests/mom/test_mom_catalog_validation_v012.py`
- `requirements/2010/traceability_matrix.csv`

## Good Reading

Good reading:

- the framework family is intentionally partial because the remaining rows are
  broad architectural statements
- clause-level runtime proof exists for many neighboring behaviors without
  automatically closing the broader framework wording
- this page is the canonical explanation for why those residual rows remain
  partial

Bad reading:

- the framework family is missing basic runtime implementation
- the current partials are just stale bookkeeping noise with no owner
- clause-level service coverage alone proves every remaining framework rule

## Reading Order

1. `requirements/2010/hla1516_framework_detailed_reconciliation.csv`
2. `requirements/2010/traceability_matrix.csv`
3. `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`
4. `tests/verification/test_framework_rule_docs_v1_0.py`
5. `tests/backends/test_python_backend_time_ddm_extended.py`
6. `tests/factories/test_fom_omt_parsing.py`

## Related Docs

- [`README.md`](README.md)
- [`../../../requirements/2010/README.md`](../../../requirements/2010/README.md)
- [`../../verification/README.md`](../../verification/README.md)
- [`../../verification/requirement_compliance_exports.md`](../../verification/requirement_compliance_exports.md)
