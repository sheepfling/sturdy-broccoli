# Tools

This directory is the canonical home for human-facing operator entrypoints.

If you are deciding what command to run, start here, not in `scripts/`.

Core operator entrypoints:

- `./tools/python`
- `./tools/bootstrap`
- `./tools/test`
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
- `./tools/human-editability`
- `./tools/examples`
- `./tools/new-fom-package`
- `./tools/rti-factories`
- `./tools/spec-api`
- `./tools/package-deps`
- `./tools/section8-gate`
- `./tools/target-radar`
- `./tools/two-federate`

The `scripts/` tree remains implementation and CI plumbing. Compatibility
wrappers may still exist under `scripts/`, but operator docs, workflows, tests,
and generated guidance should point at `tools/`.

Shortest common paths:

- bootstrap and activate: `./tools/bootstrap python`
- run one example: `./tools/examples target-radar --backend in-memory --steps 5`
- inspect factories: `./tools/rti-factories list`
- trace one method: `./tools/human-editability trace timeAdvanceRequest`
- run the default test wrapper: `./tools/test`
- run Python direct-vs-gRPC parity: `./tools/python verify-routes`
- check whether hosted Python gRPC is runnable here: `./tools/python verify-routes-preflight`

Useful `./tools/human-editability` entrypoints:

`./tools/human-editability check`
`./tools/human-editability front-doors`
`./tools/human-editability front-doors spec`
`./tools/human-editability front-doors fom`
`./tools/human-editability front-doors python-rti`
`./tools/human-editability front-doors python-rti-service`
`./tools/human-editability front-doors requirements-trace`
`./tools/human-editability front-doors rti-factories`
`./tools/human-editability front-doors requirements`
`./tools/human-editability trace timeAdvanceRequest`
`./tools/human-editability requirement REQ-RTI-TM-8_8-timeAdvanceRequest`

Useful FOM scaffold entrypoint:

`./tools/new-fom-package target-tracker`

Useful `./tools/examples` entrypoints:

`./tools/examples backend-recording`
`./tools/examples rti-factory-selection --name in-memory --probe`
`./tools/examples target-radar --backend in-memory --steps 5`
`./tools/examples minimal-fom-demo --backend in-memory`

Useful `./tools/rti-factories` entrypoints:

`./tools/rti-factories list`
`./tools/rti-factories show python`
`./tools/rti-factories show in-memory --probe`
`./tools/rti-factories instantiate in-memory --probe`
