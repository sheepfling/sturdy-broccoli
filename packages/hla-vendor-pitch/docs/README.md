# Pitch Docs

Vendor-owned Pitch runtime and parity notes live here.

This package owns:
- shared Pitch runtime discovery and launch policy under `src/hla.vendors.pitch/`
- package-owned verification/preflight policy in `src/hla.vendors.pitch/testing_policy.py`
- Pitch-specific operator notes for `./tools/pitch`
- shared Pitch split-package and real-runtime wrapper tests in
  `tests/test_rti_pitch_split_packages.py` and
  `tests/vendors/test_pitch_real_backend_matrix.py`

- [pitch_docker_quickstart.md](pitch_docker_quickstart.md): shortest operator path
- [pitch_decision_tree.md](pitch_decision_tree.md): runtime/interface selection guide
- [pitch_crc_macos_vendor_bug.md](pitch_crc_macos_vendor_bug.md): macOS vendor issue notes
- [evidence/pitch_no_2025_java_surface_probe_2026-06-18.md](evidence/pitch_no_2025_java_surface_probe_2026-06-18.md): direct JVM probe showing Pitch exposes 2010 classes only, not `hla.rti1516_2025`
- [evidence/pitch_clause4_lost_federate_gap_2026-06-11.md](evidence/pitch_clause4_lost_federate_gap_2026-06-11.md): Clause 4.1.5 blocked lost-federate evidence and operator lane notes
- [evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md](evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md): negotiated-ownership divergence notes
- [evidence/pitch_section8_time_management_vendor_divergence_2026-06-11.md](evidence/pitch_section8_time_management_vendor_divergence_2026-06-11.md): Clause 8 next-message and retraction divergence notes
- [evidence/pitch_transport_subset_vendor_divergence_2026-06-11.md](evidence/pitch_transport_subset_vendor_divergence_2026-06-11.md): transportation-type subset divergence notes
