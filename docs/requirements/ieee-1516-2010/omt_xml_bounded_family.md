# 2010 OMT/XML Bounded Family

Use this page when the question is:

- why does the 2010 XML surface still carry `partial` rows even though parser,
  validator, schema, and round-trip coverage already exist?
- which single document owns the remaining `CAP-XML` bounded pattern plus the
  now-closed OMT normalization story?
- are those partial rows still vague, or already in an explicit bounded final
  state?

Short answer:

- the remaining `CAP-XML` rows are already in an explicit bounded family state
- the canonical XML owner ledger stays `partial` for those rows
- the OMT owner ledger is now fully mapped, including the former Annex B
  normalization tail
- the bounded or closeout reasons are structured and reviewable instead of
  implied

## Owner Surface

- canonical owner doc:
  `docs/requirements/ieee-1516-2010/omt_xml_bounded_family.md`
- canonical source owners:
  - `requirements/2010/hla1516_xml_detailed_reconciliation.csv`
  - `requirements/2010/hla1516_2_omt_detailed_reconciliation.csv`
- broad bridge:
  `requirements/2010/traceability_matrix.csv`
- primary shards:
  - `unit-fom-tooling`
  - `unit-python-core` only where MOM catalog or parser-fed runtime metadata
    witnesses sharpen the OMT claim

## Final Claim Rule

- keep the remaining XML rows `partial` when the repo already proves
  schema-backed parse or reject behavior, metadata preservation, and
  merge-safe round trips, but does not yet prove every imported schema atom as
  its own curated one-row witness
- treat the OMT Annex B normalization rows as `mapped` when the repo proves
  parser recognition, metadata preservation, executable support for the carried
  common normalization forms, and explicit OMT conformance classification for
  that supported subset
- do not describe these rows as missing XML parsing or schema validation
- do not describe these rows as unsupported OMT or FDD handling
- do not flatten the family into `mapped` merely because the current parser and
  validator evidence is strong at the schema-family level
- treat the current state as an explicit bounded final reading of the present
  evidence, not as hidden uncertainty

## Current Family Shape

The current XML owner ledger has `367` packet rows:

- `3 mapped`
- `364 partial`

The remaining `364 partial` XML rows cluster into stable categories:

- `274 XML_ELEM`
- `89 XML_TYPE`
- `1 CLAUSE12_13_DETAIL`

The current OMT owner ledger has `60` packet rows:

- `60 mapped`
- `0 partial`

## What The Categories Mean

### XML schema element breadth tail

The `274 XML_ELEM` rows describe individual schema element names.

These rows are not parser-presence gaps.
They remain `partial` because the current evidence proves family-level
schema-backed validation and round-trip behavior, not an isolated curated proof
for each imported element name as a standalone requirement witness.

### XML schema type breadth tail

The `89 XML_TYPE` rows describe individual XML schema types.

These rows follow the same bounded pattern:

- the repo proves the carried schemas are used for validation
- the repo proves representative parse, reject, and serialization behavior
- the repo does not yet maintain one curated executable witness per imported
  schema type

### FDD XSD normative-source boundary

The single `CLAUSE12_13_DETAIL` XML partial row is the broad Annex F normative
source statement for the FDD schema declaration.

The repo already validates against the carried standard schema path, but that
row still phrases the claim more broadly than the current direct curated
requirement surface.

### Annex B normalization closeout

The OMT normalization rows are no longer a bounded residual.

They are now directly backed by:

- parser or schema recognition and preservation of normalization metadata
- executable helper coverage for the carried common Annex B forms
  `linear (...)` and `linearEnumerated (...)`
- standard-MIM normalization references that already align to the implemented
  `Normalize Federate Handle service` and `Normalize Service Group service`
- `packages/hla-rti-core/src/hla/fom/__init__.py` `assess_omt_conformance`,
  which now treats that common subset as conforming while still classifying
  unknown normalization strings as only partially conforming

## What Is Already Proved

The current repo directly proves most of the 1516.2 parser and schema family,
including:

- OMT scope, purpose, background, lexicon, and conformance-label documentation
- FOM, SOM, MIM, and DIF parse or serialization paths through the carried
  standard schemas
- reject behavior for invalid documents and unknown namespaces
- round-trip preservation of model-identification and other supported metadata
- merge and validation flows over repo-owned example object models
- MOM catalog payloads that depend on exact MIM-backed model metadata

Primary evidence anchors:

- `tests/factories/test_fom_omt_parsing.py`
- `tests/factories/test_fom_validate.py`
- `tests/mom/test_mom_catalog_validation_v012.py`
- `requirements/2010/traceability_matrix.csv`

The matrix also now carries `REQ-OMT-SCHEMA-001` as an explicit
`implemented-slice` witness for Annex E schema-family validation and
schema-valid round-trip behavior.

## Good Reading

Good reading:

- the OMT and XML family is implemented, linked, and strongly validated at the
  schema-family, parser, validator, and metadata-preservation level
- the remaining partial rows describe atom-level XML schema granularity limits
- the OMT normalization story is now directly closed on the common Annex B
  subset the repo actually carries and tests
- the family already has a defensible supported-scope reading

Bad reading:

- the repo still lacks meaningful OMT or XML support
- FOM, SOM, FDD, DIF, or MIM handling is still speculative
- the partial rows imply the parser cannot validate the carried standard
  schemas

## Reading Order

1. `requirements/2010/hla1516_xml_detailed_reconciliation.csv`
2. `requirements/2010/hla1516_2_omt_detailed_reconciliation.csv`
3. `requirements/2010/traceability_matrix.csv`
4. `tests/factories/test_fom_omt_parsing.py`
5. `tests/factories/test_fom_validate.py`

## Related Docs

- [`README.md`](README.md)
- [`../../../requirements/2010/README.md`](../../../requirements/2010/README.md)
- [`../../verification/README.md`](../../verification/README.md)
- [`../../plans/requirements_gap_register.md`](../../plans/requirements_gap_register.md)
