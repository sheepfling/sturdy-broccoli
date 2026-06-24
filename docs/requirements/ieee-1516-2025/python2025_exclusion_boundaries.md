# Python2025 Exclusion Boundaries

This note records what the repository is explicitly **not** claiming as part of
the main IEEE 1516.1-2025 Python RTI implementation statement.

Use it when you need the short list of boundaries around the current
`hla-backend-python2025` working-surface claim.

## Main Rule

`hla-backend-python2025` is the sole repo-owned Python RTI implementation lane
for `rti1516_2025`.

The exclusions below do **not** transfer implementation ownership away from
that lane. They describe bounded compatibility, binding, hosted-route,
requirement-granularity, or OMT-scope limits around the claim.

## Excluded Areas

| Area | Current repo stance | Primary evidence anchors |
| --- | --- | --- |
| Legacy aliases and shim imports | `hla-backend-shim` is deprecated temporary import-compatibility scaffolding and wrapper-only compatibility support. Legacy provider/import aliases are not part of the implementation-owner claim. | [`../../python_rti_backend.md`](../../python_rti_backend.md), [`../../../packages/hla-backend-shim/README.md`](../../../packages/hla-backend-shim/README.md), [`../../../tests/test_python2025_split_package.py`](../../../tests/test_python2025_split_package.py), [`../../../tests/test_package_split_scaffolds.py`](../../../tests/test_package_split_scaffolds.py) |
| Java/C++ bindings | Java and C++ routes remain binding/adaptation-seam evidence over `hla-backend-python2025`, not alternate Python RTIs and not exhaustive cross-binding behavior conformance. | [`standard_binding_runtime_capability_bounded_proof.md`](standard_binding_runtime_capability_bounded_proof.md), [`binding_and_hosted_route_boundaries.md`](binding_and_hosted_route_boundaries.md), [`../../../tests/requirements/test_2025_route_parity_matrix.py`](../../../tests/requirements/test_2025_route_parity_matrix.py) |
| Hosted transport boundaries | `python1516_2025-fedpro-grpc` is a bounded hosted transport/runtime slice over `hla-backend-python2025`, not a second full RTI implementation lane and not a blanket remote-semantics conformance claim. | [`hosted_fedpro_bounded_proof.md`](hosted_fedpro_bounded_proof.md), [`binding_and_hosted_route_boundaries.md`](binding_and_hosted_route_boundaries.md), [`../../../tests/transport/test_grpc_transport_2025.py`](../../../tests/transport/test_grpc_transport_2025.py) |
| Duplicate/umbrella rows | Duplicate/umbrella rows remain normalization aids and mapping notes rather than standalone one-row conformance assertions. | [`framework_rules.md`](framework_rules.md), [`callback_binding_deltas.md`](callback_binding_deltas.md), [`../../../tests/requirements/test_2025_finish_line_snapshot.py`](../../../tests/requirements/test_2025_finish_line_snapshot.py) |
| Retired/legacy-only rows | Retired rows remain explicit exclusions from active 2025 support obligations; the repo documents candidate replacements without converting those rows into live support claims. | [`retired_legacy_mapping.md`](retired_legacy_mapping.md), [`../../../tests/requirements/test_2025_finish_line_snapshot.py`](../../../tests/requirements/test_2025_finish_line_snapshot.py) |
| OMT extension semantics | OMT `xs:any` handling is limited to payload-preserving, schema-tolerant parsing and round-trip behavior. Arbitrary third-party extension execution semantics remain out of scope. | [`omt_xs_any_extension_tolerance.md`](omt_xs_any_extension_tolerance.md), [`../../../tests/test_rti1516_2025_validation.py`](../../../tests/test_rti1516_2025_validation.py), [`../../../tests/requirements/test_2025_finish_line_snapshot.py`](../../../tests/requirements/test_2025_finish_line_snapshot.py) |

## What Still Counts As In Scope

The exclusions above do not weaken the repo's current bounded executable claim
for the direct and hosted Python 2025 lanes:

- direct `python1516_2025` runtime proof remains owned by `hla-backend-python2025`
- hosted FedPro proof remains route evidence over that same runtime
- requirement-to-test anchors remain valid for the supported working surface

Read the broader bounded claim and current evidence posture in:

- [`../../python_rti_backend.md`](../../python_rti_backend.md)
- [`../../plans/2025_python_rti_backend_audit.md`](../../plans/2025_python_rti_backend_audit.md)
- [`../../plans/2025_requirements_finish_line.md`](../../plans/2025_requirements_finish_line.md)
