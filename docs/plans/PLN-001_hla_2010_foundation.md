# PLN-001 HLA 2010 Foundation

Title: HLA 2010 Foundation
Plan ID: PLN-001
Status: draft
Owner: @rick
Priority: P0
Objective: Stand up a 2010-only HLA workspace with source PDFs, clause
inventory scaffolding, and a validation path that can answer whether the
project is ready to claim 2010-family compliance.

Scope:
- IEEE 1516-2010 framework and rules
- IEEE 1516.1-2010 federate interface
- IEEE 1516.2-2010 OMT
- 2010-only extraction, traceability, and evidence artifacts

Out of Scope:
- 2025-spec implementation work
- broader HLA family redesign beyond the 2010 scope
- certification claims without clause-level evidence

Initial Steps:
1. Promote the 2010 PDF bundle into a project-local reference area.
2. Generate a 2010 clause inventory for the three family documents.
3. Create a traceability matrix template and an evidence ledger template.
4. Add a repo-local validation command for the 2010-only scope.
5. Record the remaining gaps explicitly instead of folding them into the main
   Python HLA workspace.

Artifacts:
- `docs/reference/`
- `docs/specs/`
- `scripts/`
- `tests/`
