# hla2010-rti-java

Standard Java RTI implementation selection package for `hla2010-spec`.

Use this package when a vendor RTI follows the standard Java HLA API and can be
selected by passing an implementation string to
`hla.rti1516e.RtiFactoryFactory.getRtiFactory(...)`.

```python
from hla2010_rti_java import JavaRTIImplementation

implementation = JavaRTIImplementation(
    "com.vendor.hla.RtiFactory",
    bridge="jpype",
    classpath=("vendor-rti.jar",),
)

report = implementation.discover()
rti = implementation.create_rti_ambassador()
```

The package sits above `hla2010-rti-java-common`, `hla2010-rti-java-jpype`, and
`hla2010-rti-java-py4j`. It owns bridge selection and discovery; the lower-level
packages own adapter mechanics and bridge runtimes.

For the shortest 2010 path:

```python
from hla2010_rti_java import java_2010_rti_ambassador

rti = java_2010_rti_ambassador(
    "com.vendor.hla.RtiFactory",
    classpath=("vendor-rti.jar",),
)
```
