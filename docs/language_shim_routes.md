# Language Shim Routes

This page tracks the Java and C++ standard-surface binding routes.
Those routes adapt official Java and C++ 1516.1 APIs onto repo-owned Python
runtime lanes so behavior exercised through language-specific API surfaces can
be compared against the local Python RTI evidence.
These routes are experimental. They are not a release, standard
implementation, vendor runtime, conformance claim, or compatibility promise.
A route should only be described as standard-backed when its artifact compiles
against the official API bundle for that language and edition.

## Standard Binding Artifacts

The language-route work currently tracks four standard API binding artifacts:

| Artifact | Standard surface | Official input | Python routes |
| --- | --- | --- | --- |
| `java-rti1516e-standard-shim.jar` | `hla.rti1516e` Java API | `IEEE1516-2010_Java_API.zip` | `java-standard-2010-jpype`, `java-standard-2010-py4j` |
| `java-rti1516-2025-standard-shim.jar` | 1516.1-2025 Java API | `1516.1-2025_downloads.zip` | `java-standard-2025-jpype`, `java-standard-2025-py4j` |
| `librti1516e_standard_cpp_shim` | `rti1516e` C++ namespace | `IEEE1516-2010_C++_API.zip` | `cpp-standard-2010-pybind`, `cpp-standard-2010-grpc` |
| `librti1516_2025_standard_cpp_shim` | `rti1516_2025` C++ namespace | `1516.1-2025_downloads.zip` | `cpp-standard-2025-pybind`, `cpp-standard-2025-grpc` |

The older `java-shim-*` routes are in-process Java-shaped test fixtures. The
older `cpp-shim-*` routes are C++ route scaffolds. They are useful, but they
must not be described as standard-backed until their artifacts satisfy the
contract below.

For the 2025 lane specifically:

- `java-standard-2025-jpype`, `java-standard-2025-py4j`,
  `cpp-standard-2025-pybind`, and `cpp-standard-2025-grpc` are binding routes,
  not separate RTIs
- those routes execute over the primary `hla-backend-python1516-2025` runtime lane
- `hla-backend-shim` remains only a legacy compatibility shim where older
  import paths or wrapper-shaped entry points still exist

`java-standard-2010-jpype` and `java-standard-2010-py4j` are real plugin
routes, but they are unavailable until `./tools/shim-routes build
java-standard-2010` produces the official-API-backed jar.

## Completion Contract

A language binding route is complete only when:

1. It compiles against the official standard API bundle.
2. It exports the standard RTI factory/loading mechanism for that language.
3. Every standard `RTIambassador` method is present.
4. Unsupported services fail intentionally and appear in the generated coverage report.
5. The route passes the core scenario suite.
6. The route emits normalized traces comparable to Python reference traces.

The current MVP is intentionally smaller than this full contract. It proves the
standard-backed route wiring and a bounded behavior slice:

- 2010 C++ standard routes run a two-federate object, interaction, and time
  exchange through the Python reference behavior model.
- 2025 Java and C++ standard routes run bounded lifecycle, object exchange,
  ownership, DDM, time-management, support-services, save/restore, MOM, and
  runtime-capability traces over the primary `python1516_2025` runtime lane.
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

For 2025 standard routes, the checked-in trace and aggregate evidence also
record:

- `runtimeProvider = python1516_2025`
- `implementationLane = hla-backend-python1516-2025`
- `wrapperOnly = false`

That contract exists to keep the route evidence explicit about the fact that
Java and C++ bindings are adaptation lanes over the main Python 2025 RTI, not
alternate 2025 RTI implementations.

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

## C++ Toolchain Inventory

Before building the C++ standard API shim artifacts or certifying profile-based
C++ capsules, run:

```sh
./tools/shim-routes cpp doctor
```

That command prints a machine-readable inventory and writes:

- `docs/evidence/shim_routes/cpp-toolchain.json`
- `docs/evidence/shim_routes/cpp-toolchain.md`

Use it to confirm:

- whether `c++`, `ar`, and `cmake` are available
- whether the 2010 and 2025 C++ shim archives already exist
- which `./tools/shim-routes build ...` command to run next
