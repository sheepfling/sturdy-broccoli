# Python RTI vs Pitch Overlap Evidence (2026-06-07)

## Purpose

This note compares the current evidence for the in-repo Python RTI against the
Docker-backed Pitch pRTI Java route after the real Pitch bridge matrix was
stabilized.

The comparison is intentionally limited to what was actually re-run in this
workspace on 2026-06-07.

## Commands Run

### Python RTI evidence path

```bash
python3 scripts/run_two_federate_suite.py --output-dir analysis/python_two_federate_suite_2026-06-07
python3 -m pytest -q tests/test_real_rti.py
```

### Real Pitch evidence path

```bash
HLA2010_ENABLE_REAL_RTI_SMOKE=1 \
HLA2010_PITCH_CRC_MODE=docker \
HLA2010_PITCH_DOCKER_BUILD=0 \
python3 -m pytest -q tests/test_pitch_real_backend_matrix.py -rs
HLA2010_ENABLE_REAL_RTI_SMOKE=1 \
HLA2010_PITCH_CRC_MODE=docker \
HLA2010_PITCH_DOCKER_BUILD=0 \
python3 -m pytest -q tests/test_real_vendor_runtime_smoke.py -k pitch -rs
```

## Results

- Python two-federate suite artifacts generated successfully under
  `analysis/python_two_federate_suite_2026-06-07/`.
- `tests/test_real_rti.py`: `21 passed in 0.88s`
- Real Pitch matrix: `7 passed, 1 warning in 104.99s`
- Real Pitch smoke: `4 passed, 6 deselected in 54.99s`

## Evidence Comparison

### Python RTI currently has broader executable evidence

The generated Python suite report at
[two_federate_suite_report.md](../../../analysis/python_two_federate_suite_2026-06-07/two_federate_suite_report.md)
shows seven exercised scenario slices:

- `exchange_time`
- `synchronization`
- `ownership`
- `negotiated_ownership`
- `save_restore`
- `ddm`
- `target_radar`

That means the Python RTI remains ahead on breadth of locally executable
scenario coverage, especially for:

- negotiated ownership
- save/restore
- DDM region filtering
- the artifact-rich target/radar flow

### Pitch now gives external confirmation on a narrower promoted overlap

The real Pitch smoke at
[test_real_vendor_runtime_smoke.py](tests/test_real_vendor_runtime_smoke.py)
and the real Pitch matrix at
[test_pitch_real_backend_matrix.py](tests/test_pitch_real_backend_matrix.py)
now prove the Java/vendor route for:

- lifecycle on `pitch-jpype`
- lifecycle on `pitch-py4j`
- two-federate exchange plus time-managed timestamp delivery on `pitch-jpype`
- two-federate exchange plus time-managed timestamp delivery on `pitch-py4j`
- two-federate synchronization on `pitch-jpype`
- two-federate synchronization on `pitch-py4j`
- unconditional divestiture plus acquisition-if-available ownership flow on `pitch-jpype`
- unconditional divestiture plus acquisition-if-available ownership flow on `pitch-py4j`

The normalized overlap bundle is recorded in:

- [normalized_overlap.json](analysis/python_pitch_overlap_2026-06-07/normalized_overlap.json)
- [normalized_overlap.md](analysis/python_pitch_overlap_2026-06-07/normalized_overlap.md)

The real negotiated-ownership probe now also exists in
[test_pitch_real_backend_matrix.py](tests/test_pitch_real_backend_matrix.py),
but it currently skips as not yet promotable rather than proving `7.8`,
`7.11`, `7.13`, `7.15`, or `7.16`.

The newer diagnostic evidence now sharpens that statement: Pitch negotiated
ownership is currently bridge-divergent rather than uniformly absent. The
Docker-backed runs show different partial callback sequences on `pitch-jpype`
and `pitch-py4j`; see:

- [pitch_negotiated_ownership_vendor_bug_2026-06-07.md](../../packages/hla2010-rti-pitch-common/docs/evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md)
- [diagnostic_summary.md](analysis/pitch_negotiated_ownership_2026-06-07/diagnostic_summary.md)

This is the important external evidence that the same Python-facing API can
drive a certified HLA 1516-2010 RTI, not just the in-memory reference RTI.

## Current Assessment

- Python RTI is stronger on scenario breadth and development-time evidence.
- Pitch is stronger as external runtime confirmation for the overlap that has
  now been proven end to end.
- The strongest honest claim today is:
  Python RTI has broader local executable behavior coverage, while Pitch now
  validates the core Java/vendor route for exchange/time, synchronization, and
  basic ownership semantics over both Java bridge paths.

That is parity on the promoted overlap, not blanket parity for the full
1516.1 surface. Negotiated ownership still remains bridge-divergent.

## Open Path

The next comparison step should still avoid overclaiming.
The remaining honest gap is:

1. keep `save_restore`, `ddm`, `negotiated_ownership`, and `target_radar` as
   Python-led evidence until Pitch-side runtime probes are equally stable;
2. promote additional Pitch ownership clauses only when the real vendor route
   proves negotiated acquisition and cancellation paths, not just the
   acquisition-if-available path.
