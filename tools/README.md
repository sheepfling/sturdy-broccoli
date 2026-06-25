# Tools

This directory is the canonical home for human-facing operator entrypoints.

If you are deciding what command to run, start here, not in `scripts/`.

For IEEE 1516.1-2025 specifically, interpret the operator surface through
`hla-backend-python1516-2025` as the main runtime lane. `hla-backend-shim` remains
only as compatibility-wrapper/import-compatibility code, only as a legacy compatibility shim, and hosted FedPro
routes are bounded route variants rather than separate RTI families.

Core operator entrypoints:

- `./tools/python`
- `./tools/bootstrap`
- `./tools/test`
- `./tools/test-focus`
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
- `./tools/fom-siso-pitch-2010-micro-strict`
- `./tools/fom-siso-pitch-micro-parity`
- `./tools/fom-siso-runtime-launcher`
- `./tools/fom-siso-runtime-showcase`
- `./tools/fom-siso-showcase`
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
- get the default recommended verification lane: `./tools/test-surface recommend`
- inspect or extend the repo-green unit sweep: `./tools/test-surface run repo-green-units`
- discover where unit shard order lives: `testing/test_surface_manifest.json` -> `repo-green-units.include_lanes`
- get the junior-friendly rerun and failure-diagnosis workflow: `docs/junior_test_diagnosis_runbook.md`
- run one 2010 example: `python examples/target_radar_simulation.py --backend python1516e --steps 5`
- run the main 2025 Target/Radar example lane: `python examples/target_radar_simulation.py --backend python1516_2025 --steps 5`
- run the isolated 2010 direct Python route example: `./tools/python smoke-examples --edition 2010`
- run the isolated 2025 direct Python route example: `./tools/python smoke-examples --edition 2025`
- run both isolated direct Python route examples: `./tools/python smoke-examples --all`
- run the focused direct Python example test: `./tools/python test-examples`
- run the default test wrapper: `./tools/test`
- stop the default test wrapper at the first failure: `./tools/test -x`
- list named focused test targets: `./tools/test-focus inventory`
- rerun one named focused target: `./tools/test-focus run foundation`
- rerun one package-aligned target: `./tools/test-focus run jpype`, `./tools/test-focus run py4j`, `./tools/test-focus run target-radar`, or `./tools/test-focus run rti-core`
- rerun one expensive 2025 concern directly: `./tools/test-focus run python-2025-time`, `./tools/test-focus run python-2025-save-restore`, `./tools/test-focus run python-2025-ownership`, `./tools/test-focus run python-2025-mom-callbacks`, or `./tools/test-focus run routes-2025`
- use submodule-style aliases when that is easier to remember: `./tools/test-focus run fom-target-radar`, `./tools/test-focus run rti-factory`, `./tools/test-focus run bridge-jpype`, `./tools/test-focus run save-restore-2025`
- resume only prior failures inside one focused target: `./tools/test-focus resume python-2025-runtime`
- discover the canonical verification lanes: `./tools/test-surface recommend`
- validate the named test-surface manifest without running tests: `./tools/test-surface validate`
- run the fast-fail repo smoke lane before expensive depth: `./tools/python verify-smoke`
- run the primary 2025 Python RTI main-surface lane, including package-boundary guards plus raw support/decode and callback-control proofs on the direct `python1516_2025` surface: `./tools/python verify-main-2025`
- run Python direct-vs-gRPC parity: `./tools/python verify-routes`
- run bounded hosted 2025 Python/FedPro route checks: `./tools/python verify-routes-2025`
- regenerate the checked-in 2025 finish-line and route-parity evidence bundle after proof-lane changes: `python3 scripts/run_spec2025_finish_line.py`
- check whether hosted Python gRPC is runnable here: `./tools/python verify-routes-preflight`
- inspect the language-shim route matrix: `./tools/shim-routes matrix --editions 2010,2025 --routes all`
- inspect the Java toolchain inventory: `./tools/shim-routes java doctor`
- inspect the Java toolchain inventory via the short front door: `./tools/java`
- run one isolated Java bridge smoke example without a vendor RTI: `./tools/java smoke --bridge jpype --edition 2010`
- run the full local 2010/2025 x JPype/Py4J isolated smoke matrix: `./tools/java smoke --all`
- build the tiny shim jar and run a real bridge route in isolation: `./tools/java smoke --bridge py4j --edition 2025 --real-shim`
- run the focused bridge example tests: `./tools/java test-bridges`
- read the shortest Java bridge wrapping recipe: `docs/java_bridge_minimal_protocol_recipe.md`
- read the Java bridge quick guide: `docs/java_bridge_wrapping_guide.md`
- read the Java bridge architecture guide: `docs/java_rti_adaptation_architecture.md`
- validate one FOM XML or an inventory family: `./tools/fom-validate DemoFOMmodule.xml` or `./tools/fom-validate --family rpr-normative` and inspect the `Edition Scope` column in the JSON/markdown/HTML reports
- validate the positive XML/XSD baseline: `./tools/fom-schema-baseline` and keep an eye on the matching `Edition Scope` labels in the surrounding report chain
- run the schema-positive top-to-bottom audit: `./tools/fom-schema-audit` and inspect its `Edition Scope` column across validator, JSON cycle, and workbench outputs
- run the high-value SISO top-to-bottom audit: `./tools/fom-siso-audit` and inspect its `Edition Scope` column across validator, JSON cycle, and workbench outputs
- generate the runtime-backed SISO showcase packet: `./tools/fom-siso-runtime-showcase`
- generate the runtime-backed SISO launcher packet: `./tools/fom-siso-runtime-launcher`
- generate the Pitch-eligible SISO micro parity packet: `./tools/fom-siso-pitch-micro-parity`
- generate the strict 2010 Pitch-only SISO micro packet: `./tools/fom-siso-pitch-2010-micro-strict`
- generate the bounded Pitch 202X micro comparison packet: `./tools/pitch 202x-micro-certify`
- generate the standards-backed showcase packet for Link 16, RPR 3.0, and Space FOM: `./tools/fom-siso-showcase`
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
`python examples/rti_factory_selection.py --name python1516e --probe`
`python examples/target_radar_simulation.py --backend python1516e --steps 5`
`python examples/target_radar_simulation.py --backend python1516_2025 --steps 5`
