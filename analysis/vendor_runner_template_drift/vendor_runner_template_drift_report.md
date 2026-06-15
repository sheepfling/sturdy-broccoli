# Vendor Runner Template Drift

- template: `docs/vendor_runner_provisioning_template.yaml`
- exit code: `0`

| Profile | OK | Workflow Job | Reason |
| --- | --- | --- | --- |
| certi | yes | .github/workflows/ci.yml:certi-runtime-required | ok |
| pitch | yes | .github/workflows/ci.yml:pitch-runtime-required | ok |
| matrix | yes | .github/workflows/ci.yml:real-profile-matrix-required | ok |
| vendor-edge | yes | .github/workflows/ci.yml:vendor-edge-matrix-required | ok |
| all | yes | .github/workflows/vendor-runtime-smoke.yml:vendor-runtime-smoke | ok |
