# Python2025 Exclusion Boundaries

This note records what the repository is explicitly **not** claiming as part of
the main IEEE 1516.1-2025 Python RTI implementation statement.

Use it when you need the short list of boundaries around the current
`hla-backend-python1516-2025` working-surface claim.

## Owner Surface

- canonical owner doc:
  `docs/requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md`
- primary shard: `unit-foundation`
- widen to: route-parity or backend-resolution artifacts only when the exclusion
  statement itself changes
- typical view tags: `2025-core`, `setup-preflight`, `route-parity`

## Final Claim Rule

- this doc records what is intentionally outside the main `python1516_2025`
  implementation-owner claim
- exclusions do not transfer ownership away from `hla-backend-python1516-2025`
- do not use excluded, wrapper-only, umbrella, retired, or tolerance-only areas
  to inflate the current repo claim
- if one of these excluded areas becomes in scope later, give it its own
  narrower owner row and direct proof rather than silently weakening the
  boundary

## Main Rule

`hla-backend-python1516-2025` is the sole repo-owned Python RTI implementation lane
for `rti1516_2025`.

The exclusions below do **not** transfer implementation ownership away from
that lane. They describe bounded compatibility, binding, hosted-route,
requirement-granularity, or OMT-scope limits around the claim.

## Excluded Areas

| Area | Current repo stance | Primary evidence anchors |
| --- | --- | --- |
| Legacy aliases and shim imports | `hla-backend-shim` is deprecated temporary import-compatibility scaffolding and wrapper-only compatibility support. Legacy provider/import aliases are not part of the implementation-owner claim. | [`../../python_rti_backend.md`](../../python_rti_backend.md), [`../../../packages/hla-backend-shim/README.md`](../../../packages/hla-backend-shim/README.md), [`../../../tests/test_python1516_2025_split_package.py`](../../../tests/test_python1516_2025_split_package.py), [`../../../tests/test_package_split_scaffolds.py`](../../../tests/test_package_split_scaffolds.py) |
| Java/C++ bindings | Java and C++ routes remain binding/adaptation-seam evidence over `hla-backend-python1516-2025`, not alternate Python RTIs and not exhaustive cross-binding behavior conformance. | [`standard_binding_runtime_capability_bounded_proof.md`](standard_binding_runtime_capability_bounded_proof.md), [`binding_and_hosted_route_boundaries.md`](binding_and_hosted_route_boundaries.md), [`../../../tests/requirements/test_2025_route_parity_matrix.py`](../../../tests/requirements/test_2025_route_parity_matrix.py) |
| Hosted transport boundaries | `python1516_2025-fedpro-grpc` is a bounded hosted transport/runtime slice over `hla-backend-python1516-2025`, not a second full RTI implementation lane and not a blanket remote-semantics conformance claim. | [`hosted_fedpro_bounded_proof.md`](hosted_fedpro_bounded_proof.md), [`binding_and_hosted_route_boundaries.md`](binding_and_hosted_route_boundaries.md), [`../../../tests/transport/test_grpc_transport_2025.py`](../../../tests/transport/test_grpc_transport_2025.py) |
| Duplicate/umbrella rows | Duplicate/umbrella rows remain normalization aids and mapping notes rather than standalone one-row conformance assertions. | [`framework_rules.md`](framework_rules.md), [`callback_binding_deltas.md`](callback_binding_deltas.md), [`../../../tests/verification/test_2025_finish_line_reporting.py`](../../../tests/verification/test_2025_finish_line_reporting.py) |
| Retired/legacy-only rows | Retired rows remain explicit exclusions from active 2025 support obligations; the repo documents candidate replacements without converting those rows into live support claims. | [`retired_legacy_mapping.md`](retired_legacy_mapping.md), [`../../../tests/verification/test_2025_finish_line_reporting.py`](../../../tests/verification/test_2025_finish_line_reporting.py) |
| OMT extension semantics | OMT `xs:any` handling is limited to payload-preserving, schema-tolerant parsing and round-trip behavior. Arbitrary third-party extension execution semantics remain out of scope. | [`omt_xs_any_extension_tolerance.md`](omt_xs_any_extension_tolerance.md), [`../../../tests/test_rti1516_2025_validation.py`](../../../tests/test_rti1516_2025_validation.py), [`../../../tests/verification/test_2025_finish_line_reporting.py`](../../../tests/verification/test_2025_finish_line_reporting.py) |

## What Still Counts As In Scope

The exclusions above do not weaken the repo's current bounded executable claim
for the direct `python1516_2025` lane plus hosted FedPro replay:

- direct `python1516_2025` runtime proof remains owned by `hla-backend-python1516-2025`
- hosted FedPro proof remains route evidence over that same runtime
- requirement-to-test anchors remain valid for the supported working surface

Read the broader bounded claim and current evidence posture in:

- [`../../python_rti_backend.md`](../../python_rti_backend.md)
- [`README.md`](README.md)
- [`binding_and_hosted_route_boundaries.md`](binding_and_hosted_route_boundaries.md)
- [`../../../requirements/2025/canonical_requirements.json`](../../../requirements/2025/canonical_requirements.json)
- [`../../../requirements/2025/backend_resolution.json`](../../../requirements/2025/backend_resolution.json)
