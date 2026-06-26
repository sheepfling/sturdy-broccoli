# Spec Reading Map

Use this page when the question is:

- where should I start reading standards-facing material?
- how do requirement notes, verification docs, and generated evidence fit together?
- which document should I open first for a claim or proof question?

Do not start with a random proof note.
Start from the claim map, then move toward executable or generated evidence.

## Start Here

Read these in order:

1. [`requirements/ieee-1516-2010/README.md`](requirements/ieee-1516-2010/README.md) or [`requirements/ieee-1516-2025/README.md`](requirements/ieee-1516-2025/README.md)
2. [`verification/README.md`](verification/README.md)
3. one focused proof note or requirement ledger for the family you care about
4. the matching executable or generated evidence doc

## By Question

| If the question is... | Start here | Then read |
| --- | --- | --- |
| where is the 2010 requirement source surface? | [`requirements/ieee-1516-2010/README.md`](requirements/ieee-1516-2010/README.md) | [`../requirements/2010/README.md`](../requirements/2010/README.md), [`verification/README.md`](verification/README.md) |
| what does the main 2025 runtime claim? | [`requirements/ieee-1516-2025/python1516_2025_direct_bounded_proof.md`](requirements/ieee-1516-2025/python1516_2025_direct_bounded_proof.md) | [`verification/README.md`](verification/README.md), [`verification/time_model_compliance.md`](verification/time_model_compliance.md) |
| what is the save/restore proof boundary? | [`requirements/ieee-1516-2025/save_restore_bounded_proof.md`](requirements/ieee-1516-2025/save_restore_bounded_proof.md) | [`verification/README.md`](verification/README.md) |
| what is the callback proof boundary? | [`requirements/ieee-1516-2025/callback_bounded_proof.md`](requirements/ieee-1516-2025/callback_bounded_proof.md) | [`verification/callback_model_compliance.md`](verification/callback_model_compliance.md) |
| what is the time/lookahead proof boundary? | [`requirements/ieee-1516-2025/time_management_bounded_proof.md`](requirements/ieee-1516-2025/time_management_bounded_proof.md) | [`verification/time_model_compliance.md`](verification/time_model_compliance.md), [`requirements/ieee-1516-2025/lookahead_window_bounded_proof.md`](requirements/ieee-1516-2025/lookahead_window_bounded_proof.md) |
| what do Java/C++ standard bindings claim? | [`requirements/ieee-1516-2025/standard_binding_runtime_capability_bounded_proof.md`](requirements/ieee-1516-2025/standard_binding_runtime_capability_bounded_proof.md) | [`requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md`](requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md), [`language_shim_routes.md`](language_shim_routes.md) |
| what is explicitly out of scope? | [`requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md`](requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md) | [`verification/README.md`](verification/README.md) |

## Practical Rule

- requirements docs explain the claim, boundary, and intended evidence scope
- verification docs explain where executable or generated proof artifacts live
- backend and route docs explain how the runtime or route is wired

## Read Next

1. [`requirements/ieee-1516-2025/README.md`](requirements/ieee-1516-2025/README.md)
2. [`requirements/ieee-1516-2010/README.md`](requirements/ieee-1516-2010/README.md)
3. [`verification/README.md`](verification/README.md)
4. [`requirements_trace_one_method.md`](requirements_trace_one_method.md)
