# Agent Acceptance Checklist

- [ ] Packet unpacked into the repository using the recommended layout.
- [ ] Canonical v1.0 files are placed under `requirements/latest`.
- [ ] Historical tranche files are placed under `requirements/history`.
- [ ] Carried-forward API/MIM/XSD/WSDL catalogs are placed under `requirements/catalogs`.
- [ ] `MANIFEST.json` committed and checksum validation added.
- [ ] Requirements schema documented.
- [ ] Requirements lint test validates required columns and unique IDs.
- [ ] Verification matrix lint test validates all referenced `requirement_id` values exist.
- [ ] Clause tracker lint test confirms all major IEEE 1516, 1516.1, and 1516.2 clauses are represented.
- [ ] Generated markdown documentation can be produced from the catalog.
- [ ] Clause 4 and Clause 5 implementation tests include requirement IDs.
- [ ] CI runs requirements linting before implementation tests.
- [ ] Source standards PDFs/zip artifacts are excluded from public distribution unless license permits.
