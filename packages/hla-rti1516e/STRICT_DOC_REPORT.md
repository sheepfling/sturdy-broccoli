# Strict doc report: hla1516_2010

Generated a Python typing/specification package from the supplied 2010 Java and C++ API files.

## Counts

```json
{
  "java_rti_declarations": 172,
  "java_rti_unique_names": 150,
  "cpp_rti_declarations": 151,
  "cpp_rti_unique_names": 140,
  "java_fed_declarations": 60,
  "java_fed_unique_names": 51,
  "cpp_fed_declarations": 60,
  "cpp_fed_unique_names": 51,
  "java_encoder_declarations": 45,
  "java_encoder_unique_names": 24,
  "rti_python_method_names": 162,
  "fed_python_method_names": 51,
  "rti_overload_groups": 17,
  "fed_overload_groups": 6,
  "encoder_overload_groups": 21,
  "java_exception_classes": 110,
  "cpp_exception_macros": 121,
  "python_exception_classes_including_base": 122
}
```

## Overload coverage

| Surface | Java declarations | Java unique names | C++ declarations | C++ unique names | Python names | Strict stub overload groups |
|---|---:|---:|---:|---:|---:|---:|
| RTIambassador | 172 | 150 | 151 | 140 | 162 | 17 |
| FederateAmbassador | 60 | 51 | 60 | 51 | 51 | 6 |
| EncoderFactory | 45 | 24 | n/a | n/a | modeled in `encoding.py` | 21 |

## Strictness notes

- `rti_ambassador.pyi`, `federate_ambassador.pyi`, and `encoding.pyi` carry strict overload sets.
- Ambiguous 2010 Java overloads that collapse to identical Python scalar types are represented with keyword-only alternatives, notably `createFederationExecution` and `joinFederationExecution`.
- The package includes C++-only RTI methods such as `createFederationExecutionWithMIM`, handle decode services, and `TransportationType` name/type services.
- Runtime `.py` modules remain importable protocol surfaces and the `.pyi` stubs provide the stricter static contract.

## Source conventions

- Java service-section comments such as `// 4.2` are preserved as `§4.2` in generated source comments and `SOURCE_TRACE.md`.
- C++ service-section comments are used when a service exists only in the C++ 2010 API.
- Java `throws` clauses are documented in the source trace rather than encoded into function types.
- 1516.2 OMT/DIF and 1516.1 FDD/MIM/WSDL files from the project bundles are referenced as schema/context sources, not copied into the package.

## Validation performed

- Python syntax compile for all `.py` modules.
- `ast.parse` validation for all generated `.pyi` stubs.
- Runtime import check for `hla1516_2010` from the generated package path.
