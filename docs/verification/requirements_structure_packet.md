# Requirements Structure Packet

This note explains how the requirements program is laid out in this repo so
far, why the files are split the way they are, and where to look next.

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

`requirements/*.csv` -> curated harmonized working set

`tests/verification/*` and focused runtime tests -> executable proof

`analysis/compliance/*` -> generated rollups and backlog views

`docs/verification/*` -> reader-facing maps and packets

That split avoids two common failure modes:

- treating imported packet rows as if they were already repo-native proof
- flattening narrow executable coverage into broader standard claims

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

The curated working set lives in top-level `requirements/*.csv`.

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

## Core file families

These file families matter most.

### 1. Seed and clause files

These establish repo-native structure before every imported packet row is
harmonized.

Examples:

- `requirements/hla1516_framework_rules.csv`
- `requirements/hla1516_1_clause_4_fm_service_decomposition.csv`
- `requirements/hla1516_1_clause_5_declaration_management.csv`
- `requirements/hla1516_1_clause_6_object_management.csv`

These files are narrower than the imported packet. They are built to drive
implementation and test design.

### 2. Detailed reconciliation files

These are the main bridge files. They translate imported packet rows into the
repo's current evidence vocabulary and mark each row `mapped`, `partial`, or
`planned`.

Examples:

- `requirements/hla1516_1_fm_detailed_reconciliation.csv`
- `requirements/hla1516_1_dm_detailed_reconciliation.csv`
- `requirements/hla1516_1_om_detailed_reconciliation.csv`
- `requirements/hla1516_1_own_detailed_reconciliation.csv`
- `requirements/hla1516_1_tm_detailed_reconciliation.csv`
- `requirements/hla1516_1_ddm_detailed_reconciliation.csv`
- `requirements/hla1516_1_sup_detailed_reconciliation.csv`
- `requirements/hla1516_1_mom_detailed_reconciliation.csv`
- `requirements/hla1516_1_api_detailed_reconciliation.csv`
- `requirements/hla1516_1_conf_detailed_reconciliation.csv`
- `requirements/hla1516_xml_detailed_reconciliation.csv`
- `requirements/hla1516_2_omt_detailed_reconciliation.csv`
- `requirements/hla1516_2_omt_xml_detailed_reconciliation.csv`
- `requirements/hla1516_framework_detailed_reconciliation.csv`

This is the real working center of gravity.

### 3. Packet-wide rollups

These give the current program state from the packet's point of view.

- `requirements/hla_1516_master_harmonization_index_v1_0.csv`
- `requirements/hla_1516_packet_hookup_status_v1_0.csv`

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

## Status vocabulary

The harmonized catalog uses a narrow vocabulary:

- `mapped`: direct executable or generated proof exists for the exact claim
- `partial`: the repo proves a narrower supported subset than the standard row
- `planned`: accepted scope, but direct proof is still missing
- `unreconciled`: used in the imported master index when no detailed bridge has
  closed the row yet

The practical rule is simple:

- if a test proves only a subset, keep the broad row `partial`
- if a negative test defines the boundary, keep that boundary explicit
- do not promote rows based on implementation proximity alone

## Clause 4 as the model

Federation Management is the clearest example of the layout strategy.

`requirements/hla1516_1_clause_4_fm_service_decomposition.csv` decomposes the
family into implementation-driving row kinds:

- `SIG`
- `PRE`
- `EFF`
- `CB`
- `EXC`
- `MOM`
- `TEST`

Then `requirements/hla1516_1_fm_detailed_reconciliation.csv` maps the imported
packet's finer row kinds such as `SVC`, `ARG`, `PRE`, `EFF`, `EXC`, `RTI_API`,
`FED_CB`, and related callback or observer slices onto that decomposition and
onto the runtime tests that actually exist.

That two-step shape is why the repo can tighten evidence in small tranches
without rewriting the whole catalog every time.

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
4. `requirements/hla_1516_master_harmonization_index_v1_0.csv` for current
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
