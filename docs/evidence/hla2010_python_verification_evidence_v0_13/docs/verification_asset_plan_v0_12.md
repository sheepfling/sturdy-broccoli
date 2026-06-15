# v0.12 verification asset plan

This plan is generated from `hla2010.verification.build_verification_plan()` and is intended to separate implemented evidence from known gaps.

Scope: **Pure Python RTI plus Java adapter/shim compatibility layer**

## Summary

```json
{
  "asset_count": 11,
  "gap_asset_ids": [
    "REQ-MOM-NEG-001",
    "REQ-MOM-REPORT-001",
    "REQ-MOM-SERVICE-001",
    "REQ-SERVICE-FILE-001",
    "REQ-TIME-ORDER-001",
    "REQ-SAVE-RESTORE-001",
    "SCENARIO-TARGET-RADAR-001",
    "ASSET-CONFORMANCE-MATRIX-001",
    "ASSET-CROSS-RTI-BRIDGE-001",
    "ASSET-NEGATIVE-MOM-MATRIX-001"
  ],
  "scope": "Pure Python RTI plus Java adapter/shim compatibility layer",
  "sections": [
    "IEEE 1516.1-2010 Annex G",
    "IEEE 1516.1-2010 Java binding",
    "1516.1-2010 \u00a711.2",
    "1516.1-2010 \u00a711.3",
    "1516.1-2010 \u00a711.4.1",
    "1516.1-2010 \u00a711.5",
    "1516.1-2010 \u00a74",
    "1516.1-2010 \u00a74-\u00a710",
    "1516.1-2010 \u00a74.16-\u00a74.25",
    "1516.1-2010 \u00a75",
    "1516.1-2010 \u00a76",
    "1516.1-2010 \u00a78",
    "1516.1-2010 \u00a78.1",
    "1516.1-2010 \u00a78.13",
    "1516.1-2010 \u00a78.16",
    "1516.1-2010 \u00a78.18",
    "1516.1-2010 \u00a79"
  ],
  "status_counts": {
    "gap": 1,
    "implemented-slice": 8,
    "implemented-smoke": 1,
    "planned": 1
  },
  "version": "0.12.0"
}
```

## Assets

### REQ-MOM-TABLE-001: MOM object and interaction exposure is derived from the active MIM/FOM catalog

Status: `implemented-slice`  
Type: `requirement`  
Sections: IEEE 1516.1-2010 §11.2, IEEE 1516.1-2010 §11.3, IEEE 1516.1-2010 Annex G

Evidence:
- `hla2010/mom_catalog.py::build_mom_exposure_model`
- `tests/test_mom_catalog_validation_v012.py::test_mom_catalog_is_derived_from_standard_mim_and_exposes_validation_matrix`

Notes: The active catalog now drives MOM object attributes, interaction parameters, request/report pairs, direction, and matrix output.

### REQ-MOM-NEG-001: Strict MOM decoding reports and raises for representative unknown, missing, direction, and bad-encoding paths

Status: `implemented-slice`  
Type: `requirement`  
Sections: IEEE 1516.1-2010 §11.4.1, IEEE 1516.1-2010 §11.5

Evidence:
- `tests/test_mom_catalog_validation_v012.py::test_strict_mom_missing_required_parameter_reports_and_raises`
- `tests/test_mom_catalog_validation_v012.py::test_strict_mom_rejects_invalid_boolean_payload_and_accepts_valid_service_reporting_adjust`
- `tests/test_mom_catalog_validation_v012.py::test_strict_mom_rejects_federate_sent_report_interaction`
- `verification/mom_negative_matrix_v0_12.json`

Gaps / caveats:
- The generated matrix is complete for planning, but the executable suite samples representative cases rather than every generated row.

### REQ-MOM-REPORT-001: MOM reports use the exact parameter names declared in the active MIM catalog

Status: `implemented-slice`  
Type: `requirement`  
Sections: IEEE 1516.1-2010 §11.3, IEEE 1516.1-2010 §11.4.1, IEEE 1516.1-2010 Annex G

Evidence:
- `tests/test_mom_catalog_validation_v012.py::test_mom_report_payload_uses_exact_mim_catalog_parameters`

Gaps / caveats:
- Report payload values are still local-process diagnostics for several specialized report classes.

