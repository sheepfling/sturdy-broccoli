# HLA-X v0.1 Prototype FOM and Test Package

This package contains concrete draft IEEE 1516-2025-style FOM XML modules and companion requirements/test-plan documents for early HLA-X RTI and federate testing.

## Files

- `foms/HLAx_Base.xml`
- `foms/HLAx_MessageTest.xml`
- `foms/HLAx_SpaceLite.xml`
- `foms/HLAx_TimeMgmtTest.xml`
- `test_plans/HLAx_MessageTest_TestPlan.md`
- `test_plans/HLAx_SpaceLite_TestPlan.md`
- `test_plans/HLAx_TimeMgmtTest_TestPlan.md`
- `VALIDATION.txt`

## Validation status

The XML files were validated in this workspace against `IEEE1516-DIF-2025.xsd` extracted from the uploaded `1516.2-2025_downloads.zip` package. See `VALIDATION.txt`.

## Executable showcase

Run the HLA-X v0.1 examples alongside the existing Target/Radar FOM-backed simulation:

```bash
./tools/hla-x demo fom-showcase --edition 2025 --output-dir analysis/hlax_fom_showcase
```

The showcase creates and destroys federation executions for MessageTest, SpaceLite, TimeMgmtTest, and Target/Radar, with named federates exchanging FOM-defined objects and interactions through the RTI.

## Notes

These are prototype FOM modules. The selected RTI may enforce additional semantic merge checks across modules, standard datatype availability, MIM loading order, or vendor-specific FDD constraints. Treat this as a concrete v0.1 baseline for iteration, not a final conformance package.
