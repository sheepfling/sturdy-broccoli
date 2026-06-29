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
- edition-wide canonical requirement truth:
  `requirements/2010/canonical_requirements.json`
- edition-wide backend-resolution companion:
  `requirements/2010/backend_resolution.json`
- family mapping bridge:
  `requirements/2010/hla1516_framework_detailed_reconciliation.csv`
- generated projection bridge:
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

- `35 mapped`
- `18 partial`

The remaining `18 partial` rows cluster into stable categories:

- `8 FW_RULE_DETAIL`
- `9 DET`
- `1 partial`

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

- `HLA1516-FW-5_3-DET-004`
  because RTI-mediated exchange and declaration gating are now directly mapped,
  while the broader federate-responsibility statement about substantive data
  correctness remains wider than the direct witnesses
- `HLA1516-FW-6_1-DET-001` through `HLA1516-FW-6_5-DET-002`
  because OMT parsing, SOM fixtures, publish or subscribe routing,
  ownership-transfer behavior, update-rate metadata, and time helpers are all
  present, while the federate-local SOM and capability statements remain
  broader than what those tests alone can claim exhaustively

### Umbrella framework rows

The remaining `partial` umbrella row is `HLA1516-RULE-006`. Earlier Rule 7,
Rule 8, Rule 9, and Rule 10 capability statements are now mapped where the
runtime directly proves the bounded executable behavior, while Rule 6 still
remains a federate-wide SOM-documentation claim rather than a runtime
capability claim.

## Residual Row Groups

The remaining `18` partial rows are not one undifferentiated backlog. They are
stable residual groups with explicit bounded readings.

### Broad conceptual framework rows

These rows remain partial because they are framework-wide conceptual or
architectural statements, not isolated runtime service obligations:

- `HLA1516-FW-FW_SCOPE-001`
- `HLA1516-FW-FW_PURPOSE-002`
- `HLA1516-FW-FW_OO_RELATIONSHIP-004`
- `HLA1516-FW-RATIONALE-015`

Canonical reading:

- repo documentation preserves these concepts and boundaries
- the runtime suite should not be stretched into proof of every conceptual
  implication

### Federate-responsibility and semantics-breadth rows

These rows remain partial because the runtime proves the nearby transport or
capability path, but not the broader substantive-correctness or full semantics
claim:

- `HLA1516-FW-5_3-DET-004`
- `HLA1516-FW-5_4-DET-002`
- `HLA1516-FW-RULE_7_PUBLISH_SUBSCRIBE-011`
- `HLA1516-FW-RULE_9_TIME-013`
- `HLA1516-FW-RULE_10_COMPLIANCE-014`

Canonical reading:

- the direct runtime witness is already credited to narrower mapped rows
- the remaining gap is broader correctness, semantics, SOM/FOM consistency, or
  federate-local conformance language

### SOM-documentation breadth rows

These rows remain partial because the repo proves OMT/SOM parsing and example
fixture preservation, but not the stronger claim that each federate in scope
owns a complete, federate-specific SOM proof surface:

- `HLA1516-FW-6_1-DET-001`
- `HLA1516-FW-6_1-DET-002`
- `HLA1516-FW-6_1-DET-003`
- `HLA1516-FW-RULE_6_SOM-010`
- `HLA1516-RULE-006`
- `HLA1516-FW-6_2-DET-003`
- `HLA1516-FW-6_3-DET-002`
- `HLA1516-FW-6_4-DET-002`
- `HLA1516-FW-6_5-DET-002`

Canonical reading:

- maintained SOM fixtures and OMT parsing prove the format and example-model
  surface
- they do not prove a per-federate authored SOM for every runtime capability

### Residual Read Rule

When one of the residual rows above stays partial, the intended reading is:

- the repo already has bounded evidence for the nearby executable capability
- the remaining gap is claim breadth, not missing basic runtime implementation
- the owner ledger is already the canonical narrowed disposition for that row

Do not reopen these rows merely because adjacent runtime slices are green. They
need broader owner evidence, not repetition of the already credited runtime
witnesses.

### Residual Exit Rule

Promote one of the residual rows above only if one of these becomes true:

1. a new direct witness proves the broader statement itself rather than only a
   neighboring runtime capability
2. a federate-specific SOM or rationale owner artifact is added and clearly
   narrows the row into a smaller honest documentation claim
3. the imported row is re-owned elsewhere with a better bounded interpretation

If none of those become true, preserve the current partial disposition.

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

Rule 3 and its direct exchange/detail slices are now mapped because the current
DM/DDM routing and declaration-gating tests directly prove RTI-mediated
exchange through the standard runtime path.

Rule 4 and the direct interface-surface rows are now mapped because joined
federates are exercised through the standard generated RTIambassador and
FederateAmbassador runtime surface rather than backend-private entry points.

Rule 8's direct dynamic-ownership capability rows are also now mapped because
the runtime directly proves joined federates can offer, request, cancel, and
complete dynamic object-attribute ownership transfer flows during execution.

Rule 9's direct update-condition capability rows are now mapped because the
runtime directly proves different subscribers can apply different update-rate
designators to the same attribute and observe different delivery behavior.

Rule 7's direct exchange-capability rows are now mapped because the DM/DDM
runtime directly proves publish/subscribe-driven attribute reflection and
interaction receipt across joined federates during execution.

Rule 10's direct time-coordination rows are now mapped because the runtime
directly proves timestamp-ordered delivery and time-advance grants coordinate
local federate time with federation exchange.

Rule 2 and its Clause 5.2 detail slices are now mapped because the runtime has
a direct witness that isolates the joined-federate simulation-state owner from
the RTI-owned standard MOM management exception.

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

1. `requirements/2010/canonical_requirements.json`
2. `requirements/2010/backend_resolution.json`
3. `requirements/2010/hla1516_framework_detailed_reconciliation.csv`
4. `requirements/2010/traceability_matrix.csv`
5. `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`
6. `tests/verification/test_framework_rule_docs_v1_0.py`
7. `tests/backends/test_python_backend_time_ddm_extended.py`
8. `tests/factories/test_fom_omt_parsing.py`

## Related Docs

- [`README.md`](README.md)
- [`../../../requirements/2010/README.md`](../../../requirements/2010/README.md)
- [`../../verification/README.md`](../../verification/README.md)
- [`../../verification/requirement_compliance_exports.md`](../../verification/requirement_compliance_exports.md)
