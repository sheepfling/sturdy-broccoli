# hla2010-rti-pitch-common

Shared Pitch runtime discovery and launch helpers for hla2010 RTI backend
plugins.

This package owns vendor-specific Pitch runtime concerns such as runtime
discovery, FedPro launch, license listing, local-settings helpers, and Pitch
user-home preparation.
Package-owned verification and preflight policy helpers live in
`src/hla2010_rti_pitch_common/testing_policy.py`.
Package-owned split-package and real-runtime wrapper coverage lives in
`tests/test_rti_pitch_split_packages.py` and
`tests/vendors/test_pitch_real_backend_matrix.py`.
Import the canonical implementation from `hla2010_rti_pitch_common`.

The human operator surface for Pitch stays `./tools/pitch`; this package does
not add a package-local command.
