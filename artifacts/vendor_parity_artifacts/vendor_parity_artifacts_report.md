# Vendor Parity Artifacts

- suite: `vendor-parity-artifacts`
- artifacts indexed: `36`
- required artifacts: `19`
- existing artifacts: `28`
- missing required artifacts: `0`

## Profiles

| Vendor | Profile | Tier | Indexed | Existing | Missing required | Kinds |
| --- | --- | --- | ---: | ---: | ---: | --- |
| shared | shared | shared | 11 | 9 | 0 | script, test, doc, preflight, promotion-review |
| certi | certi-save-restore-probe | probe | 1 | 0 | 0 | stability-summary |
| certi | certi-ddm-probe | probe | 1 | 0 | 0 | stability-summary |
| pitch | pitch-save-restore-probe | probe | 1 | 0 | 0 | stability-summary |
| pitch | pitch-ddm-probe | probe | 1 | 0 | 0 | stability-summary |
| pitch | pitch-negotiated-probe | probe | 1 | 0 | 0 | stability-summary |
| pitch | pitch-time-window-probe | probe | 1 | 1 | 0 | stability-summary |
| pitch | pitch-time-window-restore-state-probe | probe | 1 | 1 | 0 | stability-summary |
| pitch | pitch-lost-federate-probe | probe | 1 | 0 | 0 | stability-summary |
| certi | certi-save-restore | known-gap | 1 | 1 | 0 | gap-profile |
| certi | certi-ddm | known-gap | 1 | 1 | 0 | gap-profile |
| pitch | pitch-save-restore | known-gap | 1 | 1 | 0 | gap-profile |
| pitch | pitch-ddm | known-gap | 1 | 1 | 0 | gap-profile |
| pitch | pitch-negotiated | known-gap | 1 | 1 | 0 | gap-profile |
| pitch | pitch-lost-federate | known-gap | 1 | 1 | 0 | gap-profile |
| certi | certi-compare | promoted | 7 | 7 | 0 | test, support, doc |
| pitch | pitch | promoted | 4 | 4 | 0 | test, doc |

## Commands

- `./tools/certi-easy smoke compare` [promoted]
  Run the current upstream-vs-patched CERTI compare slice.
- `./tools/pitch smoke` [promoted]
  Run the current Pitch runtime smoke and matrix slice.
- `./tools/vendor-state classify --lane repo-green --json` [shared]
  Classify whether blocked vendor prerequisites are acceptable for the repo-green lane.
- `./tools/vendor-state classify --lane vendor-green --vendor certi --json` [shared]
  Classify strict CERTI vendor-green readiness from preflight artifacts.
- `./tools/vendor-state classify --lane vendor-green --vendor pitch --json` [shared]
  Classify strict Pitch vendor-green readiness from preflight artifacts.
- `./tools/certi-easy save-restore` [known-gap]
  Emit the current explicit CERTI save/restore known-gap status after preflight.
- `./tools/certi-easy save-restore-probe` [probe]
  Run the current narrow executable CERTI save/restore runtime probe after preflight.
- `./tools/certi-easy ddm` [known-gap]
  Emit the current explicit CERTI DDM known-gap status after preflight.
- `./tools/certi-easy ddm-probe` [probe]
  Run the current narrow executable CERTI DDM runtime probe after preflight.
- `./tools/pitch save-restore` [known-gap]
  Emit the current explicit Pitch save/restore known-gap status after preflight.
- `./tools/pitch save-restore-probe` [probe]
  Run the current narrow executable Pitch save/restore runtime probe after preflight.
- `./tools/pitch ddm` [known-gap]
  Emit the current explicit Pitch DDM known-gap status after preflight.
- `./tools/pitch ddm-probe` [probe]
  Run the current narrow executable Pitch DDM runtime probe after preflight.
- `./tools/pitch negotiated` [known-gap]
  Emit the current explicit Pitch negotiated-ownership known-gap status after preflight.
- `./tools/pitch negotiated-probe` [probe]
  Run the current narrow executable Pitch negotiated-ownership runtime probe after preflight.
- `./tools/pitch time-window-probe` [probe]
  Run the current narrow executable Pitch two-federate time-window future-exclusion probe after preflight.
- `./tools/pitch time-window-restore-state-probe` [probe]
  Run the current narrow executable Pitch two-federate time-window restore-state probe after preflight.
- `./tools/pitch lost-federate` [known-gap]
  Emit the current explicit Pitch lost-federate known-gap status after preflight.
- `./tools/pitch lost-federate-probe` [probe]
  Run the current narrow executable Pitch lost-federate runtime probe after preflight.
- `./tools/vendor-edge all` [shared]
  Run the highest-value vendor edge packet refresh.
- `./tools/certi-easy save-restore-review 5` [shared]
  Run repeated stability evidence plus promotion/parity refresh for the CERTI save/restore probe.
- `./tools/certi-easy ddm-review 5` [shared]
  Run repeated stability evidence plus promotion/parity refresh for the CERTI DDM probe.
- `./tools/pitch save-restore-review 5` [shared]
  Run repeated stability evidence plus promotion/parity refresh for the Pitch save/restore probe.
- `./tools/pitch ddm-review 5` [shared]
  Run repeated stability evidence plus promotion/parity refresh for the Pitch DDM probe.
- `./tools/pitch negotiated-review 5` [shared]
  Run repeated stability evidence plus promotion/parity refresh for the Pitch negotiated-ownership probe.
- `./tools/pitch lost-federate-review 5` [shared]
  Run repeated stability evidence plus promotion/parity refresh for the Pitch lost-federate probe.
