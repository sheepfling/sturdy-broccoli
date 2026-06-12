# PLN-003 Requirements Authoring Plan

## Purpose

Finish the requirement-authoring backlog so the repo has a clean, explicit,
traceable requirement set instead of broad rows, seeded placeholders, and
implementation-driven leftovers.

This plan is about writing and refining requirements, not just implementing
tests.

## Scope

Author and normalize the full HLA 2010 requirement set for:

- IEEE 1516.1 Clauses 4 through 10
- IEEE 1516.1 Clause 11 MOM/MIM
- IEEE 1516.2 OMT
- XML and schema claims
- transport-family claims tracked by the repo

## Work Plan

### 1. Normalize the catalog

- Give every row one family, one clause anchor, one requirement ID, one owner,
  and one evidence anchor.
- Split bundled rows into atomic requirements.
- Remove vague placeholders from requirement text.

### 2. Finish seeded families

- Expand OMT rows into concrete parser, merge, validation, and conformance
  requirements.
- Expand XML rows into explicit schema and round-trip requirements.
- Separate Clause 11 MOM rows from MIM rows and make the observable behavior
  explicit.

### 3. Tighten broad clauses

- Rewrite broad Clause 4-10 rows so each one states a single claim.
- Make unsupported boundaries explicit instead of implied.
- Keep broad rows partial only when the narrower supported subset is clearly
  documented.

### 4. Clarify transport claims

- Separate backend behavior from transport behavior.
- Write explicit rows for request/response semantics, callback delivery,
  failure mapping, and backend/transport parity where needed.

### 5. Reconcile policy language

- Encode supported-subset behavior directly in the requirement text.
- Mark vendor-divergent rows with the exact divergence being claimed.
- Avoid overclaiming full compliance when only a narrower subset is proven.

### 6. Regenerate and review

- Regenerate the compliance artifacts and backlog views.
- Check for remaining seeded rows, duplicated claims, or clause drift.
- Iterate until the remaining open work is evidence closure, not missing
  requirement text.

## Exit Criteria

This plan is done when:

- every requirement row has a clear clause/family assignment
- every requirement row has a clear claim scope
- every requirement row has a clear test or evidence anchor
- no seeded placeholder rows remain in the authored set
- the remaining backlog is about proof, not unclear requirement text
