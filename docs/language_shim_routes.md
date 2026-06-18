# Language Shim Routes

This page tracks the Java and C++ shim-route experiments.
The purpose of these routes is to test whether behavior exercised through
language-specific API surfaces can be compared against the local Python
reference route.
These routes are experimental. They are not a release, standard
implementation, vendor runtime, conformance claim, or compatibility promise.
A route should only be described as standard-backed when its artifact compiles
against the official API bundle for that language and edition.

## Standard Shim Artifacts

The language-shim route work currently tracks four standard API shim artifacts:

| Artifact | Standard surface | Official input | Python routes |
| --- | --- | --- | --- |
| `java-rti1516e-standard-shim.jar` | `hla.rti1516e` Java API | `IEEE1516-2010_Java_API.zip` | `java-standard-2010-jpype`, `java-standard-2010-py4j` |
| `java-rti1516-2025-standard-shim.jar` | 1516.1-2025 Java API | `1516.1-2025_downloads.zip` | `java-standard-2025-jpype`, `java-standard-2025-py4j` |
| `librti1516e_standard_cpp_shim` | `rti1516e` C++ namespace | `IEEE1516-2010_C++_API.zip` | `cpp-standard-2010-pybind`, `cpp-standard-2010-grpc` |
| `librti1516_2025_standard_cpp_shim` | `rti1516_2025` C++ namespace | `1516.1-2025_downloads.zip` | `cpp-standard-2025-pybind`, `cpp-standard-2025-grpc` |

The current `java-shim-*` routes are in-process Java-shaped test fixtures. The
current `cpp-shim-*` routes are C++ route scaffolds. They are useful, but they
must not be described as standard-backed until their artifacts satisfy the
contract below. `java-standard-2010-jpype` and `java-standard-2010-py4j` are
real plugin routes, but they are unavailable until
`./tools/shim-routes build java-standard-2010` produces the official-API-backed jar.

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

The intended operator commands are:

```sh
./tools/shim-routes demo mixed-language-target-radar --edition 2010
./tools/shim-routes demo mixed-language-target-radar --edition 2025
./tools/shim-routes matrix --editions 2010,2025 --routes all
./tools/shim-routes evidence shim-routes
```

The evidence command writes normalized MVP traces under
`docs/evidence/shim_routes/route_traces/`. Those trace files are checked by tests so
the route matrix remains grounded in executable route behavior.

## Java Toolchain Inventory

Before building the Java standard API shim artifacts, run:

```sh
./tools/shim-routes java doctor
```

That command prints a machine-readable inventory and writes:

- `docs/evidence/shim_routes/java-toolchain.json`
- `docs/evidence/shim_routes/java-toolchain.md`

Use it to confirm:

- which `JAVA_HOME` / `JDK_HOME` value won
- whether `java`, `javac`, and `jar` are available
- whether the 2010 and 2025 Java shim jars already exist
- which `./tools/shim-routes build ...` command to run next
