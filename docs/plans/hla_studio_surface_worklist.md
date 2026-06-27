# HLA Studio Surface Worklist

This worklist converts the high-priority backlog from
[`../runtime_surface_naming_and_backlog.md`](../runtime_surface_naming_and_backlog.md)
into tracked repo-native execution items.

Use this file when the question is:

- what is the next concrete HLA Studio surface task
- which naming and operator-surface items are already done
- what still blocks the three surfaces from feeling cohesive

Status values:

- `done`: implemented and verified
- `ready`: approved next item with enough detail to start
- `queued`: worthwhile but blocked behind a higher-priority item

## Scope

These tickets cover the three operator-facing HLA Studio surfaces:

- `FOM Explorer`
- `Federation Visualizer`
- `RTI Bridge API`

They also cover the cross-surface glue that makes them work as one story.

## Active Worklist

| Ticket | Surface | Status | Objective | Verification |
| --- | --- | --- | --- | --- |
| `STUDIO-001` | `FOM Explorer` | `done` | show `FOM Explorer` as the visible HTML product header while preserving `FOM Workbench` as an alias in tools and artifact names | `tests/factories/test_fom_workbench.py` |
| `STUDIO-002` | `Federation Visualizer` | `done` | keep the preferred `Federation Visualizer` product header explicit in the live HTML surface and mark it as an HLA Studio surface | `tests/scenarios/test_runtime_observer_fastapi.py` |
| `STUDIO-003` | `RTI Bridge API` | `done` | replace the raw root JSON landing with an operator-facing `RTI Bridge API` HTML landing page while keeping `federate-service` as the alias and service id | `tests/scenarios/test_federate_service_fastapi.py` |
| `STUDIO-004` | `Cross-surface` | `done` | add one aggregate `HLA Studio` index page that links the three surfaces plus available generated artifacts | `tests/scenarios/test_runtime_observer_fastapi.py`, `tests/scenarios/test_hla_studio_index.py` |
| `STUDIO-005` | `Cross-surface` | `done` | export a bridge contract artifact into the HLA Studio index so non-UI consumers have a stable offline entry | `tests/scenarios/test_runtime_observer_fastapi.py` |
| `STUDIO-006` | `FOM Explorer` | `ready` | add one-click scenario presets for `Link 16`, `RPR 3.0`, `Space FOM`, and repo-owned small examples | focused workbench browser tests plus `tests/factories/test_fom_siso_showcase.py` |
| `STUDIO-007` | `FOM Explorer` | `ready` | add a stronger validation summary rail with issue counts by severity and by source file | `tests/factories/test_fom_workbench.py`, `tests/factories/test_fom_validate.py` |
| `STUDIO-008` | `FOM Explorer` | `ready` | add round-trip and parser-stress badges directly in the explorer cards | `tests/factories/test_fom_workbench.py`, `tests/factories/test_fom_siso_audit.py` |
| `STUDIO-009` | `Federation Visualizer` | `ready` | add a visible execution summary strip for scenario, edition, backend, federate count, phase, and event rate | `tests/scenarios/test_runtime_observer_fastapi.py`, screenshot packet coverage |
| `STUDIO-010` | `Federation Visualizer` | `ready` | add stronger late-join hydration so object and interaction inspectors populate quickly from retained state | `tests/scenarios/test_runtime_observer_fastapi.py`, observer core scenario tests |
| `STUDIO-011` | `Federation Visualizer` | `ready` | add top-level artifact drawer links for listener summary, trace, state snapshot, and gallery outputs | `tests/scenarios/test_runtime_observer_fastapi.py`, `tests/scenarios/test_siso_runtime_surface_matrix.py` |
| `STUDIO-012` | `RTI Bridge API` | `ready` | group bridge docs by RTIambassador service family and show session lifecycle examples matching the Java mapping names | `tests/scenarios/test_federate_service_fastapi.py` plus contract generation tests |
| `STUDIO-013` | `RTI Bridge API` | `ready` | add better error payload examples and status code guidance on the landing page and docs | `tests/scenarios/test_federate_service_fastapi.py` |
| `STUDIO-014` | `Cross-surface` | `ready` | standardize preferred names in screenshot packets, matrix reports, and generated galleries | `tests/scenarios/test_ui_surface_screenshot_packet.py`, `tests/scenarios/test_siso_runtime_surface_matrix.py` |
| `STUDIO-015` | `Cross-surface` | `ready` | add cross-links from `FOM Explorer` to exact visualizer classes and from the visualizer to exact bridge examples | visualizer/workbench focused tests plus screenshot capture coverage |
| `STUDIO-016` | `Cross-surface` | `queued` | add stable screenshot scene ids so demos regenerate the same panels deterministically across capture runs | screenshot packet tests and gallery manifest validation |

## Notes

- `STUDIO-001` through `STUDIO-005` are the naming and aggregation baseline.
- `STUDIO-006` through `STUDIO-011` are the next operator-value items.
- `STUDIO-012` and `STUDIO-013` keep the bridge usable for humans instead of only contract tooling.
- `STUDIO-014` and `STUDIO-015` are the next cohesion pass once the individual surfaces are stronger.

## Update Rule

When one of these items changes status:

1. update this file
2. update [`../runtime_surface_naming_and_backlog.md`](../runtime_surface_naming_and_backlog.md) only if the product-facing backlog itself changed
3. keep the code/tool aliases stable unless there is an explicit migration decision
