# hla2010-verification-harness Migration

Canonical generic verification harness ownership now lives under:

- `src/hla2010_verification_harness/scenario_support.py`
- `src/hla2010_verification_harness/scenario_basic.py`
- `src/hla2010_verification_harness/scenario_exchange.py`
- `src/hla2010_verification_harness/scenario_exchange_history.py`
- `src/hla2010_verification_harness/scenario_sync.py`
- `src/hla2010_verification_harness/scenario_ownership.py`
- `src/hla2010_verification_harness/two_federate_suite_pairs.py`
- `src/hla2010_verification_harness/two_federate_suite_types.py`
- `src/hla2010_verification_harness/two_federate_suite_timeline.py`
- `src/hla2010_verification_harness/two_federate_suite_summary.py`
- `src/hla2010_verification_harness/two_federate_suite_writers.py`

The old `src/hla2010/testing/` facade has been removed. Callers should import
generic verification helpers directly from the installable
`hla2010-verification-harness` package.
