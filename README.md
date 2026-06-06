# hla2010-python

This archive is a clean seed for the Python HLA 1516.1-2010 workstream. It contains the current Python package source, Java bridge adapter source, pure-Python RTI source, examples, tests, helper scripts, FOM/MIM XML resources, and the user-supplied IEEE reference/source documents.

It intentionally does **not** include generated verification packets, generated analysis matrices, historical scaffold ZIPs, prior run summaries, pytest caches, built Java `.jar` files, or other transient assets. Those should be regenerated from source when needed.

## Layout

```text
hla2010/              Python package source
examples/             runnable examples, including Target/Radar
tests/                pytest tests and smoke coverage
tools/                spec-analysis and download helper scripts
java_shims/           Java shim source used for bridge validation; no built jar included
specs/ieee-1516-2010/ user-supplied IEEE PDFs and source ZIPs
docs/                 clean project notes for the repo seed
```

Additional repo-local material promoted from `INBOX`:

- `docs/plans/` 2010 workspace planning and foundation notes
- `docs/evidence/` unpacked verification evidence packets
- `docs/reference/hla-2010-specs.zip` original PDF-only reference drop
- `third_party/pitch/` Pitch pRTI / Visual OMT installer bundle
- `archives/` retained source-drop and verification ZIP archives

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
python -m pytest -q
python examples/target_radar_simulation.py --backend python --steps 5
```

Optional Java bridge packages can be installed with:

```bash
pip install -e '.[jpype]'
pip install -e '.[py4j]'
```

## Local RTI wiring

The repo now includes initial runtime wiring for two real RTI targets:

- `Pitch pRTI`
  exposed through the existing Java adapter layer as `pitch-jpype` and
  `pitch-py4j` backend kinds
- `CERTI`
  exposed as a native daemon/launcher target through
  `scripts/run_certi_local.sh`

Practical local commands:

```bash
./scripts/run_certi_local.sh rtig --help
python3 -c "from hla2010.rti import create_rti_ambassador; rti=create_rti_ambassador('pitch-jpype'); print(rti.getHLAversion()); rti.close()"
```

The `pitch-jpype` path currently discovers the extracted runtime from:

- `HLA2010_PITCH_HOME`, if set
- `third_party/pitch/PITCH-prti1516e-manual`, if present later
- the sibling workspace `../hla-python/INBOX/PITCH-prti1516e-manual`

The `CERTI` launcher currently discovers the install prefix from:

- `HLA2010_CERTI_PREFIX`, if set
- `third_party/certi/install`, if present later
- the sibling workspace `../hla-python/INBOX/CERTI-install`

## Current implementation focus

The package includes:

- a source-derived HLA-style Python `RTIambassador` and `FederateAmbassador` API surface;
- backend-neutral RTI adapters;
- a pure-Python in-memory RTI for local federations;
- JPype and Py4J Java RTI adapters, including a real Pitch pRTI discovery path;
- FOM/MIM loading and table-driven MOM catalog support;
- logical-time and timestamp-order support helpers;
- service-reporting, synchronization, save/restore, DDM, and Target/Radar scenario code.

This is still an **unofficial development/reference RTI**, not a certified production RTI.

## Intake status

The 2026-06-05 `INBOX` promotion inventory is recorded in
`docs/inbox_inventory_2026-06-05.md`.
