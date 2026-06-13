# Backend Decision Tree

Use this page when you need one quick routing choice instead of the full matrix.

## Decision Tree

Need to learn the API or run the first working scenario?
-> `python`

Need a local multi-federate development backend?
-> `python`

Need a process boundary without a vendor runtime?
-> `python` + hosted transport (`grpc` or `rest`)

Need to debug Java bridge mechanics only?
-> `java-shim-jpype` or `java-shim-py4j`

Need to attach to a real Java RTI from one Python process?
-> `jpype`

Need to attach to a real Java RTI through a separate gateway process?
-> `py4j`

Need a real CERTI runtime?
-> bootstrap Python first, then `./tools/certi-easy preflight`

Need a real Pitch runtime?
-> bootstrap Python first, then `./tools/pitch preflight`

Need a real Portico runtime?
-> bootstrap Python first, then add `jpype` or `py4j` extras and a real Portico install

## Rules

- If you are unsure, use `python`.
- Do not make JPype or Py4J your first-run path.
- Do not start with vendor installs before the Python RTI path is green.
- Use Java shim routes for bridge validation, not as evidence of vendor-runtime behavior.

## Read Next

1. [java_backends_quickstart.md](java_backends_quickstart.md)
2. [install_matrix.md](install_matrix.md)
3. [rti_options_and_test_matrix.md](rti_options_and_test_matrix.md)
