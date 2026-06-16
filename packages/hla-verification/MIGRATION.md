# hla-verification Migration

Canonical generic verification harness ownership now lives under:

- `src/hla.verification/scenario_support.py`
- `src/hla.verification/scenario_basic.py`
- `src/hla.verification/scenario_exchange.py`
- `src/hla.verification/scenario_exchange_history.py`
- `src/hla.verification/scenario_sync.py`
- `src/hla.verification/scenario_ownership.py`
- `src/hla.verification/two_federate_suite_pairs.py`
- `src/hla.verification/two_federate_suite_types.py`
- `src/hla.verification/two_federate_suite_timeline.py`
- `src/hla.verification/two_federate_suite_summary.py`
- `src/hla.verification/two_federate_suite_writers.py`

The old `src/hla2010/testing/` facade has been removed. Callers should import
generic verification helpers directly from the installable
`hla-verification` package.
