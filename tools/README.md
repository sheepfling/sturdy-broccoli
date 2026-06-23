# Tools

This directory is the canonical home for human-facing operator entrypoints.

If you are deciding what command to run, start here, not in `scripts/`.

For IEEE 1516.1-2025 specifically, interpret the operator surface through
`hla-backend-python2025` as the main runtime lane. `hla-backend-shim` remains
only as compatibility-wrapper/import-compatibility code, and hosted FedPro
routes are bounded route variants rather than separate RTI families.

Core operator entrypoints:

- `./tools/python`
- `./tools/bootstrap`
- `./tools/test`
- `./tools/test-surface`
- `./tools/lint`
- `./tools/certi-easy`
- `./tools/pitch`
- `./tools/vendor-green`
- `./tools/vendor-state`
- `./tools/vendor-parity`
- `./tools/vendor-probe-review`
- `./tools/vendor-edge`
- `./tools/rti-options`
- `./tools/compliance`
- `./tools/fom-overview`
- `./tools/fom-validate`
- `./tools/fom-schema-baseline`
- `./tools/fom-schema-audit`
- `./tools/fom-siso-audit`
- `./tools/fom-corpus-classification`
- `./tools/fom-workbench`
- `./tools/fom-roundtrip`
- `./tools/fom-stress`
- `./tools/download-siso`
- `./tools/package-deps`
- `./tools/section8-gate`
- `./tools/target-radar`
- `./tools/two-federate`
- `./tools/shim-routes`
- `./tools/java`

The `scripts/` tree remains implementation and CI plumbing. Compatibility
wrappers may still exist under `scripts/`, but operator docs, workflows, tests,
and generated guidance should point at `tools/`.

Shortest common paths:

- bootstrap and activate: `./tools/bootstrap python`
- run one 2010 example: `python examples/target_radar_simulation.py --backend python --steps 5`
- run the main 2025 Target/Radar example lane: `python examples/target_radar_simulation.py --backend python2025 --steps 5`
- run the default test wrapper: `./tools/test`
- discover the canonical verification lanes: `./tools/test-surface recommend`
- run the primary 2025 Python RTI main-surface lane, including package-boundary guards plus raw support/decode and callback-control proofs on the direct `python2025` surface: `./tools/python verify-main-2025`
- run Python direct-vs-gRPC parity: `./tools/python verify-routes`
- run bounded hosted 2025 Python/FedPro route checks: `./tools/python verify-routes-2025`
- regenerate the checked-in 2025 finish-line and route-parity evidence bundle after proof-lane changes: `python3 scripts/run_spec2025_finish_line.py`
- check whether hosted Python gRPC is runnable here: `./tools/python verify-routes-preflight`
- inspect the language-shim route matrix: `./tools/shim-routes matrix --editions 2010,2025 --routes all`
- inspect the Java toolchain inventory: `./tools/shim-routes java doctor`
- inspect the Java toolchain inventory via the short front door: `./tools/java`
- validate one FOM XML or an inventory family: `./tools/fom-validate DemoFOMmodule.xml` or `./tools/fom-validate --family rpr-normative` and inspect the `Edition Scope` column in the JSON/markdown/HTML reports
- validate the positive XML/XSD baseline: `./tools/fom-schema-baseline` and keep an eye on the matching `Edition Scope` labels in the surrounding report chain
- run the schema-positive top-to-bottom audit: `./tools/fom-schema-audit` and inspect its `Edition Scope` column across validator, JSON cycle, and workbench outputs
- run the high-value SISO top-to-bottom audit: `./tools/fom-siso-audit` and inspect its `Edition Scope` column across validator, JSON cycle, and workbench outputs
- refresh the public baseline and generate a parser stress report: `./tools/fom-stress --refresh-baseline`
- download authenticated SISO DataFiles packages: `./tools/download-siso`
- catalog locally downloaded SISO packages into the shared inventory: `python3 scripts/generate_siso_inventory.py`
- classify the current corpus into validation buckets: `./tools/fom-corpus-classification` and inspect the `Edition Scope` column in the bucket tables

For 2025 runtime ownership and proof status behind those commands, read:

- `docs/python_rti_backend.md`
- `docs/python_rti_reading_map.md`
- `docs/verification/time_model_compliance.md`

Useful direct example entrypoints:

`python examples/backend_recording.py`
`python examples/rti_factory_selection.py --name in-memory --probe`
`python examples/target_radar_simulation.py --backend python --steps 5`
`python examples/target_radar_simulation.py --backend python2025 --steps 5`
