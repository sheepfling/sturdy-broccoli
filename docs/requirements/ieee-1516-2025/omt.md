# OMT / FOM Requirements

Source: IEEE 1516.2-2025 Object Model Template Specification.

| ID | Clause | Page | Summary | Implementation lane |
| --- | ---: | ---: | --- | --- |
| HLA-X-2025-OMT-001 | 3.3.1 | 31-32 | HLA object model names shall follow XML naming conventions plus HLA-specific restrictions. | Add `hla.foms.validation.validate_hla_name(...)` and apply across FOM/SOM surfaces. |
| HLA-X-2025-OMT-002 | 4 | 32 | Object models shall support both OMT tabular format and OMT DIF; DIF is primary and authoritative. | Prioritize XML/DIF support; emit markdown/tabular docs second. |
| HLA-X-2025-OMT-003 | 4 | 32-33 | All OMT components shall be completed for FOMs and SOMs, though some tables may be empty or contain only required HLA content. | Use validation states: `present`, `present-empty-allowed`, `missing-required`, `invalid-entry`. |
| HLA-X-2025-OMT-004 | 4; FI 4.1.4 | 33; 47 | FOMs require MOM/MIM content and the RTI uses MIM first, then FOM modules. | Loader reports MIM supplied, standard MIM auto-provided, MOM extensions present, or MOM missing. |
| HLA-X-2025-OMT-005 | 4.1 | 33 | Object model identification table rows are required, with `NA` where no information is appropriate. | Validate Name, Type, Version, Modification date, Security classification, Description, POC, and References. |
| HLA-X-2025-OMT-006 | 6.2 | 90-94 | OMT conformance verification should identify invalid entries explicitly. | Validator errors include requirement, table, field, value, status, and message. |
| HLA-X-2025-OMT-007 | 7; FI 4.1.4.1 | 100+; 47-48 | FOM/SOM merge rules are first-class requirements. | Build a merge engine and reject conflicts in attributes, interactions, dimensions, transportation, update rates, switches, and partial definitions. |

## Initial CLI Backlog

```bash
./tools/hla-x fom validate --edition 2025 --fom path/to/FOM.xml
./tools/hla-x fom merge --edition 2025 --mim standard --fom a.xml --fom b.xml
```

Initial validation lane:

- HLA naming rules
- required OMT components
- object model identification table
- object/interaction class roots
- attribute/parameter table references
- dimension table references
- transportation/order references
- switch values
- interface services usage table, if present
