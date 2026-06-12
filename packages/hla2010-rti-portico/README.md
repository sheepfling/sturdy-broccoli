# hla2010-rti-portico

Portico RTI backend plugin package for `hla2010-spec`.

This package owns Portico runtime discovery plus the JPype and Py4J plugin
descriptors for Portico-backed RTI ambassadors.
Package-owned verification and preflight policy helpers live in
`src/hla2010_rti_portico/testing_policy.py`.
Package-owned split-package and real-runtime wrapper coverage lives in
`tests/test_rti_portico_split_package.py` and
`tests/vendors/test_portico_real_backend_matrix.py`.
Import the canonical implementation from `hla2010_rti_portico`.

The human operator surface for Portico stays `./tools/vendor-green`; this
package does not add a package-local command.
