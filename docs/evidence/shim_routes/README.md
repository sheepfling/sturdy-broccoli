# Shim Route Evidence

This family stores generated Java and C++ standard-shim artifact packets plus
the route-trace evidence used by the 2025 closeout-reporting and route-parity views.

Canonical order:

1. Java or C++ standard artifact packet
2. Java toolchain packet
3. route-trace packet

Current contents:

- `java-standard-{2010,2025}.{json,md}`: generated Java standard-shim artifact
  packets
- `cpp-standard-{2010,2025}.{json,md}`: generated C++ standard-shim artifact
  packets
- `java-toolchain.{json,md}`: generated Java discovery and artifact inventory
- [route_traces/README.md](route_traces/README.md): per-route trace packets

Related families:

- [../README.md](../README.md)
- [../java-intake/README.md](../java-intake/README.md)
- [../cpp-intake/README.md](../cpp-intake/README.md)
