# Requirements Structure Packet

This note explains how the requirements program is laid out in this repo so
far, why the files are split the way they are, and where to look next.

This page explains structure. It is not the canonical owner map for
requirement-family closure.

## Purpose

The repo tracks three different things at once:

1. the external packet intake as received
2. the repo-native harmonized working catalog
3. the executable proof that keeps requirement claims honest

Those are intentionally separated. The packet intake is preserved for audit and
provenance. The harmonized catalog is where engineering decisions happen. The
tests and generated artifacts are where claims become defensible.

## Current layout

The current layout is:

`requirements/imports/...` -> imported packet source material

`requirements/2010/*.csv` -> curated harmonized 2010 working set

`tests/verification/*` and focused runtime tests -> executable proof

`analysis/compliance/*` -> generated rollups and backlog views

`docs/verification/*` -> reader-facing maps and packets

That split avoids two common failure modes:

- treating imported packet rows as if they were already repo-native proof
- flattening narrow executable coverage into broader standard claims

## Canonical 2010 Owner Surfaces

This packet explains structure, but it is not the canonical owner map.

For the owner surfaces behind each 2010 family bucket, use:

- `docs/requirements/ieee-1516-2010/README.md`
- `requirements/2010/README.md`
- `docs/verification/requirements_hierarchy.md`

If a family-level status changes, update the canonical owner file first and use
this packet only to explain how the source, bridge, and proof layers relate.

## Imported packet layer

The imported packet is preserved under
`requirements/imports/hla_1516_requirements_codebase_packet_v1_0/`.

Use that tree when you need:

- `latest/` for the canonical v1.0 packet outputs
- `catalogs/` for carried-forward API, XSD, WSDL, and MIM catalogs
- `history/` for tranche history and audit snapshots
- `work_packet/` for the placement plan, hookup tasks, and schema contract
- `MANIFEST.json` for the audit inventory and checksums

This layer is intentionally not the live working catalog. It is the intake
baseline.

## Harmonized catalog layer

The curated 2010 working set lives in `requirements/2010/*.csv`.

The layout is not one giant flat standards dump. It is split into requirement
families that match how this repo can honestly verify behavior:

- framework and architecture
- clause-level service bridges
- whole-family detailed reconciliations
- packet-wide rollups

The practical pattern is:

1. carry a coarse or clause-focused engineering file when the standard family
   is too broad to verify directly
2. add a detailed reconciliation file that maps imported packet rows onto that
   narrower repo-native structure
3. roll those reconciliations back up into the imported master index

Use the shared shard-versus-view rule alongside that layout:

- `shards` own executable pass/fail proof
- `views` are overlapping audit or reading cuts
- canonical owner rows change status only through the narrowest owning shard
- broader views may summarize that result, but they do not replace shard
  ownership

## Core file families

These file families matter most.

### 1. Seed and clause files

These establish repo-native structure before every imported packet row is
harmonized.

Examples:

- `requirements/2010/hla1516_framework_rules.csv`
- `requirements/2010/hla1516_1_clause_4_fm_service_decomposition.csv`
- `requirements/2010/hla1516_1_clause_5_declaration_management.csv`
- `requirements/2010/hla1516_1_clause_6_object_management.csv`

These files are narrower than the imported packet. They are built to drive
implementation and test design.

### 2. Detailed reconciliation files

These are the main bridge files. They translate imported packet rows into the
repo's current evidence vocabulary and carry the canonical requirement
judgment, while backend-specific support stays in separate columns or linked
artifacts.

Examples:

- `requirements/2010/hla1516_1_fm_detailed_reconciliation.csv`
- `requirements/2010/hla1516_1_dm_detailed_reconciliation.csv`
- `requirements/2010/hla1516_1_om_detailed_reconciliation.csv`
- `requirements/2010/hla1516_1_own_detailed_reconciliation.csv`
- `requirements/2010/hla1516_1_tm_detailed_reconciliation.csv`
- `requirements/2010/hla1516_1_ddm_detailed_reconciliation.csv`
- `requirements/2010/hla1516_1_sup_detailed_reconciliation.csv`
- `requirements/2010/hla1516_1_mom_detailed_reconciliation.csv`
- `requirements/2010/hla1516_1_api_detailed_reconciliation.csv`
- `requirements/2010/hla1516_1_conf_detailed_reconciliation.csv`
- `requirements/2010/hla1516_xml_detailed_reconciliation.csv`
- `requirements/2010/hla1516_2_omt_detailed_reconciliation.csv`
- `requirements/2010/hla1516_2_omt_xml_detailed_reconciliation.csv` legacy bridge artifact
- `requirements/2010/hla1516_framework_detailed_reconciliation.csv`

This is the real working center of gravity.

### 3. Packet-wide rollups

These give the current program state from the packet's point of view.

- `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`
- `requirements/2010/hla_1516_packet_hookup_status_v1_0.csv`

The master harmonization index answers:

- which imported master rows have been reconciled into repo-native bridges
- which still remain narrower than the standard wording
- which have no harmonized bridge yet

The hookup status file answers a different question:

- which packet integration tasks are already satisfied by the repo layout

