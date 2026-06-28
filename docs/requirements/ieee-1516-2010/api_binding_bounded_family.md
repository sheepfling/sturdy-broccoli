# 2010 API-Binding Bounded Family

Use this page when the question is:

- why does the 2010 API-binding surface still carry `partial` rows even though
  the generated ambassador method surface is already strongly mapped?
- where do the remaining C++ catalog and Web Services binding rows get their
  canonical bounded reading?
- which document explains the difference between mapped source-derived API
  method metadata and still-partial imported binding catalogs?

Short answer:

- the remaining `CAP-API` partial rows are already in an explicit bounded
  family state
- the canonical API owner ledger stays `partial` only for broad binding,
  header-token, and WSDL-catalog claims that the repo does not implement live
- the mapped `CPP_METHOD` rows already credit the generated ambassador method
  surface directly through source-derived `raw_api` metadata and requirements
  ledger checks

## Owner Surface

- canonical owner doc:
  `docs/requirements/ieee-1516-2010/api_binding_bounded_family.md`
- canonical source owner:
  `requirements/2010/hla1516_1_api_detailed_reconciliation.csv`
- neighboring clause owner:
  `requirements/2010/hla1516_1_conf_detailed_reconciliation.csv`
- broad bridge:
  `requirements/2010/traceability_matrix.csv`
- export and handoff surface:
  `docs/verification/requirement_compliance_exports.md`
- primary shard:
  `unit-shim-tooling`

## Final Claim Rule

- keep the remaining API rows `partial` when the repo already proves the
  generated ambassador method surface or preserves imported binding catalogs,
  but does not yet prove a live Web Services runtime surface, per-class C++
  header-token witnesses, or broader cross-binding semantics
- treat the mapped `CPP_METHOD` rows as directly closed where source-derived
  `raw_api` metadata and the requirements-ledger checks preserve the standard
  ambassador method signature surface
- do not describe these rows as missing Python RTI API coverage
- do not flatten imported C++ catalog tokens or WSDL operation rows into
  `mapped` merely because the generated method surface is strongly covered

## Current Family Shape

The current API owner ledger has `614` packet rows:

- `221 mapped`
- `393 partial`

The remaining `393 partial` rows cluster into stable categories:

- `308 WSDL_OP`
- `79 CPP_CLASS`
- `6 CLAUSE12_13_DETAIL`

## What The Categories Mean

### Web Services binding operation tail

The `308 WSDL_OP` rows are imported Web Services operation catalog rows.

These rows are not missing packet integrity or schema-validation coverage.
They remain `partial` because the repo carries the imported WSDL operation
catalog and validates it through the packet loader, but does not yet implement
or verify a live WSDL-backed runtime surface for each operation.

### C++ header-token catalog tail

The `79 CPP_CLASS` rows are imported C++ catalog or class/header token rows.

These rows remain `partial` because the repo preserves the imported C++ catalog
and source-derived ambassador method metadata, but does not yet maintain one
curated executable or static witness per header-level token.

### Broad binding and clause-detail rows

The remaining `6 CLAUSE12_13_DETAIL` rows are the broad binding-level claims:

- `HLA1516.1-API_CONCURRENCY-006`
- `HLA1516.1-API_DYNAMIC_LINK-007`
- `HLA1516.1-API_CPP-012`
- `HLA1516.1-API_WSDL-013`
- `HLA1516.1-API_CPP_NORMATIVE-017`
- `HLA1516.1-API_WS_NORMATIVE-018`

These rows stay `partial` because they speak more broadly than the currently
credited method-signature evidence:

- designator behavior is only partially proved across bindings
- callback dispatch exists, but not the full cross-binding concurrency contract
- generated binding facades exist, but no dedicated dynamic-link verification
  slice exists
- the imported normative C++ and Web Services binding catalogs are present, but
  only the method-signature surface is directly mapped today

## Residual Read Rule

When one of the API-family rows stays `partial`, the intended reading is:

- the repo already proves the generated ambassador method surface where it says
  `mapped`
- the remaining gap is binding breadth or imported-catalog atom granularity,
  not missing core Python RTI method coverage
- the canonical owner ledger now says that explicitly in each remaining partial
  row via `Canonical residual disposition:`

Do not reopen these rows merely because method-signature or packet-loader
coverage is green. They need narrower per-token or live-binding witnesses, not
repetition of the already credited source-derived evidence.

## Residual Exit Rule

Promote one of the residual API rows only if one of these becomes true:

1. a new direct witness proves that imported C++ token or WSDL operation as
   its own curated requirement
2. a live Web Services binding surface is implemented and verified for the
   relevant operation or broader binding row
3. the row is intentionally re-owned into a smaller honest canonical claim
   whose bounded surface matches the evidence already carried

If none of those become true, preserve the current partial disposition.

## What Is Already Proved

The current repo directly proves the generated ambassador method surface for
the imported C++ method rows through:

- source-derived `raw_api` metadata that preserves the standard generated
  method surface
- requirements-ledger coverage that ensures the generated API surface remains
  represented in the canonical requirements inventory
- callback-family overview rows for reflect, receive, and remove method groups
- cross-binding designator metadata and overload-resolution coverage for
  local-settings, logical-time, FOM-module, and update-rate designators

Primary evidence anchors:

- `tests/factories/test_fom_time_factories.py`
- `tests/verification/test_spec_traceability_all_methods.py`
- `tests/verification/test_requirements_ledger_v013.py`
- `tests/verification/test_api_detailed_reconciliation.py`
- `requirements/2010/traceability_matrix.csv`

## Good Reading

Good reading:

- the generated 2010 ambassador method surface is already mapped
- the remaining partial rows are imported binding-catalog or broad
  cross-binding residuals
- the API family has an honest bounded final-state reading instead of an
  undocumented tail

Bad reading:

- the repo lacks meaningful 2010 API coverage
- the remaining partial rows imply that the generated Python-facing method
  surface is missing
- imported WSDL or C++ catalog rows are automatically `mapped` just because the
  method-signature surface is strong

## Reading Order

1. `requirements/2010/hla1516_1_api_detailed_reconciliation.csv`
2. `requirements/2010/hla1516_1_conf_detailed_reconciliation.csv`
3. `requirements/2010/traceability_matrix.csv`
4. `docs/verification/requirement_compliance_exports.md`

## Related Docs

- [`README.md`](README.md)
- [`../../../requirements/2010/README.md`](../../../requirements/2010/README.md)
- [`../../verification/README.md`](../../verification/README.md)
- [`../../verification/requirement_compliance_exports.md`](../../verification/requirement_compliance_exports.md)
