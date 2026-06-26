# FOM SISO Showcase

Use this when you need a standards-backed narrative packet for the high-value
SISO families rather than just a validation table.

If the first question is "how do these families hook into each other?", read
[`fom_siso_family_map.md`](fom_siso_family_map.md) before this page.

## Front Door

- `./tools/fom-siso-showcase`
- `./tools/fom-siso-showcase --packet link16-standalone-template`
- `./tools/fom-siso-showcase --packet link16-rpr2-integrated --packet rpr3-annex-a-normative`

Generated artifacts land under:

- `artifacts/fom_siso_showcase/fom_siso_showcase_report.json`
- `artifacts/fom_siso_showcase/fom_siso_showcase_report.md`
- `artifacts/fom_siso_showcase/fom_siso_showcase.html`
- `artifacts/fom_siso_showcase/workbench/fom_workbench_snapshot.json`
- `artifacts/fom_siso_showcase/workbench/fom_workbench.html`

## What It Does

The showcase packet turns the existing repo surfaces into a displayable story:

- validator packets
- protobuf and XML round-trip packets
- merged FOM overview packets
- a dedicated HTML showcase front door
- a workbench snapshot and HTML view with named custom load sets
- expected-vs-actual bucket checks for each showcase packet

The generated HTML page also includes a lane legend so operators can tell the
difference between template rejection, merge/load proof, round-trip pressure,
schema-only lanes, runtime-backed scenarios, and curated showcase packets.

It does not claim that every third-party FOM is already backed by runnable
federate code in this repo. The goal is narrower and more honest:

- show which packets are intentionally clean
- show which packets are intentionally stress-only
- show which template-like packets should fail fast
- turn those outcomes into a presentable narrative with exact artifacts

## Included Showcase Packets

- `link16-standalone-template`
  - expected: `parse-fail-fast`
  - purpose: demonstrate that standalone Link 16 is a template-like stressor,
    not a complete federation root in this parser
- `link16-rpr2-integrated`
  - expected: `validate-clean` or `roundtrip-only-stress`
  - purpose: demonstrate Link 16 as an integrated tactical comms slice inside
    a broader RPR family
- `rpr3-annex-a-normative`
  - expected: `roundtrip-only-stress`
  - purpose: present the current normative RPR 3.0 family as the main tactical
    showcase packet while being explicit that it currently validates on a 2010
    compatibility lane and stresses the 2025 round-trip lane
- `rpr3-merged-informative-1516-2010`
  - expected: `roundtrip-only-stress`
  - purpose: present a large merged stress packet for parser, JSON-cycle, and
    visualizer pressure
- `space-fom-core`
  - expected: `roundtrip-only-stress` or `validate-clean`
  - purpose: present a broader ontology with environment, management, entity,
    and orbital-state datatype pressure

## Why It Matters

The showcase surface is the shortest honest answer to:

- what should we demo first?
- which packet proves integration versus just scale?
- where do the four FOM tools already have something worth showing?

Use it alongside:

- [fom_siso_family_map.md](fom_siso_family_map.md)
- [fom_validate.md](fom_validate.md)
- [fom_workbench.md](fom_workbench.md)
- [fom_reading_map.md](fom_reading_map.md)
- [fom_siso_quirks.md](fom_siso_quirks.md)
- [rpr_siso_feedback_log.md](rpr_siso_feedback_log.md)
