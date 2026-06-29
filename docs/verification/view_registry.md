# Verification View Registry

Use this page when the question is:

- which focused target or audit slice should I use?
- where do overlapping proof cuts live?
- why can two slices cover some of the same tests without conflicting?

This is the canonical registry for overlapping verification views.

Read it together with:

- [`shard_registry.md`](shard_registry.md) for runnable shard ownership
- [`../test_surface.md`](../test_surface.md) for operator-facing lane selection
- [`../plans/requirements_remaining_closure.md`](../plans/requirements_remaining_closure.md)
  for requirement-facing shard-versus-view rules

## Rules

Treat these statements as hard rules:

1. views may overlap freely
2. views answer audit, restart, or focused-rerun questions
3. views do not replace canonical shard ownership
4. views do not define repo-green by themselves
5. backend divergence still belongs in backend-resolution columns or companion
   artifacts, not in view labels

## Focused Rerun Views

These focused targets come from
[`../../testing/test_focus_manifest.json`](../../testing/test_focus_manifest.json).

| View | Primary command | Alias hints | Overlaps commonly with | Main question answered |
| --- | --- | --- | --- | --- |
| `foundation` | `./tools/test-focus run foundation` | `policy`, `boundaries` | `unit-foundation` | did package policy or import structure drift? |
| `python-examples` | `./tools/test-focus run python-examples` | `examples-python` | `unit-python-core` | did direct Python example behavior drift? |
| `java-bridges` | `./tools/test-focus run java-bridges` | `bridges-java` | `unit-shim-tooling` | did bridge-wrapper behavior drift? |
| `jpype` | `./tools/test-focus run jpype` | `bridge-jpype`, `vendor-pitch-jpype` | `java-bridges`, `vendor` | is the JPype side specifically broken? |
| `py4j` | `./tools/test-focus run py4j` | `bridge-py4j`, `vendor-pitch-py4j` | `java-bridges`, `vendor` | is the Py4J side specifically broken? |
| `fom` | `./tools/test-focus run fom` | `foms` | `unit-fom-tooling` | did parser, schema, or factory behavior drift? |
| `target-radar` | `./tools/test-focus run target-radar` | `fom-target-radar`, `radar` | `unit-scenarios-light`, `python1516_2025-main` | did the shared Target/Radar scenario surface drift? |
| `python-2025-runtime` | `./tools/test-focus run python-2025-runtime` | `runtime-2025`, `python1516_2025` | `unit-python-2025-core`, `python1516_2025-main` | did broad direct 2025 runtime semantics drift? |
| `execution-membership` | `./tools/test-focus run execution-membership` | `membership-guards`, `not-joined`, `lifecycle-guards` | `unit-scenarios-light`, `unit-python-2025-core`, `unit-transport-local`, `python1516_2025-routes` | did connect/join/resign/destroy state guards or not-joined update/send/query rejection drift on the direct lane or hosted 2025 gRPC/FedPro route or the REST-hosted Python route? Use `transport` instead when the question is generic REST parity or transport plumbing. |
| `python-2025-time` | `./tools/test-focus run python-2025-time` | `time-2025`, `window-2025` | `python-2025-runtime`, `target-radar`, `python1516_2025-routes` | did time-window or lookahead behavior drift? |
| `python-2025-save-restore` | `./tools/test-focus run python-2025-save-restore` | `save-restore-2025`, `restore-2025` | `python-2025-runtime`, `python1516_2025-routes` | did save/restore or rollback behavior drift on the direct lane or hosted 2025 gRPC/FedPro route? |
| `python-2025-ownership` | `./tools/test-focus run python-2025-ownership` | `ownership-2025` | `python-2025-runtime`, `python1516_2025-routes` | did ownership behavior drift on the direct lane or hosted 2025 gRPC/FedPro route? |
| `python-2025-ddm` | `./tools/test-focus run python-2025-ddm` | `ddm-2025`, `regions-2025` | `python-2025-runtime`, `python1516_2025-routes` | did DDM region-routing, overlap filtering, passive aliases, or restore cleanup drift on the direct lane or hosted 2025 gRPC/FedPro route? |
| `python-2025-mom-callbacks` | `./tools/test-focus run python-2025-mom-callbacks` | `mom-2025`, `callbacks-2025`, `support-2025` | `python-2025-runtime`, `python1516_2025-routes` | did MOM, callback, or support-service behavior drift on the direct lane or hosted 2025 gRPC/FedPro route? |
| `transport` | `./tools/test-focus run transport` | `grpc`, `rest` | `unit-transport-local`, `python-routes`, `python1516_2025-routes` | did hosted route transport behavior drift? |
| `routes-2025` | `./tools/test-focus run routes-2025` | `fedpro-2025`, `grpc-2025`, `route-parity-2025` | `transport`, `python1516_2025-routes`, `requirements-2025` | did the hosted 2025 route parity or bounded hosted-owner surface drift? |
| `backends` | `./tools/test-focus run backends` | `backend-integration` | `unit-scenarios-light`, `vendor` | did backend adapter behavior drift? |
| `rti-core` | `./tools/test-focus run rti-core` | `rti-factory`, `core-factory` | `unit-python-core`, `foundation` | did core RTI discovery or factory selection drift? |
| `requirements-2025` | `./tools/test-focus run requirements-2025` | `closeout-2025`, `requirements`, `parity-2025` | `routes-2025`, `verification`, `matrix` | did the 2025 canonical requirement catalog, backend-resolution companion, route parity, or canonical owner surfaces drift? |
| `verification` | `./tools/test-focus run verification` | `verification-harness` | `requirements-2025`, `matrix` | did detailed ledgers or verification harnesses drift? |
| `time` | `./tools/test-focus run time` | `time-suite` | `python-2025-time`, `python1516_2025-main` | did time-management algorithms or backend matrices drift? |
| `vendors` | `./tools/test-focus run vendors` | `vendor-runtime` | `unit-vendor-onboarding`, `vendor` | did real vendor-runtime behavior drift? |

