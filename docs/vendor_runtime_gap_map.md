# Vendor Runtime Gap Map

This page separates three different kinds of remaining work:

1. repo mechanics that are already stabilized
2. environment prerequisites that must exist on the host or runner
3. real vendor/runtime conformance gaps that still need new proof slices

Use this page when a vendor run is not green and you need to decide whether the
next action is:

- fix the host/runtime environment
- rerun through the supported operator path
- or accept that the gap is currently a real conformance limitation

## Stable Repo Mechanics

These are the parts that should now be treated as standard repo behavior:

- vendor preflight runs before vendor smoke
- `./tools/python verify` is the repo-green lane
- `./tools/vendor-green ...` is the strict vendor-green lane
- vendor runtime tests use centralized cleanup helpers
- the CERTI runtime matrix no longer depends on widespread hard-coded UDP ports
- the Pitch real-runtime matrix now shares the same cleanup discipline

If one of those fails, treat it as repo work.

## Environment Prerequisites

These are not solved by more repo refactoring.

### CERTI

Required:

- loopback bind/connect permission
- working `.venv`
- fixed upstream/patched prefixes and build roots

Typical blocked signal:

- `environment: loopback-blocked`

Supported route:

```bash
./tools/certi-easy preflight
./tools/certi-easy smoke compare
./tools/certi-easy ddm-probe
./tools/certi-easy ddm-review 5
```

Primary references:

- [vendor_runtime_runner_guide.md](vendor_runtime_runner_guide.md)
- [../packages/hla-backend-certi/docs/certi_section8_runbook.md](../packages/hla-backend-certi/docs/certi_section8_runbook.md)
- [../packages/hla-backend-certi/docs/certi_runtime_limitations.md](../packages/hla-backend-certi/docs/certi_runtime_limitations.md)

### Pitch

Required:

- reachable Docker daemon
- repo Docker-backed runtime path
- fixed `HLA2010_PITCH_HOME` and `HLA2010_PITCH_USER_HOME`
- required ports available

Typical blocked signals:

- `environment: docker-blocked`
- `environment: bundle-blocked`
- `environment: ports-blocked`

Supported route:

```bash
./tools/pitch preflight
./tools/pitch smoke
./tools/pitch verify
```

Primary references:

- [vendor_runtime_runner_guide.md](vendor_runtime_runner_guide.md)
- [../packages/hla-vendor-pitch/docs/pitch_docker_quickstart.md](../packages/hla-vendor-pitch/docs/pitch_docker_quickstart.md)
- [../packages/hla-vendor-pitch/docs/pitch_decision_tree.md](../packages/hla-vendor-pitch/docs/pitch_decision_tree.md)

## Current Vendor Runtime Status

### CERTI

Promoted real-runtime slices:

- exchange
- time query / queued-FQR compare slices on the patched path
- synchronization
- selected ownership slices

Still incomplete:

- broader real-runtime proof outside the promoted exchange/time/sync/ownership slices
- save/restore real-matrix coverage
- DDM real-matrix coverage
- a narrow executable DDM probe now exists through `./tools/certi-easy ddm-probe`,
  but it is not promoted as a stable parity slice yet

Primary references:

- [backend_conformance_matrix.md](backend_conformance_matrix.md)
- [../packages/hla-backend-certi/docs/certi_runtime_limitations.md](../packages/hla-backend-certi/docs/certi_runtime_limitations.md)
- [../packages/hla-backend-certi/docs/certi_negotiated_ownership_findings.md](../packages/hla-backend-certi/docs/certi_negotiated_ownership_findings.md)

### Pitch

Promoted real-runtime slices:

- exchange/time overlap rows
- synchronization
- basic ownership

Not promoted:

- negotiated ownership
- save/restore
- DDM
- target/radar

Supported explicit known-gap / probe routes:

- `./tools/pitch negotiated`
- `./tools/pitch negotiated-probe`
- `./tools/pitch negotiated-review 5`
- `./tools/pitch save-restore`
- `./tools/pitch save-restore-probe`
- `./tools/pitch save-restore-review 5`
- `./tools/pitch ddm`
- `./tools/pitch ddm-probe`
- `./tools/pitch ddm-review 5`

Primary references:

- [backend_conformance_matrix.md](backend_conformance_matrix.md)
- [../packages/hla-vendor-pitch/docs/pitch_decision_tree.md](../packages/hla-vendor-pitch/docs/pitch_decision_tree.md)
- [../packages/hla-vendor-pitch/docs/evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md](../packages/hla-vendor-pitch/docs/evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md)

## What To Do Next

### If preflight is blocked

Do not call the runtime coverage incomplete. Fix the host or rerun on an
unsandboxed local terminal or dedicated CI runner.

### If preflight is green but a promoted slice fails

Treat it as real vendor/runtime evidence and compare it against the currently
promoted proof notes before making a new broad claim.

### If the target area is save/restore or DDM

Treat it as new conformance work, not packaging work.

That means the next deliverable should be one of:

- a new executable vendor slice
- a new diagnostic note
- or an explicit supported-subset statement

The machine-readable known-gap profiles under `analysis/vendor_gap_profiles/`
now also carry the supported next-step chain for these unpromoted areas:

- preflight
- probe
- repeated review

Use that artifact when CI or local tooling needs an explicit handoff from
`known-gap` status to the current probe/review route.
