# SISO Pitch Micro Parity

Use this when you want only the Pitch-eligible `micro-2` rows from the SISO
runtime showcase.

## Front Door

- `./tools/fom-siso-pitch-micro-parity`
- `./tools/fom-siso-pitch-2010-micro-strict`

Generated artifacts land under:

- `artifacts/siso_pitch_micro_parity/siso_pitch_micro_parity_summary.json`
- `artifacts/siso_pitch_micro_parity/siso_pitch_micro_parity_results.csv`
- `artifacts/siso_pitch_micro_parity/siso_pitch_micro_parity_manifest.json`
- `artifacts/siso_pitch_micro_parity/siso_pitch_micro_parity_report.md`

Promote into `analysis/...` only when you want to retain and cite a specific
packet.

## Included Rows

This runner selects only:

- `Link 16`, `RPR`, `Space`
- `micro-2` only
- `2010` on `pitch-jpype` and `pitch-py4j`
- `2025` on `pitch-202x-jpype` and `pitch-202x-py4j`

That yields 12 backend/scenario attempts.

## Boundary

- `pitch-jpype` and `pitch-py4j` are real 2010 vendor-runtime rows.
- `pitch-202x-jpype` and `pitch-202x-py4j` are bounded adapter rows over the
  repo Python 2025 runtime.
- Do not treat the `202X` rows as IEEE `1516.1-2025` vendor conformance.

## Strict 2010 Lane

Use `./tools/fom-siso-pitch-2010-micro-strict` when you want only the six real
Pitch 2010 micro rows:

- `3` SISO families
- `2` real Pitch backends
- no bounded `202X` adapter rows

This lane fails fast if Pitch preflight is not confirmed through
`./tools/pitch preflight`.
