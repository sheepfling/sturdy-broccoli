# hla2010-rti-certi

CERTI RTI backend plugin package.

This package now contains the CERTI transport adapter, CERTI runtime discovery
helpers, and CERTI Java bridge adapter glue under `src/hla2010_rti_certi/`.

The old paths remain as compatibility facades:

- `hla2010.backends.certi`
- `hla2010.backends.certi_java`
- `hla2010.real_rti_certi`

New CERTI-specific code should import from `hla2010_rti_certi`.

Bootstrap the repo root Python environment before you add CERTI runtime work:

```bash
./scripts/bootstrap_profile.sh python
source .venv/bin/activate
```

Then follow the vendor-runtime order in
[`../../docs/python_environment.md`](../../docs/python_environment.md).
