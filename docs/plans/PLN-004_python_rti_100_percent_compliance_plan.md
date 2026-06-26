# PLN-004 Python RTI 100 Percent Compliance Plan

## Purpose

Finish the compliance program for the repo-owned Python RTI lanes in a way that
is faithful, auditable, and honest.

This plan is not about inflating percentages by relabeling rows.
It is about:

- converting every row that should be direct support into direct executable
  proof
- keeping every row that should not be direct support explicit as a bounded
  claim, exclusion, or backend-resolution note
- updating the vendor and backend companion artifacts whenever Python-lane
  proof changes what those rows can honestly claim

The execution order is:

1. repository-green baseline and commit-ready closeout surfaces
2. `2025` Python RTI
3. `2010` Python RTI
4. vendor and backend companion rows as they are affected by those Python
   changes

## Goal Statement

Reach a faithful, auditable `100%` requirements outcome for the `2025` and then
`2010` Python RTI lanes by converting every remaining bounded, umbrella,
retired, legacy, route-limited, or partial requirement row into either direct
executable coverage or an intentionally narrowed canonical claim with explicit
evidence, while also updating affected vendor compliance rows and companion
backend-resolution artifacts whenever the Python-lane proof changes their
honest disposition.

## Copyable Goal Statement

Use this as the program-level objective:

> Reach a faithful, auditable `100%` requirements outcome for the `2025` and
> then `2010` Python RTI lanes by converting every remaining bounded, umbrella,
> retired, legacy, route-limited, or partial requirement row into either
> direct executable coverage or an intentionally narrowed canonical claim with
> explicit evidence, while also updating affected vendor compliance rows and
> companion backend-resolution artifacts whenever the Python-lane proof changes
> their honest disposition.

## Scope

This plan covers:

- the `2025` row-level requirement disposition ledger
- the `2010` harmonized requirement master index and family companions
- the canonical human-facing owner docs under `docs/requirements/`
- the closeout and audit surfaces under `docs/plans/`
- generated finish-line and compliance artifacts
- boss-facing spreadsheet exports
- vendor and backend companion artifacts for:
  - `Pitch`
  - `CERTI`
  - `Portico`
  - Java and C++ binding companions
  - hosted route and transport companions

This plan does not treat certified third-party conformance as implied.
If the repo wants to claim broader vendor or binding semantics later, that
requires a separate explicit program with its own proof.

## Execution Model

Use these execution terms precisely:

- `shard`: an independently runnable proof slice with one primary owner and one
  narrow pass or fail outcome
- `view`: an overlapping reporting surface that may read from multiple shards
  without owning their execution semantics
- `owner doc`: the canonical human-facing requirement reading
- `owner companion`: the canonical ledger, backend-resolution table, or row
  disposition artifact that carries the machine-facing truth

Operational rule:

1. close proof through shards
2. summarize status through views
3. never let a view become the source of row truth

See
[`PLN-005_requirements_shards_views_and_verification_plan.md`](PLN-005_requirements_shards_views_and_verification_plan.md),
[`../verification/shard_registry.md`](../verification/shard_registry.md), and
[`../verification/view_registry.md`](../verification/view_registry.md) for the
canonical model.

## Honest 100 Percent Rule

Use these terms precisely:

- `dispositioned`: every tracked row has an explicit final state
- `covered` or `mapped`: the repo has direct executable or direct evidence
  support for the exact row claim
- `bounded`: the repo intentionally claims a narrower supported scope than the
  broad source wording
- `duplicate/umbrella`: the row is a parent or normalization row rather than a
  standalone direct support claim
- `retired/legacy-only`: the row is an explicit exclusion from active support

Do not confuse these percentages:

1. `100% dispositioned`
2. `100% covered on active normative rows`
3. `100% of every tracked row marked covered`
4. `full conformance`

This plan only counts `100%` as honest when the denominator is explicit and the
row policy is written down before the metric is promoted.

## Denominator Rule

