# Backend Compliance Discovery

Use this page when the question is:

- which backends have explicit compliance evidence now
- where vendor parity is passing, partial, divergent, or not yet matrixed
- which generated artifact to open next for one backend or one spec slice

## Short Path

Refresh the compliance packet, then run the discovery command:

```bash
./tools/compliance generate
./tools/compliance discover --show-backlog
```

Filter to one backend when needed:

```bash
./tools/compliance discover --backend certi-native
./tools/compliance discover --backend vendor-certi-java-bridge
./tools/compliance discover --backend python-inmemory
```

Read machine-friendly output:

```bash
./tools/compliance discover --format json
```

Refresh and discover in one command:

```bash
./tools/compliance discover --refresh --show-backlog
```

Filter the ranked backlog directly:

```bash
./tools/compliance discover --show-backlog --priority P1
./tools/compliance discover --show-backlog --backend certi-native
./tools/compliance discover --show-backlog --section 8
```

## What The Command Reads

The discovery command does not generate new compliance claims. It reads the
existing packet and presents it in one place.

Primary sources:

- `analysis/compliance/core_backend_matrix.json`
- `analysis/compliance/section8_backend_matrix.json`
- `analysis/compliance/pitch_backend_matrix.json`
- `analysis/compliance/python_requirement_disposition.json`
- `analysis/compliance/certi_requirement_disposition.json`
- `analysis/compliance/certi-native_requirement_disposition.json`
- `analysis/compliance/portico_requirement_disposition.json`
- `analysis/compliance/portico-jpype_requirement_disposition.json`
- `analysis/compliance/portico-py4j_requirement_disposition.json`
- `analysis/compliance/pitch_requirement_disposition.json`
- `analysis/compliance/pitch-jpype_requirement_disposition.json`
- `analysis/compliance/pitch-py4j_requirement_disposition.json`
- `analysis/compliance/requirements_matrix_2010.json`
- `analysis/compliance/vendor_discovery_backlog.json`

Context sources:

- [backend_conformance_matrix.md](backend_conformance_matrix.md)
- [rti_options_and_test_matrix.md](rti_options_and_test_matrix.md)

## What You Get

The text output gives:

- backend count and source artifact counts
- refresh and discovery commands
- requirement-level vendor status totals
- one block per backend with:
  - matrix families present
  - status counts
  - session-status counts
  - first notable divergent or not-yet-matrixed row
  - one evidence test anchor
- optional ranked vendor backlog rows with recommended next actions

This is meant to answer “where should I look next” before you open the full
matrix files.

## Which Artifact To Open Next

After the discovery summary:

- Open `analysis/compliance/core_backend_matrix.md` for high-level backend slice parity across federation, exchange, ownership, and negotiated ownership.
- Open `analysis/compliance/section8_backend_matrix.md` for detailed Section 8 time-management backend coverage.
- Open `analysis/compliance/pitch_backend_matrix.md` for the focused Pitch real-runtime view.
- Open `analysis/compliance/pitch_requirement_disposition.md` for aggregate Pitch family requirement dispositions and split-profile clause summaries.
- Open `analysis/compliance/certi_requirement_disposition.md` for the aggregate CERTI family requirement disposition view.
- Open `analysis/compliance/pitch-jpype_requirement_disposition.md` or `analysis/compliance/pitch-py4j_requirement_disposition.md` when you need backend-specific requirement rows for one Pitch bridge profile.
- Open `analysis/compliance/certi-native_requirement_disposition.md` when you need the generated explicit CERTI native-runtime profile view.
- Open `analysis/compliance/portico_requirement_disposition.md`, `analysis/compliance/portico-jpype_requirement_disposition.md`, or `analysis/compliance/portico-py4j_requirement_disposition.md` when you need the generated explicit Portico requirement views; the JPype and Py4J profiles currently inherit the same family-level projection because Portico remains install-dependent and no profile-specific requirement evidence is generated yet.
- Open `analysis/compliance/requirements_matrix_2010.csv` when you need clause and requirement rows with vendor notes merged into the spec catalog.
- Open `analysis/compliance/vendor_discovery_backlog.md` when you want the ranked next vendor/backend discovery work across all current artifacts.
- Open `docs/backend_conformance_matrix.md` when you want the manual clause-level narrative for Python, CERTI, and Pitch.

## Operator Pattern

Recommended loop:

1. Run `./tools/compliance generate`.
2. Run `./tools/compliance discover --show-backlog`.
3. Filter to the backend, section, or priority you care about.
4. Open the specific matrix or evidence row named by the discovery output.
5. Implement or rerun the matching focused vendor test only after the artifact view is clear.

## Best Next Vendor Work

Typical high-value backlog entries right now:

- CERTI negotiated ownership divergence:
  - use the backlog row for `certi-native`
  - drill into `analysis/compliance/core_backend_matrix.md`
- Pitch Section 8 query/time rows still `not-yet-matrixed`:
  - use `--backend pitch-jpype --section 8`
  - drill into `analysis/compliance/section8_backend_matrix.md`
- Hosted transport rows that are positive-path only:
  - use `--priority P5`
  - drill into `core_backend_matrix.md` or `section8_backend_matrix.md`
- Portico install-dependent discovery:
  - promote only after Portico appears in the generated backend matrices
  - do not maintain a separate manual tracker for it

## Scope Limits

This discovery command is only as current as the generated compliance packet.
If the packet is stale, rerun `./tools/compliance generate` or use
`./tools/compliance discover --refresh`.