### REQ-MOM-SERVICE-001: MOM HLAservice interactions are modeled as RTI-received actions with negative-path service failure reporting

Status: `implemented-slice`  
Type: `requirement`  
Sections: IEEE 1516.1-2010 §11.3, IEEE 1516.1-2010 §11.4.1

Evidence:
- `hla2010/backends/python_rti.py::_run_mom_service_action`
- `verification/mom_negative_matrix_v0_12.json`

Gaps / caveats:
- Not every Annex G service action has a complete semantic implementation yet.

### REQ-SERVICE-FILE-001: Service-report file output contains initial and per-service records with section anchors

Status: `implemented-slice`  
Type: `requirement`  
Sections: IEEE 1516.1-2010 §11.5

Evidence:
- `hla2010/service_reporting.py`
- `tests/test_compliance_slice_v011.py::test_mom_service_reports_to_file_and_global_report_file`

Gaps / caveats:
- The current format is JSONL for auditability; exact vendor/report-file formatting is not claimed.

### REQ-TIME-ORDER-001: Timestamp-order queues respect local GALT/LITS-style lower-bound rules and DDM filtering before delivery

Status: `implemented-slice`  
Type: `requirement`  
Sections: IEEE 1516.1-2010 §8.1, IEEE 1516.1-2010 §8.13, IEEE 1516.1-2010 §8.16, IEEE 1516.1-2010 §8.18, IEEE 1516.1-2010 §9

Evidence:
- `hla2010/time_management.py`
- `tests/test_compliance_slice_v011.py::test_ddm_region_filtering_applies_before_timestamp_order_delivery`

Gaps / caveats:
- The distributed-time algorithm remains a local-process approximation, not a proven multi-process LBTS algorithm.

### REQ-SAVE-RESTORE-001: Save/restore coordinates with time-state and restores logical-time state

Status: `implemented-slice`  
Type: `requirement`  
Sections: IEEE 1516.1-2010 §4.16-§4.25, IEEE 1516.1-2010 §8

Evidence:
- `tests/test_compliance_slice_v011.py::test_scheduled_save_waits_for_time_and_restore_reinstates_time_state`

Gaps / caveats:
- External persistent save-file interchange is not implemented.

### SCENARIO-TARGET-RADAR-001: Two-federate Target/Radar simulation runs over Python RTI and Java shim profiles

Status: `implemented-smoke`  
Type: `scenario`  
Sections: IEEE 1516.1-2010 §4, IEEE 1516.1-2010 §5, IEEE 1516.1-2010 §6, IEEE 1516.1-2010 §8

Evidence:
- `examples/target_radar_simulation.py`
- `tests/test_target_radar_scenario.py`
- `test_run_summary.txt`

Gaps / caveats:
- Scenario is a smoke demonstration, not a conformance test.

### ASSET-CONFORMANCE-MATRIX-001: Service-by-service conformance matrix covering all generated RTIambassador methods and all FederateAmbassador callbacks

Status: `planned`  
Type: `planned-artifact`  
Sections: IEEE 1516.1-2010 §4-§10

Evidence:
- `analysis/python_rti_coverage.json`
- `analysis/python_rti_compliance_v0_12.json`

Gaps / caveats:
- Needs expected exception/state transitions for every service overload.

### ASSET-CROSS-RTI-BRIDGE-001: Cross-run verification against at least one real Java RTI via JPype and Py4J

Status: `gap`  
Type: `planned-artifact`  
Sections: IEEE 1516.1-2010 Java binding, IEEE 1516.1-2010 §4-§10

Evidence:
- `tests/test_optional_real_java_bridges.py`

Gaps / caveats:
- No vendor RTI, jpype1, or py4j package is available in this sandbox.

### ASSET-NEGATIVE-MOM-MATRIX-001: Generated negative-path test cases for each MOM HLAadjust/HLArequest/HLAservice parameter set

Status: `implemented-slice`  
Type: `planned-artifact`  
Sections: IEEE 1516.1-2010 §11.4.1, IEEE 1516.1-2010 Annex G

Evidence:
- `verification/mom_negative_matrix_v0_12.json`
- `hla2010/mom_catalog.py::build_negative_matrix`

Gaps / caveats:
- The matrix is generated; exhaustive parameterized execution remains the next verification slice.