Before pushing for `100%`, freeze the denominator for each edition.

For `2025`, pick one of these and document it explicitly in the owner surfaces
and exports:

1. `all tracked rows`
2. `active normative non-retired non-umbrella rows`

Recommended rule:

- report `100% dispositioned`
- report `100% covered on active normative non-retired non-umbrella rows`
- report umbrella, retired, backend-resolution, and bounded rows separately

Only pursue literal `100% covered on all tracked rows` if the repo deliberately
funds:

- standalone proof decomposition for umbrella rows
- compatibility or migration proof for retired or legacy-only rows

## Phase Plan

### Phase 0: Get the repository green and commit-ready

Before changing any requirement claim:

1. make the repo green on the currently claimed requirement surfaces
2. keep documentation, generated artifacts, and tests aligned
3. split work into commit-ready slices so requirement truth, tooling, tests,
   and generated packets can be reviewed independently

This phase exists to prevent false requirement movement caused by stale
generated outputs, broken links, or mixed-purpose diffs.

### Phase 1: Freeze the 2025 metric

1. declare the denominator for `100%`
2. classify every non-plain-covered row as one of:
   - direct support target
   - explicit exclusion target
   - umbrella decomposition target
   - route or binding broadening target
   - backend-resolution-only target
3. encode that rule in:
   - `docs/plans/2025_requirement_by_requirement_audit.md`
   - `docs/plans/requirements_completion_audit.md`
   - `docs/verification/requirement_compliance_exports.md`

### Phase 2: Burn down the remaining 2025 Python RTI proof debt

For every row that still blocks the selected `100%` metric:

1. identify the canonical owner doc
2. identify the owner companion ledger
3. identify the narrowest shard or focused command
4. define the exact exit condition
5. add or tighten proof until the row can honestly move

Expected row classes:

- framework umbrella rows
- callback/configuration/binding umbrella rows
- retired or legacy-only rows if the repo chooses to support them
- route or hosted boundaries if the repo chooses to broaden them
- OMT extension-semantics rows if the repo chooses to broaden them
- any currently covered rows that still need stricter standalone proof rather
  than broad bounded-slice inheritance

Current execution companion for the umbrella-row class:

- [`2025_python_rti_umbrella_decomposition_worklist.md`](2025_python_rti_umbrella_decomposition_worklist.md)

### Phase 3: Update vendor and backend rows whenever Python proof changes

Whenever a Python-lane row changes:

1. refresh the matching backend-resolution companion
2. refresh the generated vendor disposition artifacts
3. refresh any affected:
   - route parity packets
   - Pitch `202X` comparison packets
   - binding surfaces
   - hosted transport notes
4. confirm the vendor row does not inherit optimism it has not directly earned

Operational rule:

- Python progress may improve vendor rows
- Python progress must not silently overwrite vendor divergence

### Phase 4: Lock the 2025 finish line

After the row moves are complete:

1. rerun the row-level audit
2. rerun the grouped harmonization worklist checks
3. rerun finish-line snapshots
4. rerun documentation and traceability checks
5. rerun the owning shards that feed the affected views
6. regenerate spreadsheet exports

The `2025` finish line is only stable when:

- the owner docs
- the ledgers
- the finish-line packets
- the generated exports

all tell the same story.

### Phase 5: Repeat the same process for 2010 Python RTI

For `2010`, apply the same rule family-by-family:

1. identify rows or bounded families that still block the chosen metric
2. tighten direct Python proof where the row should become `mapped`
3. keep mixed-backend and vendor divergence explicit where the row should stay
   bounded
4. update companion ledgers and generated vendor artifacts whenever the Python
   story changes

Likely priority families:

- mixed-backend priority rows
- high-volume partial families whose direct Python proof can be tightened
- XML or OMT rows if the repo deliberately broadens the current bounded scope

Current execution companion for the `2010` bounded-family class:

- [`2010_python_rti_bounded_family_execution_worklist.md`](2010_python_rti_bounded_family_execution_worklist.md)