## Audit Views

These are document-level views that overlap runnable shards:

| View tag | Typical owner docs | Typical shard owners |
| --- | --- | --- |
| `2010-core` | 2010 bounded family notes and source ledgers | `unit-python-core`, `unit-scenarios-light` |
| `2025-core` | 2025 bounded proof notes plus the canonical requirement catalog and backend-resolution companion | `unit-python-2025-core`, `python1516_2025-main` |
| `transport` | hosted-route boundary docs and route-parity artifacts | `unit-transport-local`, `python-routes`, `python1516_2025-routes` |
| `setup-preflight` | onboarding, toolchain, and environment docs | `unit-foundation`, `unit-vendor-onboarding`, `unit-shim-tooling` |
| `execution-membership` | federation-management and object-management owner docs that talk about joined versus not-joined rules | `unit-scenarios-light`, `unit-python-2025-core`, `unit-transport-local` for the hosted 2025 gRPC/FedPro slice plus the REST-hosted Python route, `python1516_2025-routes`; use the broader `transport` view for generic REST-hosted route questions |
| `java-shim` | Java toolchain and standard-shim docs | `unit-shim-tooling` |
| `cpp-shim` | C++ toolchain and standard-shim docs | `unit-shim-tooling` |
| `ownership` | ownership bounded proof notes and canonical owner companions | `unit-python-2025-core`, `python1516_2025-main` |
| `time` | time-model compliance and bounded proof notes | `unit-python-2025-core`, `python1516_2025-main`, `python1516_2025-routes` |
| `save-restore` | save/restore bounded proof notes and route parity | `python1516_2025-main`, `python1516_2025-routes` |
| `ddm` | DDM bounded proof notes and region-routing evidence | `unit-python-2025-core`, `python1516_2025-main`, `python1516_2025-routes` |
| `fom-omt` | OMT, XML, parser, and validation docs | `unit-fom-tooling`, `python1516_2025-main` |
| `scenarios` | Target/Radar and scenario-backed bounded proof notes | `unit-scenarios-light`, `python1516_2025-main` |
| `closeout-reporting` | closeout packets, audits, and exports | `requirements-2025`, `verification`, `matrix` |

## Practical Rule

When choosing between a shard and a view:

1. if you need stable pass/fail ownership, use a shard
2. if you need a thematic rerun or audit slice, use a view
3. if a requirement status changes, record the owning shard first and the view
   second

## Related Docs

- [`shard_registry.md`](shard_registry.md)
- [`../test_surface.md`](../test_surface.md)
- [`../local_verification_commands.md`](../local_verification_commands.md)
- [`../plans/PLN-005_requirements_shards_views_and_verification_plan.md`](../plans/PLN-005_requirements_shards_views_and_verification_plan.md)
