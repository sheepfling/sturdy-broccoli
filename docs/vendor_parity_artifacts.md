# Vendor Parity Artifacts

Use the harmonized vendor parity packet when you want one index over the
current vendor smoke commands, vendor matrix tests, runbooks, findings notes,
optional preflight JSON snapshots, and the normalized repo-green versus
vendor-green status derived from those snapshots, plus any explicit known-gap
profiles for currently unpromoted slices like save/restore or DDM.

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

The packet now also embeds:

- repo-green runtime classification
- strict CERTI vendor-green classification
- strict Pitch vendor-green classification
- optional known-gap profiles for explicit unpromoted vendor slices
- optional repeated-run probe stability summaries from dedicated runners
- optional promotion-review summaries over those repeated-run probe slices

The generated packet also classifies profile artifacts and commands by evidence
tier:

- `promoted`: defended vendor lanes such as `certi-compare` or `pitch`
- `probe`: narrow executable runtime probes such as `*-probe`
- `known-gap`: explicit unpromoted operator routes such as `./scripts/pitch_docker_easy.sh negotiated`
- `shared`: repo-wide support artifacts and commands

That means one generated summary can answer both:

- what vendor artifacts exist
- whether the current preflight state is merely blocked by the host or ready for strict vendor execution
- whether a missing vendor slice is still an explicit known gap rather than an absent route
- whether a probe slice has accumulated repeated-run stability evidence yet
- whether any of those repeated-run probe slices are actual promotion-review candidates

Typical sequence:

```bash
./scripts/certi_easy.sh preflight --json-file analysis/preflight_artifacts/certi-preflight.json
./scripts/pitch_docker_easy.sh preflight --json-file analysis/preflight_artifacts/pitch-preflight.json
./scripts/ci/vendor_edge_matrix.sh all
python3 scripts/run_vendor_parity_artifacts.py
```
