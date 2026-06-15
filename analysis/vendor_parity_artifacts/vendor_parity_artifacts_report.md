# Vendor Parity Artifacts

- suite: `vendor-parity-artifacts`
- artifacts indexed: `33`
- required artifacts: `19`
- existing artifacts: `24`
- missing required artifacts: `0`

## Profiles

| Vendor | Profile | Tier | Indexed | Existing | Missing required | Kinds |
| --- | --- | --- | ---: | ---: | ---: | --- |
| shared | shared | shared | 11 | 10 | 0 | script, test, doc, preflight, promotion-review |
| certi | certi-save-restore-probe | probe | 1 | 0 | 0 | stability-summary |
| certi | certi-ddm-probe | probe | 1 | 0 | 0 | stability-summary |
| pitch | pitch-save-restore-probe | probe | 1 | 0 | 0 | stability-summary |
| pitch | pitch-ddm-probe | probe | 1 | 0 | 0 | stability-summary |
| pitch | pitch-negotiated-probe | probe | 1 | 0 | 0 | stability-summary |
| pitch | pitch-lost-federate-probe | probe | 1 | 0 | 0 | stability-summary |
| certi | certi-save-restore | known-gap | 1 | 0 | 0 | gap-profile |
| certi | certi-ddm | known-gap | 1 | 0 | 0 | gap-profile |
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

- `certi`: result `real CERTI runnable`, environment `loopback-ok`, exit `0`, file `analysis/preflight_artifacts/certi-preflight.json`
- `pitch`: result `not ready; fix the blocked prerequisite(s) above and rerun`, environment `ports-blocked`, exit `1`, file `analysis/preflight_artifacts/pitch-preflight.json`

## Runtime Status

- repo-green: `repo-green` (exit `0`)
- certi vendor-green: `vendor-green` (exit `0`)
- pitch vendor-green: `environment-blocked` (exit `1`)

Required markers for `certi` in `repo-green`:
- `active_build_root`: `<repo>/.local/certi/patched/build/libRTI/ieee1516-2010`
- `active_prefix`: `<repo>/.local/certi/patched/install/bin/rtig`
- `patched_build_root`: `<repo>/.local/certi/patched/build/libRTI/ieee1516-2010`
- `patched_prefix`: `<repo>/.local/certi/patched/install/bin/rtig`
- `upstream_build_root`: `<repo>/.local/certi/upstream/build/libRTI/ieee1516-2010`
- `upstream_prefix`: `<repo>/.local/certi/upstream/install/bin/rtig`

Required markers for `pitch` in `repo-green`:
- `runtime_home`: `third_party/pitch/PITCH-prti1516e-manual/lib/prtifull.jar`

Required ports for `pitch` in `repo-green`:
- `crc`: `127.0.0.1:8989` [blocked]
- `fedpro`: `127.0.0.1:15164` [blocked]

Required markers for `certi` in `certi vendor-green`:
- `active_build_root`: `<repo>/.local/certi/patched/build/libRTI/ieee1516-2010`
- `active_prefix`: `<repo>/.local/certi/patched/install/bin/rtig`
- `patched_build_root`: `<repo>/.local/certi/patched/build/libRTI/ieee1516-2010`
- `patched_prefix`: `<repo>/.local/certi/patched/install/bin/rtig`
- `upstream_build_root`: `<repo>/.local/certi/upstream/build/libRTI/ieee1516-2010`
- `upstream_prefix`: `<repo>/.local/certi/upstream/install/bin/rtig`

Required markers for `pitch` in `pitch vendor-green`:
- `runtime_home`: `third_party/pitch/PITCH-prti1516e-manual/lib/prtifull.jar`

Required ports for `pitch` in `pitch vendor-green`:
- `crc`: `127.0.0.1:8989` [blocked]
- `fedpro`: `127.0.0.1:15164` [blocked]

## Known Gaps

- `certi-save-restore`: no known-gap artifact is currently present
- `certi-ddm`: no known-gap artifact is currently present
- `pitch-save-restore`: no known-gap artifact is currently present
- `pitch-ddm`: classification `known-gap`, status `not-promoted`, file `analysis/vendor_gap_profiles/pitch-ddm.json`
  - next: `./tools/pitch preflight`
  - next: `./tools/pitch ddm-probe`
  - next: `./tools/pitch ddm-review 5`
- `pitch-negotiated`: classification `known-gap`, status `bridge-divergent`, file `analysis/vendor_gap_profiles/pitch-negotiated.json`
  - next: `./tools/pitch preflight`
  - next: `./tools/pitch negotiated-probe`
  - next: `./tools/pitch negotiated-review 5`
- `pitch-lost-federate`: classification `known-gap`, status `backend-split`, file `analysis/vendor_gap_profiles/pitch-lost-federate.json`
  - operator-state: `environment-blocked`
  - blocker: The canonical ./tools/pitch lost-federate-probe lane is currently blocked on this surface because Docker is unreachable and the required CRC/FedPro loopback ports are not permitted.
  - next: `./tools/pitch preflight`
  - next: `./tools/pitch lost-federate-probe`
  - next: `./tools/pitch lost-federate-review 5`
  - artifact: `analysis/preflight_artifacts/pitch-preflight.json`
  - artifact: `analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json`
  - artifact: `analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_report.md`

## Probe Stability

- `certi-save-restore-probe`: no stability artifact is currently present
- `certi-ddm-probe`: no stability artifact is currently present
- `pitch-save-restore-probe`: no stability artifact is currently present
- `pitch-ddm-probe`: no stability artifact is currently present
- `pitch-negotiated-probe`: no stability artifact is currently present
- `pitch-lost-federate-probe`: no stability artifact is currently present

## Promotion Review

- no promotion-review artifact is currently present

## Packet Files

- JSON summary: `vendor_parity_artifacts_summary.json`
- Artifact manifest CSV: `vendor_parity_artifacts_manifest.csv`
- Markdown report: `vendor_parity_artifacts_report.md`
