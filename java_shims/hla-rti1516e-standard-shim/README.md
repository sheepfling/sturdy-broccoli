# HLA-X Java 2010 Standard Shim

This artifact is the first Rosetta standard shim target. It builds a Java RTI
shim jar against the official IEEE 1516.1-2010 Java API bundle retained under
`specs/`.

The supported claim is deliberately narrow:

- surface-backed by the official Java API
- core scenario subset implemented
- unsupported services generated and reported
- not a full RTI conformance claim

Build from the repository root:

```sh
./tools/hla-x build java-standard-2010
```

The jar is written to:

```text
build/rosetta/java-standard-2010/hla-x-rti1516e-java-shim.jar
```
