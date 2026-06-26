# C++ Toolchain

Use this page when the agent or a human needs to confirm the local C++ setup
for standard shim builds, C++ route certification, or SDK capsule work.

## Front Door

Run:

```sh
./tools/shim-routes cpp doctor
```

That command reports:

- whether `c++`, `ar`, and `cmake` are available
- whether the 2010 and 2025 standard shim archives already exist
- which build command to run next when an archive is missing

It also writes a machine-readable inventory and a Markdown summary under:

- `docs/evidence/shim_routes/cpp-toolchain.json`
- `docs/evidence/shim_routes/cpp-toolchain.md`

`./tools/bootstrap doctor` also includes a summarized `cpp_toolchain` row for
the broader workspace preflight, but `./tools/shim-routes cpp doctor` is the
route-specific source of truth.

## Required Tools

For the repo-owned standard shim builds, the required host tools are:

- `c++`
- `ar`

For profile-based C++ SDK capsule generation and smoke checks, you also need:

- `cmake`

## Shim Artifacts

The canonical C++ shim artifacts are:

- `build/shim_routes/cpp-standard-2010/librti1516e_standard_cpp_shim.a`
- `build/shim_routes/cpp-standard-2025/librti1516_2025_standard_cpp_shim.a`

If either archive is missing, the inventory tells you the exact build command to
run:

- `./tools/shim-routes build cpp-standard-2010`
- `./tools/shim-routes build cpp-standard-2025`

## Related Docs

- [language_shim_routes.md](language_shim_routes.md)
- [vendor_runtime_runner_guide.md](vendor_runtime_runner_guide.md)
- [../packages/hla-backend-cpp-shim/src/hla/backends/cpp_shim/cpp_intake.py](../packages/hla-backend-cpp-shim/src/hla/backends/cpp_shim/cpp_intake.py)
