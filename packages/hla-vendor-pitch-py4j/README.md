# hla-vendor-pitch-py4j

Pitch Java RTI adapter through Py4J.

This package owns the `pitch-py4j` backend plugin descriptor and Pitch-specific
runtime wiring. Generic Py4J Java bridge mechanics live in
`hla-bridge-java-py4j`.

Verification and preflight policy for this backend is intentionally shared
through `hla.vendors.pitch.testing_policy`.
Split-package guard coverage lives in `tests/test_rti_pitch_split_packages.py`,
and the shared real-runtime wrapper matrix lives in
`tests/vendors/test_pitch_real_backend_matrix.py`.
Import the package from `hla.vendors.pitch.py4j`.

The human operator surface for Pitch stays `./tools/pitch`; this package does
not add a package-local command.
