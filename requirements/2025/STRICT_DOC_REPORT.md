# HLA 1516.1-2025 strict-doc Python package report

Built from `hla1516_2025_best_python_spec_package.zip` and enhanced with strict overload stubs, module/class docstrings, and source trace comments.

## Added in this pass

- `hla1516_2025/rti_ambassador.pyi`: strict overload set for RTI services.
- `hla1516_2025/federate_ambassador.pyi`: strict overload set for callback services.
- `hla1516_2025/encoding.pyi`: strict encoding factory overloads and encoding protocol source comments.
- Runtime module docstrings across the package.
- `SOURCE_TRACE.md`: source mapping to Java/C++ files, service numbers, overload counts, and Java throws summaries.

## Overload coverage

| Surface | Java declarations | Java unique names | Python runtime names | Strict stub overload groups |
|---|---:|---:|---:|---:|
| RTIambassador | 206 | 179 | 188 | 21 |
| FederateAmbassador | 62 | 56 | 56 | 6 |
| EncoderFactory | 82 | 43 | modeled in `encoding.py` | 39 |

## Source conventions

- Java service-section comments such as `// 4.2` are preserved as `§4.2` in the generated source trace and stubs.
- Java overload declarations become Python `@overload` entries where distinguishable in Python typing.
- The ambiguous Java `joinFederationExecution` overload family is represented as keyword-only overloads in Python to keep all variants distinguishable.
- Exceptions remain normal Python classes; Java `throws` clauses are documented in the source trace rather than encoded into function types.

## Validation performed

- Python syntax compile for all `.py` modules.
- `ast.parse` validation for all generated `.pyi` stubs.
- Runtime import check for `hla1516_2025` from the generated zip.
