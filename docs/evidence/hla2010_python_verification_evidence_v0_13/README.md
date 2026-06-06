# HLA 2010 Python RTI Verification Evidence Pack v0.13

This pack collects the verification evidence generated during the HLA 2010 Python RTI scaffold work. It is intentionally separate from the clean repo seed so generated verification outputs do not pollute the initial repository layout.

## Contents

- `analysis/` — generated API inventories, Java/C++ method inventories, section traceability, service conformance matrices, MOM negative-path matrices, and compliance-delta JSON.
- `verification/` — generated verification plan, traceability CSVs, MOM negative matrices, and service conformance CSV.
- `tests/` — executable pytest assets, including API traceability, MOM catalog validation, generated MOM negative tests, service conformance matrix tests, time/FOM/startup/sync tests, and Target/Radar smoke tests.
- `docs/` — human-readable design and compliance notes from the v0.8-v0.13 development slices.
- `hla2010/` and `tools/` — selected verification-generation source modules and scripts used to produce the matrices.
- `source_docs/` — manifests documenting the source standards and repo-seed scope. The IEEE PDFs/ZIPs remain in the repo seed/specs folder rather than being duplicated here.

## Important caveat

This is evidence of progress, not proof of full standard certification. The matrices expose gaps deliberately. At v0.13 the evidence shows broad API traceability and substantial executable negative-path coverage, but it does not establish perfect compliance, perfect semantic equivalence to all Java/C++ RTI behaviors, or certification by IEEE/SISO/vendor conformance tools.
