# Verification Summary v0.13

## Service conformance matrix

- Rows: 217
- RTIambassador rows: 162
- FederateAmbassador rows: 55
- Rows with known gaps: 152
- Verification status counts: {'callback-helper-covered': 55, 'focused-executable-tests': 15, 'group-level-slice-tests': 147}

## MOM negative-path matrix

- Total generated cases: 269
- Strict executable cases: 237
- Planned semantic service cases: 32
- MOM interactions inspected: 84
- RTI-received leaf interactions inspected: 53
- Case summary: {'by_execution_level': {'planned-service-semantics': 32, 'rti-strict': 237}, 'by_kind': {'bad_boolean_encoding': 9, 'bad_float_encoding': 1, 'bad_handle_encoding': 74, 'bad_interval_encoding': 2, 'bad_time_encoding': 6, 'missing_parameter_choice': 2, 'missing_required_parameter': 90, 'unexpected_parameter': 53, 'unsupported_or_failed_service_action': 32}, 'case_count': 269, 'section_refs': ['IEEE 1516.1-2010 §11.3', 'IEEE 1516.1-2010 §11.4.1', 'IEEE 1516.1-2010 §11.5', 'IEEE 1516.1-2010 Annex G']}

## Verification asset plan

- Asset count: 13
- Status counts: {'gap': 1, 'implemented-slice': 9, 'implemented-smoke': 1, 'planned': 2}
- Scope: Pure Python RTI plus Java adapter/shim compatibility layer

## Latest recorded test result

The v0.13 run summary recorded `577 passed, 2 skipped`. The skipped tests are the optional real JPype/Py4J bridge tests that require external bridge packages and a vendor RTI.
