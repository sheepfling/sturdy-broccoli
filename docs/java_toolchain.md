# Java Toolchain

Use this page when the agent or a human needs to find the Java toolchain
required for Rosetta builds and Java-route tests.

## Front Door

Run:

```sh
./tools/java
```

That command reports:

- which Java home was discovered
- whether `java`, `javac`, and `jar` are available
- whether the Rosetta Java shim jars already exist
- which build command to run next if a jar is missing

It also writes a machine-readable inventory and a Markdown summary under:

- `docs/evidence/rosetta/java-toolchain.json`
- `docs/evidence/rosetta/java-toolchain.md`

## Discovery Order

Java home discovery follows this order:

1. `JAVA_HOME`
2. `JDK_HOME`
3. `jdk4py.JAVA_HOME`
4. `/usr/libexec/java_home`
5. `PATH` fallback for the `java` tool

The repository prefers a real JDK, not just a runtime, because Rosetta builds
need `javac` and `jar` as well as `java`.

## Required Tools

For Java-backed routes and Rosetta builds, the useful toolchain is:

- `java`
- `javac`
- `jar`

## Rosetta Artifacts

The canonical Java shim artifacts are:

- `build/rosetta/java-standard-2010/hla-x-rti1516e-java-shim.jar`
- `build/rosetta/java-standard-2025/hla-x-rti1516-2025-java-shim.jar`

If either jar is missing, the inventory tells you the exact build command to
run:

- `./tools/hla-x build java-standard-2010`
- `./tools/hla-x build java-standard-2025`

`./tools/java` is the short operator front door. The longer Rosetta-lab alias
remains `./tools/hla-x java doctor`.

## Related Docs

- [hla_x_rosetta_release.md](hla_x_rosetta_release.md)
- [vendor_runtime_runner_guide.md](vendor_runtime_runner_guide.md)
- [../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_runtime.py](../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_runtime.py)
