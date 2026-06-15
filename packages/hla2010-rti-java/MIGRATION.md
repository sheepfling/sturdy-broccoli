# Java RTI Selector Package Migration

Implementation moved into:

- `hla2010_rti_java`

This package owns the standard Java RTI implementation selector surface:

- `JavaRTIImplementation`
- `java_2010_rti_ambassador`
- `java_rti_ambassador_for_edition`
- `debug_java_rti_implementation`

Lower-level bridge mechanics remain in `hla2010-rti-java-common`,
`hla2010-rti-java-jpype`, and `hla2010-rti-java-py4j`.
