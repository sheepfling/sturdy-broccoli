# IEEE 1516-2010 (2010 edition) / IEEE 1516.1-2010 (2010 edition) / IEEE 1516.2-2010 (2010 edition) Requirements Codebase Integration Work Packet

## Objective

Organize the IEEE 1516-2010 (2010 edition), IEEE 1516.1-2010 (2010 edition), and IEEE 1516.2-2010 (2010 edition) requirements artifacts into the codebase and connect them to implementation, tests, CI, and generated documentation.

This packet assumes the generated catalog is an engineering requirements baseline, not a certified legal/compliance extraction. The agent should preserve that caveat in repository docs and track peer-review status separately from implementation status.

## Canonical deliverables

Use these as the current canonical inputs:

- `hla_1516_requirements_master_v1_0.csv`
- `hla_1516_requirements_master_v1_0.xlsx`
- `hla_1516_verification_matrix_v1_0.csv`
- `hla_1516_clause_tracker_v1_0.csv`
- `hla_1516_clauses5_11_detailed_requirements_v1_0.csv`
- `hla_1516_cpp_api_catalog_v1_0.csv`
- carried-forward catalogs: Java API, MIM, XSD, and WSDL

## Recommended repository layout

```text
repo/
  docs/
    standards/
      hla-1516-2010/
        README.md
        requirements/
          latest/
          catalogs/
          history/
          dashboards/
          manifests/
        generated/
          by-standard/
          by-clause/
          by-capability/
  tools/
    requirements/
      README.md
      lint_requirements.py
      generate_requirements_docs.py
      schema.py
  tests/
    requirements/
      test_requirements_schema.py
      test_requirements_referential_integrity.py
      test_requirements_clause_coverage.py
```

## Integration phases

### Phase 1 — Asset placement

Copy the packet contents into the repository using the layout above. Treat `requirements/latest` as canonical. Treat `requirements/history` as audit/history only. Treat `requirements/restricted_reference_inputs` as private/reference material unless the repo license permits committing it.

### Phase 2 — Schema and linting

Create a requirements schema contract and validation command. At minimum, validate:

- required columns exist;
- `requirement_id` is unique;
- `test_id` is unique or intentionally many-to-one;
- every verification `requirement_id` exists in the master catalog;
- every P0/P1 requirement has a `verification_method`;
- clause tracker rows exist for IEEE 1516-2010 (2010 edition), IEEE 1516.1-2010 (2010 edition), and IEEE 1516.2-2010 (2010 edition) major clauses;
- manifest checksums match committed artifacts.

### Phase 3 — Test traceability

Add test metadata so tests can identify which requirements they cover. A simple starting rule is: every HLA service test includes at least one requirement ID from the catalog. Begin with Clause 4 and Clause 5, then expand through Clause 6, Clause 8, and Clause 11.

### Phase 4 — Documentation generation

Generate markdown views from the CSVs:

- by standard;
- by clause;
- by capability;
- by implementation area;
- by verification status.

Generated docs should state that the v1.0 catalog is an engineering baseline requiring peer review for exact paragraph traceability.

### Phase 5 — Implementation backlog generation

Use the requirements to create implementation tasks for:

- Federation Management;
- Declaration Management;
- Object Management;
- Ownership Management;
- Time Management;
- Data Distribution Management;
- Support Services;
- MOM/MIM;
- OMT/XML;
- native/gRPC/REST transport equivalence.

Each backlog item should link to requirement IDs and acceptance tests.

## Definition of done

The codebase is considered hooked up when:

1. canonical CSV/XLSX artifacts are placed in a stable docs path;
2. `MANIFEST.json` checksums are committed and verified in CI;
3. schema and referential-integrity tests pass;
4. generated markdown docs can be regenerated from CSVs;
5. at least one implementation test per Clause 4 and Clause 5 service carries requirement metadata;
6. the clause tracker is visible in the docs and identifies remaining peer-review work;
7. restricted standards inputs are handled according to repo policy.
