# Package Dependency Tree

This page is generated from the `project.dependencies` fields in
`packages/*/pyproject.toml`.

Regenerate it with:

```bash
./tools/package-deps generate
```

## Summary

- `hla2010-spec` is the single true root package.
- `hla2010-rti-backend-common`, `hla2010-rti-runtime-common`, `hla2010-rti-transport-common`, and `hla2010-verification-harness` are the shared support layers.
- Python and Java backend families are separated; `hla2010-rti-python` depends on backend-common rather than on Java support packages.
- transport packages depend only on `hla2010-spec` plus `hla2010-rti-transport-common`.
- FOM and verification leaf packages depend only on `hla2010-spec` and `hla2010-verification-harness`.

## Dependency Layers

- Layer 0: `hla2010-spec`
- Layer 1: `hla2010-rti-backend-common`
- Layer 2: `hla2010-rti-java-common`, `hla2010-rti-python`, `hla2010-rti-transport-common`
- Layer 3: `hla2010-rti-java-jpype`, `hla2010-rti-java-py4j`, `hla2010-rti-runtime-common`
- Layer 4: `hla2010-rti-certi`, `hla2010-rti-pitch-common`, `hla2010-rti-portico`, `hla2010-rti-transport-grpc`, `hla2010-rti-transport-rest`, `hla2010-verification-harness`
- Layer 5: `hla2010-fom-target-radar`, `hla2010-rti-pitch-jpype`, `hla2010-rti-pitch-py4j`

## Direct Graph

```mermaid
graph TD
    hla2010_rti_runtime_common[hla2010-rti-runtime-common] --> hla2010_fom_target_radar[hla2010-fom-target-radar]
    hla2010_spec[hla2010-spec] --> hla2010_fom_target_radar[hla2010-fom-target-radar]
    hla2010_verification_harness[hla2010-verification-harness] --> hla2010_fom_target_radar[hla2010-fom-target-radar]
    hla2010_spec[hla2010-spec] --> hla2010_rti_backend_common[hla2010-rti-backend-common]
    hla2010_rti_java_common[hla2010-rti-java-common] --> hla2010_rti_certi[hla2010-rti-certi]
    hla2010_rti_runtime_common[hla2010-rti-runtime-common] --> hla2010_rti_certi[hla2010-rti-certi]
    hla2010_rti_transport_common[hla2010-rti-transport-common] --> hla2010_rti_certi[hla2010-rti-certi]
    hla2010_spec[hla2010-spec] --> hla2010_rti_certi[hla2010-rti-certi]
    hla2010_rti_backend_common[hla2010-rti-backend-common] --> hla2010_rti_java_common[hla2010-rti-java-common]
    hla2010_spec[hla2010-spec] --> hla2010_rti_java_common[hla2010-rti-java-common]
    hla2010_rti_java_common[hla2010-rti-java-common] --> hla2010_rti_java_jpype[hla2010-rti-java-jpype]
    hla2010_spec[hla2010-spec] --> hla2010_rti_java_jpype[hla2010-rti-java-jpype]
    hla2010_rti_java_common[hla2010-rti-java-common] --> hla2010_rti_java_py4j[hla2010-rti-java-py4j]
    hla2010_spec[hla2010-spec] --> hla2010_rti_java_py4j[hla2010-rti-java-py4j]
    hla2010_rti_java_common[hla2010-rti-java-common] --> hla2010_rti_pitch_common[hla2010-rti-pitch-common]
    hla2010_rti_runtime_common[hla2010-rti-runtime-common] --> hla2010_rti_pitch_common[hla2010-rti-pitch-common]
    hla2010_spec[hla2010-spec] --> hla2010_rti_pitch_common[hla2010-rti-pitch-common]
    hla2010_rti_java_jpype[hla2010-rti-java-jpype] --> hla2010_rti_pitch_jpype[hla2010-rti-pitch-jpype]
    hla2010_rti_pitch_common[hla2010-rti-pitch-common] --> hla2010_rti_pitch_jpype[hla2010-rti-pitch-jpype]
    hla2010_spec[hla2010-spec] --> hla2010_rti_pitch_jpype[hla2010-rti-pitch-jpype]
    hla2010_rti_java_py4j[hla2010-rti-java-py4j] --> hla2010_rti_pitch_py4j[hla2010-rti-pitch-py4j]
    hla2010_rti_pitch_common[hla2010-rti-pitch-common] --> hla2010_rti_pitch_py4j[hla2010-rti-pitch-py4j]
    hla2010_spec[hla2010-spec] --> hla2010_rti_pitch_py4j[hla2010-rti-pitch-py4j]
    hla2010_rti_java_common[hla2010-rti-java-common] --> hla2010_rti_portico[hla2010-rti-portico]
    hla2010_rti_java_jpype[hla2010-rti-java-jpype] --> hla2010_rti_portico[hla2010-rti-portico]
    hla2010_rti_java_py4j[hla2010-rti-java-py4j] --> hla2010_rti_portico[hla2010-rti-portico]
    hla2010_spec[hla2010-spec] --> hla2010_rti_portico[hla2010-rti-portico]
    hla2010_rti_backend_common[hla2010-rti-backend-common] --> hla2010_rti_python[hla2010-rti-python]
    hla2010_spec[hla2010-spec] --> hla2010_rti_python[hla2010-rti-python]
    hla2010_rti_backend_common[hla2010-rti-backend-common] --> hla2010_rti_runtime_common[hla2010-rti-runtime-common]
    hla2010_rti_transport_common[hla2010-rti-transport-common] --> hla2010_rti_runtime_common[hla2010-rti-runtime-common]
    hla2010_spec[hla2010-spec] --> hla2010_rti_runtime_common[hla2010-rti-runtime-common]
    hla2010_rti_backend_common[hla2010-rti-backend-common] --> hla2010_rti_transport_common[hla2010-rti-transport-common]
    hla2010_spec[hla2010-spec] --> hla2010_rti_transport_common[hla2010-rti-transport-common]
    hla2010_rti_runtime_common[hla2010-rti-runtime-common] --> hla2010_rti_transport_grpc[hla2010-rti-transport-grpc]
    hla2010_rti_transport_common[hla2010-rti-transport-common] --> hla2010_rti_transport_grpc[hla2010-rti-transport-grpc]
    hla2010_spec[hla2010-spec] --> hla2010_rti_transport_grpc[hla2010-rti-transport-grpc]
    hla2010_rti_runtime_common[hla2010-rti-runtime-common] --> hla2010_rti_transport_rest[hla2010-rti-transport-rest]
    hla2010_rti_transport_common[hla2010-rti-transport-common] --> hla2010_rti_transport_rest[hla2010-rti-transport-rest]
    hla2010_spec[hla2010-spec] --> hla2010_rti_transport_rest[hla2010-rti-transport-rest]
    hla2010_spec[hla2010-spec]
    hla2010_rti_backend_common[hla2010-rti-backend-common] --> hla2010_verification_harness[hla2010-verification-harness]
    hla2010_rti_runtime_common[hla2010-rti-runtime-common] --> hla2010_verification_harness[hla2010-verification-harness]
    hla2010_spec[hla2010-spec] --> hla2010_verification_harness[hla2010-verification-harness]
```

