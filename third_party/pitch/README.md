# Pitch Local Vendor Drop

`third_party/pitch/` is a local operator drop zone for Pitch vendor material.
It is intentionally not a tracked source tree.

What belongs here:

- `HLA_PITCH_linux.zip`
  The original vendor archive. Some helper scripts can extract this on demand.
- `HLA_PITCH_linux/`
  An unpacked copy of the vendor archive. Helper scripts can copy the runtime
  out of this tree.
- `PITCH-prti1516e-manual/`
  The extracted runtime home used by the repo's Pitch launchers and smoke
  tests.

What does not belong in git:

- vendor jars
- native libraries
- bundled JRE files
- Docker sample payloads unpacked from the vendor bundle
- any other large binary assets from the Pitch distribution

Those files are intentionally ignored by Git and must not be committed.

## Expected Runtime Shape

Most repo tooling expects a runtime home at:

`third_party/pitch/PITCH-prti1516e-manual/`

Typical contents include subdirectories like:

- `lib/`
- `samples/`
- `user.home/`
- `docs/`

## Re-supply Options

Any of these are acceptable:

1. Set `HLA2010_PITCH_HOME` to an external extracted runtime.
2. Place `HLA_PITCH_linux.zip` in this directory and let the helper scripts
   extract it.
3. Place an extracted `HLA_PITCH_linux/` tree here and let the helper scripts
   copy `PITCH-prti1516e-manual/` into place.
4. Place `PITCH-prti1516e-manual/` here directly.

## Fastest Recovery Path

To check whether the repo can see a valid local Pitch runtime:

```bash
./scripts/check_pitch_preflight.sh
```

To exercise the normal operator path after re-supplying the runtime:

```bash
./pitch preflight
./pitch install
./pitch smoke
```

If you are only pointing at an external install, this is enough:

```bash
export HLA2010_PITCH_HOME=/absolute/path/to/PITCH-prti1516e-manual
./pitch preflight
```
