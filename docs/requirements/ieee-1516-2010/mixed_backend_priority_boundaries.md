# Mixed-Backend Priority Boundaries

Use this page when the question is:

- why are a few 2010 priority owner rows now `pass` even though backend truth still differs?
- which single document owns the backend split for the lost-federate and RO/TSO rows?
- are these rows closed, or still an open ambiguity bucket?

Short answer:

- they are already in an explicit bounded mixed-backend state
- the canonical requirement rows are now `pass`
- backend-by-backend truth lives in the companion ledger, not in one overloaded status cell

## Owner Surface

- canonical owner doc:
  `docs/requirements/ieee-1516-2010/mixed_backend_priority_boundaries.md`
- canonical source companion:
  `requirements/2010/hla1516_1_priority_backend_resolution.csv`
- primary owner rows:
  `requirements/2010/hla1516_1_priority_clauses_4_8_11.csv`
- broad bridge:
  `requirements/2010/traceability_matrix.csv`
- export and handoff surface:
  `docs/verification/requirement_compliance_exports.md`
- primary shards:
  - `unit-scenarios-light` for lost-federate rows
  - `unit-python-core` for the RO/TSO ordering row

## Final Claim Rule

- canonical requirement status answers the repo-supported claim only
- do not flatten mixed backend truth into one optimistic backend-parity claim
- Python proof can be `verified` while Pitch remains `blocked` or
  `vendor-divergent` and Portico remains `classification-required`
- treat the current state as an explicit bounded final reading of the present
  evidence, not as hidden ambiguity
- keep backend divergence in the companion ledger instead of forcing the owner
  row back to `partial`

## Default Final Stance

- this owner note is the canonical final reading for the current mixed-backend
  priority rows
- the rows are not waiting on wording cleanup; they are already in their
  intended bounded final-state presentation
- the unresolved part is only optional future backend expansion, not ambiguity
  in the current requirement reading
- keep the clause rows `pass` and keep the backend split in
  `hla1516_1_priority_backend_resolution.csv` unless the repo reopens a broader
  cross-backend parity claim

## Exit Condition

Treat this bucket as closed for documentation ownership and closeout-surface
purposes unless one of these becomes true:

1. CERTI, Pitch, or Portico evidence materially changes one of the three rows
2. the repo decides to make a broader cross-backend parity claim for these
   requirements
3. the canonical requirement rows stop being the right owner location for this
   mixed-backend boundary

If none of those happen, preserve the current bounded reading and do not keep
listing these rows as active execution-queue debt.

## Current Mixed-Backend Rows

| Requirement ID | Summary | Canonical status | Current bounded reading |
| --- | --- | --- | --- |
| `HLA1516.1-FM-4.1.5-001` | lost-federate detection and MOM reporting | `pass` | Python directly proves connection-lost callback delivery and observer-visible `HLAreportFederateLost`; CERTI is not yet closed on this surface, Pitch is blocked on the canonical probe, and Portico still needs runtime classification. |
| `HLA1516.1-FM-4.1.5-002` | automatic resign handling for lost federates | `pass` | Python directly proves automatic lost-federate resign handling on the shared scenario; CERTI is not yet closed on this surface, Pitch is blocked on the canonical probe, and Portico still needs runtime classification. |
| `HLA1516.1-TM-8.1.2-003` | RTI shall never convert RO messages into received TSO messages | `pass` | Python and CERTI directly prove receive-order override paths remain receive-order on delivery; Pitch is vendor-divergent on this ordering surface, and Portico still needs runtime classification. |

## Backend Resolution Rule

Read the backend-resolution companion like this:

- `python_runtime_disposition`: strongest repo-owned executable proof lane
- `certi_runtime_disposition`: current CERTI closeout state for the same row
- `pitch_runtime_disposition`: current Pitch closeout state for the same row
- `portico_runtime_disposition`: current Portico classification or proof state
- `primary_command`: narrowest command that justified the current row state
- `boundary_note`: one-sentence reason backend-resolution truth still diverges

Good shape:

- canonical status: `pass`
- backend resolution:
  - `python=verified`
  - `certi=verified` or `not-yet-tested`
  - `pitch=blocked` or `vendor-divergent`
  - `portico=classification-required`

Bad shape:

- promoting the row to a broader cross-backend parity claim just because Python passes
- treating Pitch preflight blockage as if it were the same thing as Python proof
- hiding Portico uncertainty inside a generic clause-level note

## Reading Order

1. `requirements/2010/hla1516_1_priority_clauses_4_8_11.csv`
2. `requirements/2010/hla1516_1_priority_backend_resolution.csv`
3. `requirements/2010/traceability_matrix.csv`
4. the owning shard command named in the companion ledger

## Related Docs

- [`README.md`](README.md)
- [`../../../requirements/2010/README.md`](../../../requirements/2010/README.md)
- [`../../verification/README.md`](../../verification/README.md)
- [`../../verification/requirement_compliance_exports.md`](../../verification/requirement_compliance_exports.md)
