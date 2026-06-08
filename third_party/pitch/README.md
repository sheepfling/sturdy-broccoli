# Pitch Local Vendor Drop

`third_party/pitch/` is reserved for local Pitch vendor payloads such as:

- `HLA_PITCH_linux.zip`
- `HLA_PITCH_linux/`
- `PITCH-prti1516e-manual/`

Those files are intentionally ignored by Git and must not be committed. The
repo may discover and use a local extraction at
`third_party/pitch/PITCH-prti1516e-manual/`, but that path is local operator
state rather than tracked source.

Use `HLA2010_PITCH_HOME` to point at an external Pitch installation, or place a
local extraction in this directory when running the Pitch launchers and vendor
tests.