### Phase 6: Final compliance closeout

When both editions are processed:

1. prove the final percentages from the canonical ledgers
2. prove every excluded class is intentional
3. prove every vendor row affected by Python proof changes was updated
4. regenerate the spreadsheet packets and executive summary surfaces

## Current Completion Track

Execute the remaining work in this order:

1. keep the repository green and commit-ready while requirement truth moves
2. close the remaining `2025` Python RTI rows against the declared denominator
3. refresh every affected backend-resolution and vendor companion surface
4. close the remaining `2010` Python RTI bounded-family and partial-row tails
5. regenerate boss-facing `2010` and `2025` spreadsheet packets
6. prove that top-level docs, owner docs, ledgers, views, and exports all
   report the same final story

For each bucket or row family, use the same operating sequence:

1. identify the canonical owner doc and owner companion
2. identify the narrowest owning shard
3. decide whether the row should become direct proof, stay bounded, stay
   duplicate/umbrella, or stay backend-resolution only
4. update canonical docs first, then companion ledgers
5. rerun the owning shard and affected doc-policy checks
6. refresh generated artifacts and spreadsheet exports when their inputs change
7. only then promote the bucket in closeout or finish-line views

This keeps `shards` as the executable ownership layer and `views` as the
overlapping reporting layer.

## Working Rules

### Row Movement Rule

Do not move a row to `covered` or `mapped` unless:

1. the exact row claim is supported directly
2. the narrowest owning shard is named
3. the owner doc and owner companion are both updated

### Vendor Update Rule

Whenever Python proof changes an owning family:

1. inspect the matching vendor rows
2. refresh generated vendor artifacts
3. keep vendor divergences explicit instead of implied

### Documentation Rule

Every metric or closeout statement must be derivable from:

- canonical owner docs
- canonical owner companions
- executable proof or generated artifact inputs

Do not let presentation packets become the source of truth.

### Repository-Green Rule

Before promoting any requirement bucket:

1. the narrowest owning shard must pass
2. affected documentation policy or link checks must pass
3. affected generated outputs must be refreshed if their inputs changed
4. the repo must remain in a reviewable, commit-ready state

If a bucket needs a view-only explanation update, do not mark the row moved
until the underlying shard evidence is still green.

## Deliverables

This plan is finished through these deliverables:

1. canonical owner docs for the `2025` and `2010` requirement surfaces
2. aligned owner companions and backend-resolution tables
3. repo-green shard coverage for every promoted direct-support claim
4. synchronized finish-line and closeout views
5. separate boss-facing spreadsheet packets for:
   - `2010 / 1516e`
   - `2025 / 1516_2025`
6. commit-ready slices for:
   - canonical requirement truth
   - tooling and export support
   - tests and documentation guards
   - refreshed generated artifacts

## Exit Criteria

This plan is complete when all of these are true:

1. the repo has one explicit, documented denominator for the `2025` and `2010`
   Python RTI `100%` metric
2. every row that counts against that denominator is either directly covered or
   deliberately reclassified by explicit policy
3. every reclassification has a canonical owner doc and companion artifact
4. every Python-proof change that affects vendor truth has propagated into the
   vendor compliance rows and backend-resolution artifacts
5. finish-line docs, closeout docs, ledgers, generated artifacts, and
   spreadsheet exports all agree on the final metric
6. the resulting claim is honest enough to survive row-by-row audit without
   hidden exclusions or overloaded status fields

## Related Docs

- [requirements_completion_audit.md](requirements_completion_audit.md)
- [requirements_remaining_closure.md](requirements_remaining_closure.md)
- [requirements_gap_register.md](requirements_gap_register.md)
- [requirements_execution_queue.md](requirements_execution_queue.md)
- [2025_requirement_by_requirement_audit.md](2025_requirement_by_requirement_audit.md)
- [../verification/requirement_compliance_exports.md](../verification/requirement_compliance_exports.md)