## Why the layout works this way

The structure is built around proof shape, not around document purity.

That means:

- clause decomposition exists where the packet rows are too coarse to drive
  implementation or tests
- whole-family reconciliations exist where the packet has broader families that
  need to inherit narrower, test-backed closure
- the imported master index is regenerated from the detailed bridges instead of
  edited as a standalone truth source

This keeps the direction of truth clear:

`focused requirement row -> direct evidence -> family bridge -> master index`

not:

`broad packet row -> optimistic claim -> later search for evidence`

## Canonical Status Versus Backend Resolution

Do not overload one field to mean both:

- the canonical requirement judgment
- backend-by-backend or route-by-route support

Good shape:

- canonical status: `partial`
- backend resolution: `python=verified`, `pitch=vendor-divergent`,
  `certi=not-yet-tested`
- primary shard: the exact command or lane that justified the requirement-level
  status change

The harmonized catalogs use a narrow canonical-status vocabulary:

- `mapped`: direct executable or generated proof exists for the exact claim
- `partial`: the repo proves a narrower supported subset than the standard row
- `planned`: accepted scope, but direct proof is still missing
- `covered`: used in the newer 2025 harmonization packet when a row-level audit
  plus explicit evidence anchors close the repo-native claim
- `duplicate/umbrella`: grouping or normalization row, not a standalone proof
  row
- `retired/legacy-only`: explicit exclusion or migration-boundary row
- `unreconciled`: used in imported rollups only when no detailed bridge has yet
  closed the row

The practical rule is simple:

- if a test proves only a subset, keep the broad row `partial`
- if a negative test defines the boundary, keep that boundary explicit
- do not promote rows based on implementation proximity alone
- if backend support diverges, keep that divergence in separate backend columns
  or linked backend-resolution artifacts rather than flattening it into the
  canonical status cell

For the 2025 grouped harmonization surface specifically:

- the grouped worklist is now fully dispositioned:
  - `57 covered`
  - `5 duplicate/umbrella`
  - `2 retired/legacy-only`
- that removes stale grouped `planned` and `partial` bucket debt
- it does not erase row-level bounded-scope limits or make umbrella and retired rows behave like standalone runtime proof

## Clause 4 as the model

Federation Management is the clearest example of the layout strategy.

`requirements/2010/hla1516_1_clause_4_fm_service_decomposition.csv` decomposes the
family into implementation-driving row kinds:

- `SIG`
- `PRE`
- `EFF`
- `CB`
- `EXC`
- `MOM`
- `TEST`

Then `requirements/2010/hla1516_1_fm_detailed_reconciliation.csv` maps the imported
packet's finer row kinds such as `SVC`, `ARG`, `PRE`, `EFF`, `EXC`, `RTI_API`,
`FED_CB`, and related callback or observer slices onto that decomposition and
onto the runtime tests that actually exist.

That two-step shape is why the repo can tighten evidence in small tranches
without rewriting the whole catalog every time.

## Preferred Closeout Shape

When you add or revise a requirement-closeout table, prefer these columns:

| Column | Meaning |
| --- | --- |
| `Requirement family` | clause, capability family, or grouped bucket |
| `Requirement IDs` | exact IDs or grouped row identifiers |
| `Canonical status` | `planned`, `partial`, `mapped`, `covered`, `duplicate/umbrella`, or `retired/legacy-only` |
| `Backend resolution` | separate backend columns or a linked backend-resolution artifact |
| `Primary shard` | first canonical shard that owns the proof |
| `Widen to` | broader shard or route only if the claim crosses that boundary |
| `View tags` | overlapping audit cuts such as `time`, `ownership`, or `fom-omt` |
| `Evidence artifact` | CSV, packet, JSON, or proof note that records the result |
| `Boundary note` | honest supported-scope or exclusion note |

## Current pinned state

Per `requirements/imports/hla_1516_requirements_codebase_packet_v1_0/HARMONIZATION_NOTES.md`,
the current imported master harmonization index stands at:

- `2675 mapped`
- `1328 partial`
- `0 planned`
- `0 unreconciled`

That does not mean every broad standards claim is fully closed. It means every
imported master row is now represented by a harmonized bridge and is carrying
an explicit status rather than sitting outside the catalog.

## Reader map

Use these entry points in this order:

1. `requirements/README.md` for the source-family inventory
2. `docs/verification/requirements_hierarchy.md` for the reader-facing L1/L2/L3
   hierarchy
3. `requirements/imports/.../HARMONIZATION_NOTES.md` for the packet pin and
   imported-versus-curated split
4. `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` for current
   packet-wide status
5. the relevant `*_detailed_reconciliation.csv` file for actual row-level work

## What is still structurally unfinished

The layout is coherent now, but the work is not fully done.

What remains is mostly evidence tightening inside existing bridge files:

- replace indirect anchors with direct runtime or verifier-backed witnesses
- keep burning down `partial` rows where the repo can prove a broader exact
  behavior
- keep broad rows partial when only a narrower supported subset is honest

So the remaining work is less about inventing new structure and more about
improving the truthfulness and sharpness of the existing structure.
