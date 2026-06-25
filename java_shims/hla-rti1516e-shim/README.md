# HLA 1516e Java RTI shim

This is a deliberately tiny Java RTI shim for exercising the Python Java backend
adapters. It is not a conforming RTI implementation. It implements only the
small service subset used by `hla.rti1516e.testing.scenarios.run_basic_federate_scenario`:
connection, create/join/resign/destroy, handle lookup, object update callbacks,
interaction callbacks, and basic time-management callbacks.

It also includes a small `hla.rti1516e.encoding` package so JPype/Py4J routes
can prove Java-owned payload encoding without vendor jars. The shim
`EncoderFactory` currently covers:

- `HLAASCIIstring`
- `HLAunicodeString`
- `HLAoctet`
- `HLAopaqueData`
- `HLAfixedRecord`
- `HLAfixedArray`
- `HLAvariableArray`

Build it with:

```bash
python java_shims/hla-rti1516e-shim/tools/build_java_shim.py \
  --output /tmp/hla-rti1516e-shim.jar
```

When `jpype1` or `py4j` is installed, the optional pytest tests use this jar to
exercise the real bridge modules. Without those optional packages, the normal
unit tests use the in-process Java-shaped shim in `hla.rti1516e.testing.java_shim`.
