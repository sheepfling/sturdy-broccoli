# Repo seed scope

Included:

- Python package code under `src/hla2010/`;
- examples and FOM XML examples;
- pytest source tests;
- Java shim source and build script, excluding built jars;
- source/reference IEEE PDFs and ZIPs supplied by the user;
- concise project notes.

Excluded:

- generated `analysis/` outputs;
- generated `verification/` packets/assets;
- historical `hla2010_python_scaffold_v*.zip` archives;
- `test_run_summary.txt` files;
- built Java `.jar` files;
- caches and temporary files.

To regenerate verification or conformance assets later, use the package modules and tests rather than committing generated packets into the fresh seed.
