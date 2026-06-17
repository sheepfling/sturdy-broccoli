from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PITCH_BUNDLES: dict[str, tuple[str, ...]] = {
    "pitch-negotiated-ownership": (
        "packages/hla-vendor-pitch/docs/evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_negotiated_ownership_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_negotiated_divesting_offer_probe",
    ),
    "pitch-lost-federate": (
        "packages/hla-vendor-pitch/docs/evidence/pitch_clause4_lost_federate_gap_2026-06-11.md",
        "packages/hla-verification/src/hla/verification/scenario_lost_federate.py::run_external_lost_federate_observer_scenario",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lost_federate_mom_matrix",
    ),
    "pitch-time-management": (
        "packages/hla-vendor-pitch/docs/evidence/pitch_section8_time_management_vendor_divergence_2026-06-11.md",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_logical_time_query_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_time_bound_query_matrix",
    ),
    "pitch-transport-subset": (
        "packages/hla-vendor-pitch/docs/evidence/pitch_transport_subset_vendor_divergence_2026-06-11.md",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_transportation_type_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_transportation_type_rejection_matrix",
    ),
}
