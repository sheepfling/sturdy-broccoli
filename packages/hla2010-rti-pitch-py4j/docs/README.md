# Pitch Py4J Docs

Package-owned notes for the `pitch-py4j` backend live here.

- This package owns the `pitch-py4j` plugin descriptor and retained
  package-local compatibility facades under
  `src/hla2010_rti_pitch_py4j/`.
- Package-owned verification/preflight policy for the runtime lane is shared
  deliberately through `hla2010_rti_pitch_common.testing_policy`.
- Split-package guard coverage lives in `tests/test_rti_pitch_split_packages.py`,
  and the shared real-runtime wrapper matrix lives in
  `tests/vendors/test_pitch_real_backend_matrix.py`.
- The human operator surface for this backend stays `./tools/pitch`, not a
  package-local command wrapper.
- Shared Pitch runtime/operator notes stay in
  `../../hla2010-rti-pitch-common/docs/`.
- Generic Py4J bridge implementation notes stay in
  `../../hla2010-rti-java-py4j/`.
