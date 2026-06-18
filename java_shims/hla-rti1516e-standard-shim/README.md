# Java 2010 Standard Shim

This artifact is the first Java standard API shim target. It builds a Java RTI
shim jar against the official IEEE 1516.1-2010 Java API bundle retained under
`specs/`.

The supported claim is deliberately narrow:

- surface-backed by the official Java API
- core scenario subset implemented
- unsupported services generated and reported
- not a full RTI conformance claim

Build from the repository root:

```sh
./tools/shim-routes build java-standard-2010
```

The jar is written to:

```text
build/shim_routes/java-standard-2010/java-rti1516e-standard-shim.jar
```
