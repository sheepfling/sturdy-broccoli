# Pitch SISO Micro Delivery Alignment

Date: `2026-06-24`

Artifact source:
- `artifacts/pitch_202x_micro_certification/pitch_202x_micro_certification_summary.json`
- `artifacts/pitch_202x_micro_certification/pitch_202x_micro_certification_report.md`

Scope:
- command: `./tools/pitch 202x-micro-certify`
- real vendor-runtime bridges:
  - `pitch-jpype`
  - `pitch-py4j`
- bounded adapter routes:
  - `pitch-202x-jpype`
  - `pitch-202x-py4j`

## Summary

The earlier failing real Pitch 2010 SISO micro rows were recovered by aligning
their callback wait discipline with the already-passing real Pitch exchange
smoke path.

Final bounded comparison result:

- `link16`: passed on real Pitch 2010 and bounded `pitch-202x-*`
- `rpr`: passed on real Pitch 2010 and bounded `pitch-202x-*`
- `space`: passed on real Pitch 2010 and bounded `pitch-202x-*`
- certification state: `bounded-vendor-comparison`

## What failed first

The first failing real Pitch 2010 micro result showed:

- registration/update/send attempts had happened
- both federates had zero:
  - `discoverObjectInstance`
  - `reflectAttributeValues`
  - `receiveInteraction`

That proved the issue was not:

- a `pitch-202x-*` 2025 adapter failure
- an XML/FOM parse or decode failure
- a simple pre-registration exception on the scenario side

## Earlier fixes before the final alignment

Two narrower issues were fixed before the final green result:

1. per-ambassador handle locality
   - object, attribute, interaction, and parameter handles must be resolved per
     RTI ambassador for real vendor routes
2. named object registration reservation discipline
   - explicit object names must use the shared reservation-aware registration
     helper path

Those fixes removed:

- handle-conversion failures
- `ObjectInstanceNameNotReserved` failures

But they still did not produce delivery callbacks on the real Pitch 2010 SISO
micro lane.

## What actually fixed delivery

The final passing change was to give the two-federate SISO showcase rows the
same explicit callback wait loops already used by the proven real Pitch control
smoke.

Instead of only relying on a bounded callback drain, the executable lane now
waits explicitly for:

- discovery after registration
- reflection after attribute update
- interaction receipt after interaction send

That is the important behavioral conclusion:

- real Pitch 2010 delivery in this micro lane needed stronger callback wait
  discipline than the generic bounded drain

## Comparison against the control smoke

Control comparison:

- real Pitch exchange smoke:
  - `tests/vendors/test_real_vendor_runtime_smoke.py::test_pitch_java_real_exchange_smoke`
  - passed live on both `pitch-jpype` and `pitch-py4j`

The important structural difference was:

- control smoke already used explicit `wait_for_callback_count_pair(...)`
- SISO micro originally did not

After aligning the SISO micro lane to that same callback discipline, the real
Pitch 2010 micro rows turned green.

## Claim boundary

This note supports the following precise statement:

- the earlier failing real Pitch 2010 SISO micro rows were an executable-lane
  callback-delivery timing/discipline issue, not a 2025 adapter defect and not
  an XML/FOM decoding issue

It does not support the broader statement:

- all Pitch runtime callback behavior is now fully characterized across all
  topologies and clauses

## Additional runtime observation

The successful live run also logged FedPro session drop/resume messages while
the bounded comparison packet still completed green.

Treat those messages as vendor-observable runtime behavior that may need
separate tracking, not as an automatic packet failure.
