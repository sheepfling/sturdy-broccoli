# Proto2025 v0.1 Prototype FOM and Test Package

This package contains concrete draft IEEE 1516-2025-style FOM XML modules and companion requirements/test-plan documents for early Proto2025 RTI and federate testing.

## Files

- `foms/Proto2025_Base.xml`
- `foms/Proto2025_MessageTest.xml`
- `foms/Proto2025_SpaceLite.xml`
- `foms/Proto2025_TimeMgmtTest.xml`
- `test_plans/Proto2025_MessageTest_TestPlan.md`
- `test_plans/Proto2025_SpaceLite_TestPlan.md`
- `test_plans/Proto2025_TimeMgmtTest_TestPlan.md`
- `VALIDATION.txt`

## Validation status

The XML files were validated in this workspace against `IEEE1516-DIF-2025.xsd` extracted from the uploaded `1516.2-2025_downloads.zip` package. See `VALIDATION.txt`.

## Executable showcase

Run the Proto2025 v0.1 examples alongside the existing Target/Radar FOM-backed simulation:

```bash
./tools/shim-routes demo fom-showcase --edition 2025 --output-dir analysis/proto2025_fom_showcase
```

The showcase creates and destroys federation executions for MessageTest, SpaceLite, TimeMgmtTest, and Target/Radar, with named federates exchanging FOM-defined objects and interactions through the RTI.

## Notes

These are prototype FOM modules. The selected RTI may enforce additional semantic merge checks across modules, standard datatype availability, MIM loading order, or vendor-specific FDD constraints. Treat this as a concrete v0.1 baseline for iteration, not a final conformance package.
