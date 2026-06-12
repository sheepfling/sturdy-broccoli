# Portico Docs

Package-owned Portico runtime and parity notes live here.

This package owns:
- Portico runtime discovery and plugin code under `src/hla2010_rti_portico/`
- package-owned verification/preflight policy in `src/hla2010_rti_portico/testing_policy.py`
- Portico-specific operator notes for `./tools/vendor-green` and related repo vendor lanes

Portico does not currently have the same real-runtime verification depth as
CERTI and Pitch, but its docs surface should still stay package-owned rather
than falling back to root-level backend notes.

Current requirement-disposition boundary:
- [portico_requirement_disposition_policy.md](portico_requirement_disposition_policy.md): package-owned explanation for why the generated Portico family artifacts currently stay `classification-required` for applicable rows
- `analysis/compliance/portico_requirement_disposition.md`: generated family-level disposition packet
- `analysis/compliance/portico-jpype_requirement_disposition.md`: generated JPype-profile disposition packet
- `analysis/compliance/portico-py4j_requirement_disposition.md`: generated Py4J-profile disposition packet

Current shared-harness wrapper tranche:
- `tests/test_rti_portico_split_package.py`: package-split policy and import boundary guard
- `tests/vendors/test_portico_real_backend_matrix.py`: optional real-runtime thin wrappers for the shared exchange and synchronization scenarios over `portico-jpype` and `portico-py4j`
- those wrappers are intentionally not promoted into generated requirement evidence yet; they establish the package-owned test surface needed for future tranche-by-tranche disposition promotion