## Direct Dependencies

| Package | Internal deps | External deps |
| --- | --- | --- |
| `hla2010-fom-target-radar` | `hla2010-spec, hla2010-verification-harness, hla2010-rti-runtime-common` | `-` |
| `hla2010-rti-backend-common` | `hla2010-spec` | `-` |
| `hla2010-rti-certi` | `hla2010-spec, hla2010-rti-java-common, hla2010-rti-runtime-common, hla2010-rti-transport-common` | `-` |
| `hla2010-rti-java-common` | `hla2010-spec, hla2010-rti-backend-common` | `-` |
| `hla2010-rti-java-jpype` | `hla2010-spec, hla2010-rti-java-common` | `jpype1` |
| `hla2010-rti-java-py4j` | `hla2010-spec, hla2010-rti-java-common` | `py4j` |
| `hla2010-rti-pitch-common` | `hla2010-spec, hla2010-rti-java-common, hla2010-rti-runtime-common` | `-` |
| `hla2010-rti-pitch-jpype` | `hla2010-spec, hla2010-rti-java-jpype, hla2010-rti-pitch-common` | `-` |
| `hla2010-rti-pitch-py4j` | `hla2010-spec, hla2010-rti-java-py4j, hla2010-rti-pitch-common` | `-` |
| `hla2010-rti-portico` | `hla2010-spec, hla2010-rti-java-common, hla2010-rti-java-jpype, hla2010-rti-java-py4j` | `-` |
| `hla2010-rti-python` | `hla2010-spec, hla2010-rti-backend-common` | `-` |
| `hla2010-rti-runtime-common` | `hla2010-spec, hla2010-rti-backend-common, hla2010-rti-transport-common` | `-` |
| `hla2010-rti-transport-common` | `hla2010-spec, hla2010-rti-backend-common` | `-` |
| `hla2010-rti-transport-grpc` | `hla2010-spec, hla2010-rti-transport-common, hla2010-rti-runtime-common` | `grpcio` |
| `hla2010-rti-transport-rest` | `hla2010-spec, hla2010-rti-transport-common, hla2010-rti-runtime-common` | `-` |
| `hla2010-spec` | `-` | `-` |
| `hla2010-verification-harness` | `hla2010-spec, hla2010-rti-backend-common, hla2010-rti-runtime-common` | `-` |
