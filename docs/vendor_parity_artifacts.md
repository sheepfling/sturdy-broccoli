# Vendor Parity Artifacts

Use the harmonized vendor parity packet when you want one index over the
current vendor smoke commands, vendor matrix tests, runbooks, findings notes,
and optional preflight JSON snapshots.

Generate the packet with:

```bash
python3 scripts/run_vendor_parity_artifacts.py
```

Default output:

- `analysis/vendor_parity_artifacts/vendor_parity_artifacts_summary.json`
- `analysis/vendor_parity_artifacts/vendor_parity_artifacts_manifest.csv`
- `analysis/vendor_parity_artifacts/vendor_parity_artifacts_report.md`

The packet does not run vendor smoke by itself. It normalizes the current
artifact surface so a follow-on CERTI or Pitch run can be attached to a stable
manifest instead of being reconstructed from scattered docs and scripts.

Typical sequence:

```bash
./certi-easy preflight --json-file analysis/preflight_artifacts/certi-preflight.json
./pitch preflight --json-file analysis/preflight_artifacts/pitch-preflight.json
./scripts/ci/vendor_edge_matrix.sh all
python3 scripts/run_vendor_parity_artifacts.py
```
