# Vendor Probe Promotion Review

- candidate count: `2`

| Profile | Vendor | Area | Readiness | Decision | Attempts | Docs |
| --- | --- | --- | --- | --- | ---: | --- |
| certi-save-restore-probe | certi | save_restore | missing | missing-evidence |  | docs/backend_conformance_matrix.md |
| certi-ddm-probe | certi | ddm | missing | missing-evidence |  | docs/backend_conformance_matrix.md |
| pitch-save-restore-probe | pitch | save_restore | missing | missing-evidence |  | packages/hla-vendor-pitch/docs/pitch_decision_tree.md |
| pitch-ddm-probe | pitch | ddm | missing | missing-evidence |  | packages/hla-vendor-pitch/docs/pitch_decision_tree.md |
| pitch-negotiated-probe | pitch | negotiated_ownership | missing | missing-evidence |  | packages/hla-vendor-pitch/docs/pitch_decision_tree.md |
| pitch-time-window-probe | pitch | time_window_future_exclusion | candidate | candidate-review | 5 | packages/hla-vendor-pitch/docs/pitch_decision_tree.md |
| pitch-time-window-restore-state-probe | pitch | time_window_restore_state | candidate | candidate-review | 5 | packages/hla-vendor-pitch/docs/pitch_decision_tree.md |

- `certi-save-restore-probe`: no repeated-run stability artifact is present
  - next: ./tools/certi-easy save-restore-review 5
- `certi-ddm-probe`: no repeated-run stability artifact is present
  - next: ./tools/certi-easy ddm-review 5
- `pitch-save-restore-probe`: no repeated-run stability artifact is present
  - next: ./tools/pitch save-restore-review 5
- `pitch-ddm-probe`: no repeated-run stability artifact is present
  - next: ./tools/pitch ddm-review 5
- `pitch-negotiated-probe`: no repeated-run stability artifact is present
  - next: ./tools/pitch negotiated-review 5
- `pitch-time-window-probe`: repeated-run stability evidence exists; perform clause-level parity review before promotion
  - next: compare pitch-time-window-probe against packages/hla-vendor-pitch/docs/pitch_decision_tree.md and promote only if clause-level parity is now defensible
- `pitch-time-window-restore-state-probe`: repeated-run stability evidence exists; perform clause-level parity review before promotion
  - next: compare pitch-time-window-restore-state-probe against packages/hla-vendor-pitch/docs/pitch_decision_tree.md and promote only if clause-level parity is now defensible
