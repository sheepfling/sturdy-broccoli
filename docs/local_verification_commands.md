# Local Verification Commands

These are the commands captured in the latest local verification note.

```bash
./tools/test-surface recommend
./tools/python verify-fast
./tools/python verify-main-2025
./tools/python verify-routes-preflight
./tools/python verify-routes
./tools/python verify-routes-2025
python3 scripts/run_spec2025_finish_line.py
./tools/lint
./tools/test
./tools/python verify
./tools/vendor-green matrix
./tools/two-federate --output-dir analysis/python_two_federate_suite_2026-06-07
python3 -m pytest -q tests/runtime/test_real_rti.py
./tools/certi-easy verify-best-effort
./tools/pitch preflight
./tools/pitch verify
./tools/pitch verify-best-effort
./tools/pitch smoke
./tools/pitch smoke-best-effort
```

Use this page when you want the exact local commands, not the broader status.

For the primary 2025 Python RTI lane, interpret these commands through the
audited `hla-backend-python2025` runtime. `hla-backend-shim` is only
temporary import-compatibility scaffolding plus
compatibility-wrapper/import-compatibility code, and the hosted 2025 gRPC
route is a bounded route variant rather than a separate RTI family.

Use this operator rule consistently:

- `./tools/python verify-main-2025` is the default proof path for the real
  2025 Python RTI
- `./tools/python verify-routes-2025` extends that proof across the hosted
  FedPro route
- shim checks are guardrails around the main lane, not a parallel
  implementation lane

`./tools/python verify-main-2025` is the regular main-surface lane for the
current `python2025` backend claim. It runs the direct in-process runtime proof
selectors, the package/runtime boundary guardrails that keep `shim`
compatibility-only, the 2025 requirements-registry and bounded proof-note
surface, plus the dedicated OMT validation/parsing evidence surface, without
mixing that claim into hosted-route hygiene.

That main-surface lane also includes the explicit raw `python2025` proofs for
support-service handle-factory/decode behavior, snake-case direct-surface
aliases, and callback-control services on `hla-backend-python2025` itself.
It also names the Target/Radar time-window ladder explicitly: the integrated
lookahead-processing-window gauntlet, the core/future-exclusion/output-delivery/
consumer-order/pipeline/receive-order-poison scenarios, the restore-state /
restore-output / pipeline-restore legs, and the matching negative-oracle
rejection checks.
It now also names the save/restore proof family explicitly: the backend-neutral
save/restore route, queued-callback restore behavior, scheduled time-state
restore behavior, the direct federation save/restore lifecycle path, the
example-FOM save/restore gauntlet, the smoke ownership rollback gauntlet, the
dirty-lookahead rollback with pre-save queued-TSO redelivery path, and the
restore-output / restore-pipeline replay guards.
It now also names the service-heavy proof family explicitly: direct automatic
resign support-service state, callback-control over live object reflection,
ownership acquire/query/negotiation flows, and direct MOM report/control/action
routing on the `python2025` surface.
It now also names the federation/object/DDM proof family explicitly: lifecycle,
listing, object-and-interaction exchange, name reservation, region/DDM
lifecycle and declaration gating, object-scope relevance, and directed-routing
checks on the direct `python2025` surface.

Direct real-runtime pytest paths are now secondary diagnostics. Use the vendor
operator path first so preflight is confirmed before the runtime tests start.
Use `./tools/certi-easy verify-best-effort` or the `*-best-effort` Pitch routes
when you need the same normalized artifacts in a sandboxed or local
environment that cannot satisfy the strict vendor runtime prerequisites.

`./tools/python verify-routes` is the regular hygiene lane for the 2010 hosted
Python RTI surface. Run it after changes to `hla.backends.inmemory`,
`python-grpc`, the older Python direct-vs-gRPC parity fixtures, or the hosted
2010 Target/Radar example path.

`./tools/python verify-routes-2025` is the regular hygiene lane for the main
`python2025` RTI plus the bounded hosted `python-2025-fedpro-grpc` route. Run
it after changes to 2025 transport-hosted client/server wiring, hosted-route
examples, the in-process Target/Radar time-window proof ladder, direct
`python2025` save/restore, ownership, callback, support-service, or MOM
proofs, the checked-in 2025 finish-line bundle, the 2025 route-parity ledger,
the 2025 requirements-registry and bounded proof-note surface, or other route-level behavior that must
stay aligned between the direct `python2025` lane and the hosted FedPro route.
It also names the hosted Target/Radar time-window family explicitly through the
factory-hosted and shared FedPro Target/Radar example, future-exclusion,
output-delivery, consumer-order, integrated-gauntlet, receive-order-poison,
restore-output, and pipeline-restore scenario routes before the full transport
suite runs.
It now also names the hosted save/restore family explicitly through the shared
FedPro save/restore route, queued-callback and scheduled time-state restore
routes, lifecycle and per-peer status tracking, the example-FOM and smoke
ownership gauntlets, and the hosted dirty-lookahead / restore-output replay
guards before the full transport suite runs.
It now also names the hosted service-heavy family explicitly through FedPro
support-service and switch round trips, hosted ownership acquire/negotiation
flows, and hosted MOM manager/service/control/exception routing before the full
transport suite runs.
It now also names the hosted federation/object/DDM family explicitly through
shared FedPro lifecycle/listing routes, hosted object exchange and name
reservation, hosted region/DDM lifecycle and declaration gating, hosted
object-scope relevance, and hosted directed-routing checks before the full
transport suite runs.

`python3 scripts/run_spec2025_finish_line.py` is the explicit manual refresh
entrypoint for the checked-in 2025 evidence bundle. Use it when you want to
rebuild the finish-line snapshot, verification matrix, and route-parity
artifacts without rerunning the full `verify-routes-2025` hosted lane.

For 2025 runtime ownership and proof status behind those commands, use:

- [`python_rti_backend.md`](python_rti_backend.md)
- [`python_rti_reading_map.md`](python_rti_reading_map.md)
- [`verification/time_model_compliance.md`](verification/time_model_compliance.md)