- `./tools/vendor-probe-review promotion-review` [shared]
  Write the promotion-review artifact over repeated-run vendor probe evidence.
- `python3 scripts/generate_compliance_artifacts.py` [shared]
  Refresh generated compliance matrices after a vendor run.

## Preflight

- `certi`: no JSON preflight snapshot is currently present
- `pitch`: no JSON preflight snapshot is currently present

## Runtime Status

- repo-green: `missing-artifact` (exit `1`)
- certi vendor-green: `missing-artifact` (exit `1`)
- pitch vendor-green: `missing-artifact` (exit `1`)

## Known Gaps

- `certi-save-restore`: classification `known-gap`, status `not-promoted`, file `artifacts/vendor_gap_profiles/certi-save-restore.json`
  - next: `./tools/certi-easy preflight`
  - next: `./tools/certi-easy save-restore-probe`
  - next: `./tools/certi-easy save-restore-review 5`
- `certi-ddm`: classification `known-gap`, status `not-promoted`, file `artifacts/vendor_gap_profiles/certi-ddm.json`
  - next: `./tools/certi-easy preflight`
  - next: `./tools/certi-easy ddm-probe`
  - next: `./tools/certi-easy ddm-review 5`
- `pitch-save-restore`: classification `known-gap`, status `not-promoted`, file `artifacts/vendor_gap_profiles/pitch-save-restore.json`
  - next: `./tools/pitch preflight`
  - next: `./tools/pitch save-restore-probe`
  - next: `./tools/pitch save-restore-review 5`
- `pitch-ddm`: classification `known-gap`, status `not-promoted`, file `artifacts/vendor_gap_profiles/pitch-ddm.json`
  - next: `./tools/pitch preflight`
  - next: `./tools/pitch ddm-probe`
  - next: `./tools/pitch ddm-review 5`
- `pitch-negotiated`: classification `known-gap`, status `bridge-divergent`, file `artifacts/vendor_gap_profiles/pitch-negotiated.json`
  - next: `./tools/pitch preflight`
  - next: `./tools/pitch negotiated-probe`
  - next: `./tools/pitch negotiated-review 5`
- `pitch-lost-federate`: classification `known-gap`, status `backend-split`, file `artifacts/vendor_gap_profiles/pitch-lost-federate.json`
  - operator-state: `environment-blocked`
  - blocker: The canonical ./tools/pitch lost-federate-probe lane is currently blocked on this surface because Docker is unreachable and the required CRC/FedPro loopback ports are not permitted.
  - next: `./tools/pitch preflight`
  - next: `./tools/pitch lost-federate-probe`
  - next: `./tools/pitch lost-federate-review 5`
  - artifact: `artifacts/preflight_artifacts/pitch-preflight.json`
  - artifact: `artifacts/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json`
  - artifact: `artifacts/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_report.md`

## Probe Stability

- `certi-save-restore-probe`: no stability artifact is currently present
- `certi-ddm-probe`: no stability artifact is currently present
- `pitch-save-restore-probe`: no stability artifact is currently present
- `pitch-ddm-probe`: no stability artifact is currently present
- `pitch-negotiated-probe`: no stability artifact is currently present
- `pitch-time-window-probe`: stable `True`, success `5` / attempts `5`, promotion `candidate`, file `artifacts/vendor_probe_stability/pitch-time-window-probe/vendor_probe_stability_summary.json`
- `pitch-time-window-restore-state-probe`: stable `True`, success `5` / attempts `5`, promotion `candidate`, file `artifacts/vendor_probe_stability/pitch-time-window-restore-state-probe/vendor_probe_stability_summary.json`
- `pitch-lost-federate-probe`: no stability artifact is currently present

## Promotion Review

- candidate count: `2`
- `certi-save-restore-probe`: decision `missing-evidence`, readiness `missing`, docs `docs/backend_conformance_matrix.md`
  - next: ./tools/certi-easy save-restore-review 5
- `certi-ddm-probe`: decision `missing-evidence`, readiness `missing`, docs `docs/backend_conformance_matrix.md`
  - next: ./tools/certi-easy ddm-review 5
- `pitch-save-restore-probe`: decision `missing-evidence`, readiness `missing`, docs `packages/hla-vendor-pitch/docs/pitch_decision_tree.md`
  - next: ./tools/pitch save-restore-review 5
- `pitch-ddm-probe`: decision `missing-evidence`, readiness `missing`, docs `packages/hla-vendor-pitch/docs/pitch_decision_tree.md`
  - next: ./tools/pitch ddm-review 5
- `pitch-negotiated-probe`: decision `missing-evidence`, readiness `missing`, docs `packages/hla-vendor-pitch/docs/pitch_decision_tree.md`
  - next: ./tools/pitch negotiated-review 5
- `pitch-time-window-probe`: decision `candidate-review`, readiness `candidate`, docs `packages/hla-vendor-pitch/docs/pitch_decision_tree.md`
  - next: compare pitch-time-window-probe against packages/hla-vendor-pitch/docs/pitch_decision_tree.md and promote only if clause-level parity is now defensible
- `pitch-time-window-restore-state-probe`: decision `candidate-review`, readiness `candidate`, docs `packages/hla-vendor-pitch/docs/pitch_decision_tree.md`
  - next: compare pitch-time-window-restore-state-probe against packages/hla-vendor-pitch/docs/pitch_decision_tree.md and promote only if clause-level parity is now defensible

## Packet Files

- JSON summary: `vendor_parity_artifacts_summary.json`
- Artifact manifest CSV: `vendor_parity_artifacts_manifest.csv`
- Markdown report: `vendor_parity_artifacts_report.md`
