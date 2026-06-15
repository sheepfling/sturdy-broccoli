# hla2010-rti-certi

CERTI RTI backend plugin package.

This package now contains the CERTI transport adapter, CERTI runtime discovery
helpers, and native CERTI backend plugin under `src/hla2010_rti_certi/`.
Package-owned verification and preflight policy helpers live in
`src/hla2010_rti_certi/testing_policy.py`.
Package-owned split-package and real-runtime wrapper coverage lives in
`tests/test_rti_certi_split_package.py`,
`tests/vendors/test_certi_real_backend_exchange_matrix.py`,
`tests/vendors/test_certi_real_backend_ownership_matrix.py`, and
`tests/vendors/test_certi_real_backend_time_matrix.py`.

New CERTI-specific code should import from `hla2010_rti_certi`.
The human operator surface for CERTI stays `./tools/certi-easy`; this package
does not add a package-local command.

Bootstrap the repo root Python environment before you add CERTI runtime work:

```bash
./tools/bootstrap python
source .venv/bin/activate
```

Then follow the vendor-runtime order in
[`../../docs/python_environment.md`](../../docs/python_environment.md).
