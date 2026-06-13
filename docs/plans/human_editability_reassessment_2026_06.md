# Human Editability Reassessment 2026-06

This note re-evaluates the repo from the perspective of a new human editor.

The repo is in a better architectural state than it was before the recent
guardrail work. The main remaining problem is no longer "hidden magic" as much
as "too many surfaces to understand before a human feels safe editing."

That distinction matters:

- guardrails are now materially stronger
- contributor navigation is still too broad
- the repo is easier to verify than it is to approach

## What Improved

These areas are materially better than they were:

- package hierarchy now has a machine-readable source of truth in
  `packages/package_graph.yaml`
- maintained package code now has strong guards against dynamic exports,
  wildcard facades, repo-root sniffing, and public dunder routing
- runtime, callback, Python RTI service, and Java bridge surfaces are now much
  more explicit and directly testable
- the Python RTI path is clearly the primary route for first real use
- a package-backed minimal FOM/federate example exists
- traceability now has executable validation and generated indexes

Those were necessary changes. They make the repo safer to maintain.

## What Still Feels Hard

The repo is still difficult for a human to open and "play with" without
already knowing its conventions.

### 1. Too Many Surfaces Before First Confident Edit

Current scale is still high:

- `18` installable package roots under `packages/`
- `98` Markdown docs under `docs/`
- `59` Markdown artifacts under `analysis/`
- `77` script files under `scripts/`
- `79` files under `requirements/`

That does not mean the repo is wrong. It means the repo needs a smaller
opinionated path for ordinary editing tasks.

### 2. Onboarding Is Canonical, But Still Long

`docs/onboarding.md` is better than the old state, but it still asks a new
reader to move through eleven documents before they can feel oriented.

That is a documentation hierarchy. It is not yet a contributor path.

### 3. Front Doors Are Maps, Not Working Lanes

`./tools/human-editability front-doors all` is useful, but each front door
still points to several files plus a reading map.

That helps a reviewer.
It does not yet help a new editor answer concrete questions such as:

- "I want to add one RTI service."
- "I want to add one callback."
- "I want to create one new FOM package."
- "I want to add one new federate pair."

### 4. Python RTI Is Primary, But The Edit Loop Is Still Wide

The Python RTI is now the right reference backend, but the implementation is
still spread across many service-family modules, state helpers, route helpers,
and generated indexes.

That architecture is defensible.
It is still heavier than a newcomer expects when they only want to:

- find one public method
- find the actual implementation
- change behavior
- run one targeted verification path

### 5. New FOM / Federate Work Is Documented More Than Scaffolded

`docs/create_federate_and_fom.md` is clear, and the minimal demo package is a
good reference, but the path is still manual.

A human still has to:

- copy the package shape by hand
- know which files are required
- know which tests to add
- know which requirement rows are appropriate

That is better than no guidance, but still not the "one obvious path" finish
line.

### 6. Traceability Is Executable, But Still Artifact-Heavy

The traceability program is much better defended now, but a new editor still
sees many surfaces:

- `requirements/traceability_matrix.csv`
- `analysis/compliance/requirements_ledger.csv`
- `analysis/traceability/service_trace_index.*`
- validation scripts
- generated compliance artifacts

That is good for auditability.
It is still too much for the common question:

"What requirement owns this method, where is the implementation, and what test
proves it?"

### 7. "All Smells Closed" Is True For The Guarded Inventory, But Misleading For Contributor Experience

`docs/plans/human_editability_smell_inventory.md` and
`analysis/human_editability/smell_inventory.json` currently show no remaining
open smells.

That is true only for the currently tracked finish-line inventory.
It should not be read as:

- onboarding is now short
- editing is now obvious
- traceability is now simple
- creating new packages is now turnkey

The guarded inventory is mostly about eliminating drift and magic.
The next phase is about lowering human cognitive load.

## Main Human Pain Points

If the goal is "a human can open this repo and safely start changing it," the
current main pain points are:

1. too many docs before first confident edit
2. too many package families before first mental model settles
3. too many traceability artifacts for ordinary method tracing
4. too much manual scaffolding for new FOM/federate work
5. too much indirection between public RTI method, implementation, and test
6. too much Java and vendor surface visible before it is needed

## Recommended Next Workstreams

These are the next practical workstreams to make the repo meaningfully easier
for humans.

### Workstream A: One Human Path

Create one short path for the most common contributor goals:

1. run the Python RTI example
2. edit one RTI service
3. create one new FOM package
4. trace one requirement end to end

This should likely become one page, not a map of pages.

### Workstream B: Scaffold New FOM / Federate Packages

Add one scaffold command or template flow such as:

```bash
./tools/new-fom-package your-demo
```

It should create:

- package layout
- `pyproject.toml`
- package `README.md`
- FOM resource location
- scenario module
- example runner
- starter test

The current doc should then become the explanation of the scaffold, not the
primary creation mechanism.

### Workstream C: Edit-One-Service Workflow

Add one contributor path specifically for Python RTI service edits:

- public method
- service registry row
- implementation helper or entrypoint
- focused tests
- traceability command

The finish line is that a human can change one service without reading the
entire Python RTI family first.

### Workstream D: Reduce Traceability To One Human Query Path

Keep the generated artifacts, but present one canonical human question path:

```bash
./tools/human-editability trace timeAdvanceRequest
```

Then tighten the docs so this command is the first thing readers see, with the
other files treated as backing assets rather than equal-priority entrypoints.

### Workstream E: Package Ownership Cards

Each installable package family should have a short ownership card that answers:

- what this package is for
- what humans usually edit here
- what not to edit here
- first files to open
- quickest tests to run

This is especially important for:

- `hla2010-spec`
- `hla2010-rti-python`
- `hla2010-rti-runtime-common`
- `hla2010-rti-backend-common`
- `hla2010-fom-*`

### Workstream F: Keep Java And Vendor Paths Clearly Secondary

The Java and vendor routes should stay documented, but they should remain
visibly later-phase routes:

- one short quickstart
- one smoke test path
- one limitations page per family

They should not crowd the first editing path for the repo.

## Concrete Finish Definition

The repo is in a more workable human-editable spot when a new contributor can
do all of these without tribal knowledge:

1. find the public spec interface for one RTI or callback method
2. find the real Python RTI implementation for that method
3. run one focused test slice for that method
4. create a new package-owned FOM and federate example from a scaffold
5. trace a requirement row to implementation and proof with one command
6. understand package ownership without reading the whole docs tree
7. ignore Java and vendor families until they intentionally opt into them

## Immediate Next Recommendation

Do not reopen the current guarded smell inventory first.

Use the next phase to add:

1. a true edit-one-service guide
2. a real new-FOM-package scaffold
3. a shorter onboarding path centered on concrete tasks, not document families
4. a contributor-facing package ownership map

That will move the repo from "well-guarded" to "pleasant to approach."
