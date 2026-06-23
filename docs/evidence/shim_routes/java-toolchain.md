# Java Toolchain Inventory

- Status: `degraded`
- Discovery source: `jdk4py.JAVA_HOME`
- JAVA_HOME env: ``
- JDK_HOME env: ``
- Java home: `/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/jdk4py/java-runtime`
- java: `/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/jdk4py/java-runtime/bin/java`
- javac: `/usr/bin/javac`
- jar: `/usr/bin/jar`

## Tool Checks

- java: PASS
- javac: PASS
- jar: PASS

## Shim Artifacts

| key | label | path | exists | build command |
| --- | --- | --- | --- | --- |
| `java-standard-2010` | Java 2010 standard shim jar | `build/shim_routes/java-standard-2010/java-rti1516e-standard-shim.jar` | FAIL | `./tools/shim-routes build java-standard-2010` |
| `java-standard-2025` | Java 2025 standard shim jar | `build/shim_routes/java-standard-2025/java-rti1516-2025-standard-shim.jar` | PASS | `./tools/shim-routes build java-standard-2025` |

## Notes

- Java home discovered from jdk4py.JAVA_HOME

## Warnings

- one or more Java standard shim jars are missing; build them with ./tools/shim-routes build <target>
