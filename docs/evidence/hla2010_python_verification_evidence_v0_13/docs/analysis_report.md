# HLA 2010 Java/C++ API Analysis and Python Scaffold

This report summarizes the uploaded IEEE HLA 2010 download bundles and the Python API scaffold generated from the Java and C++ API files.

## Input bundles processed

- `1516.1-2010_downloads.zip`
  - SHA-256: `e6343f40b066d51b7f435c9aae6788be24f5d585e370d972c032ab0b503e27c1`
  - Extracted contents: `HLAstandardMIM.xml`, `IEEE1516-2010_C++_API.zip`, `IEEE1516-2010_Java_API.zip`, `IEEE1516-FDD-2010.xsd`, `hla1516e.wsdl`.
- `1516.2-2010_downloads.zip`
  - SHA-256: `1fb3d77318d87f55938ec74e4bc2a1a90f3bf62aa56937850f1073c9d446bb2b`
  - Extracted contents: `IEEE1516-DIF-2010.xsd`, `IEEE1516-OMT-2010.xsd`, `RestaurantFOMmodule.xml`, `RestaurantSOMmodule.xml`.

The requested 2025 ZIP URL is listed by IEEE, but this execution environment could not persist the remote ZIP file. I included `tools/download_ieee_zips.py` so the same three resources can be fetched in a normal local environment.

## Java and C++ API inventory

| Area | Result |
|---|---:|
| Java API files | 204 |
| Java root package files | 58 |
| Java encoding files | 30 |
| Java exception files | 110 |
| Java time files | 6 |
| C++ header files | 30 |
| Java `RTIambassador` declarations | 172 |
| Java `RTIambassador` unique names | 150 |
| C++ `RTIambassador` declarations | 151 |
| C++ `RTIambassador` unique names | 140 |
| Java `FederateAmbassador` declarations | 70 |
| Java `FederateAmbassador` unique names parsed | 55 |
| C++ `FederateAmbassador` declarations | 60 |
| C++ `FederateAmbassador` unique names | 51 |

The Java `FederateAmbassador` unique-name count includes four nested supplemental-info accessors (`hasProducingFederate`, `getProducingFederate`, `hasSentRegions`, `getSentRegions`). The actual callback surface aligns with the C++ callback set at 51 callback names.

## Main Java/C++ reconciliation points

- **Naming:** Java and C++ use lowerCamelCase API names. The Python package preserves those in `hla.rti1516e.raw_api` and adds snake_case aliases in `hla.rti1516e.api`.
- **Overloads:** Java and C++ overload families do not map one-to-one into Python. The raw layer accepts `*args`/`**kwargs`; later typed adapter layers can expose explicit keyword signatures for common overload families.
- **C++ output parameters:** Python should return data directly or return dataclasses instead of requiring mutable output parameters.
- **Binary data:** Java `byte[]` and C++ `VariableLengthData` map to Python `bytes`.
- **Handles:** Handles are opaque, hashable value objects. Concrete adapters decide wire encoding and vendor interop behavior.
- **Transportation type:** Java uses `TransportationTypeHandle`; C++ uses `TransportationType`. The Python surface keeps both concepts available.
- **Passive subscription:** Java exposes passive subscription methods by name; C++ uses boolean active/passive parameters. The Python surface includes the Java-style passive aliases while allowing adapter-specific overload handling.
- **MIM create federation:** C++ has `createFederationExecutionWithMIM`; Java folds MIM into overloads of `createFederationExecution`. The Python surface includes both names.
- **Factory/decode helpers:** Java handle/map factories and C++ decode helpers are both represented so a Python backend can support either idiom.

## Python package contents

- `hla.rti1516e.raw_api`: source-derived lowerCamelCase `RTIambassador` and `FederateAmbassador` surfaces plus overload metadata.
- `hla.rti1516e.api`: Pythonic snake_case aliases layered over the raw API.
- `hla.rti1516e.enums`: enum classes corresponding to the Java/C++ API vocabulary.
- `hla.rti1516e.exceptions`: Python exception classes for the Java API exception set.
- `hla.rti1516e.handles`: opaque handle objects and handle-set aliases.
- `hla.rti1516e.time`: initial logical-time classes and factories for integer64 and float64 time.
- `hla.rti1516e.encoding`: minimal HLA primitive/composite data element helpers.
- `analysis/java_methods.json` and `analysis/cpp_methods.json`: parsed method inventories with source-file and line references.
- `analysis/api_comparison.md`: compact Java/C++ comparison notes.
- `analysis/source_inventory.json`: extraction inventory and SHA-256 information for the uploaded ZIPs.

## Status

This is an API façade and scaffold, not a complete RTI implementation. It is ready for the next phase: implement a concrete backend that speaks to an existing RTI, a local protocol implementation, or a generated federate-protocol transport.
