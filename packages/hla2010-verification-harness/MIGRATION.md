# hla2010-verification-harness Migration

Canonical generic verification harness ownership now lives under:

- `src/hla2010_verification_harness/two_federate_suite_pairs.py`
- `src/hla2010_verification_harness/two_federate_suite_types.py`
- `src/hla2010_verification_harness/two_federate_suite_timeline.py`
- `src/hla2010_verification_harness/two_federate_suite_summary.py`
- `src/hla2010_verification_harness/two_federate_suite_writers.py`

The root `src/hla2010/testing/` modules remain as compatibility facades while
callers move toward the split package imports.
