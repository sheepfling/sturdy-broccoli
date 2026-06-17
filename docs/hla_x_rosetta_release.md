# HLA-X Rosetta Release

HLA-X is intended to become an open, Python-centered compatibility lab for IEEE
HLA 1516.1-2010 and 1516.1-2025.

The product claim is:

> One HLA behavior model, three languages, two standards, reproducible evidence.

This does not mean that a backend alias is a standard implementation. A route is
standard-backed only when it is driven by an artifact that compiles against the
official IEEE API bundle for that language and edition.

## Standard Shim Artifacts

The Rosetta release reserves four standard shim artifacts:

| Artifact | Standard surface | Official input | Python routes |
| --- | --- | --- | --- |
| `hla-x-rti1516e-java-shim.jar` | `hla.rti1516e` Java API | `IEEE1516-2010_Java_API.zip` | `java-standard-2010-jpype`, `java-standard-2010-py4j` |
| `hla-x-rti1516-2025-java-shim.jar` | 1516.1-2025 Java API | `1516.1-2025_downloads.zip` | `java-standard-2025-jpype`, `java-standard-2025-py4j` |
| `libhla_x_rti1516e_cpp_shim` | `rti1516e` C++ namespace | `IEEE1516-2010_C++_API.zip` | `cpp-standard-2010-pybind`, `cpp-standard-2010-grpc` |
| `libhla_x_rti1516_2025_cpp_shim` | `rti1516_2025` C++ namespace | `1516.1-2025_downloads.zip` | `cpp-standard-2025-pybind`, `cpp-standard-2025-grpc` |

The current `java-shim-*` routes are in-process Java-shaped test fixtures. The
current `cpp-shim-*` routes are C++ route scaffolds. They are useful, but they
must not be described as standard-backed until their artifacts satisfy the
contract below. `java-standard-2010-jpype` and `java-standard-2010-py4j` are
real plugin routes, but they are unavailable until
`./tools/hla-x build java-standard-2010` produces the official-API-backed jar.

## Completion Contract

A shim is complete only when:

1. It compiles against the official standard API bundle.
2. It exports the standard RTI factory/loading mechanism for that language.
3. Every standard `RTIambassador` method is present.
4. Unsupported services fail intentionally and appear in the generated coverage report.
5. The route passes the core scenario suite.
6. The route emits normalized traces comparable to Python reference traces.

The current MVP is intentionally smaller than this full contract. It proves the
standard-backed route wiring and a core behavior slice:

- 2010 C++ standard routes run a two-federate object, interaction, and time
  exchange through the Python reference behavior model.
- 2025 Java and C++ standard routes run lifecycle-core smoke through the 2025
  shim path.
- Full standard conformance, DDM, ownership, save/restore, MOM, and complete
  2025 object exchange remain outside the MVP.

## Core Scenario Suite

The core suite for all routes is:

1. connect and disconnect
2. create and destroy federation
3. join and resign federation
4. object class and attribute handle lookup
5. interaction class and parameter handle lookup
6. publish and subscribe object attributes
7. publish and subscribe interactions
8. register object instance
9. discover object callback
10. reflect attributes callback
11. receive interaction callback
12. synchronization point registration, announce, achieved, and synchronized
13. basic time regulation, constrained, and advance grant

The intended public commands are:

```sh
./tools/hla-x demo mixed-language-target-radar --edition 2010
./tools/hla-x demo mixed-language-target-radar --edition 2025
./tools/hla-x matrix --editions 2010,2025 --routes all
./tools/hla-x evidence rosetta-routes
```

The evidence command writes normalized MVP traces under
`docs/evidence/rosetta/route_traces/`. Those trace files are checked by tests so
the release matrix remains grounded in executable route behavior.

## Java Toolchain Inventory

Before building the Java Rosetta shims, run:

```sh
./tools/hla-x java doctor
```

That command prints a machine-readable inventory and writes:

- `docs/evidence/rosetta/java-toolchain.json`
- `docs/evidence/rosetta/java-toolchain.md`

Use it to confirm:

- which `JAVA_HOME` / `JDK_HOME` value won
- whether `java`, `javac`, and `jar` are available
- whether the 2010 and 2025 Rosetta jars already exist
- which `./tools/hla-x build ...` command to run next
