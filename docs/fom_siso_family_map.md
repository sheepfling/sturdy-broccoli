# SISO FOM Family Map

Use this page when the question is not "does this XML parse?" but:

- how do the SISO families relate to each other?
- which XMLs are roots versus extensions?
- which family loads need companion modules?
- which ones force parser normalization or special handling?
- which ones run with Pitch, and on which boundary?
- which HLA edition lane should I think about for each packet?

This is the front-door mental model for the SISO corpus in this repo.

## Short Answer

There are three main families worth thinking about first:

1. `Link 16`
   - not the main federation root by itself
   - best treated as an extension slice over `RPR 2.0`
2. `RPR`
   - the main tactical family
   - comes in two important practical shapes here:
     - `RPR 2.0` with Link 16 integration
     - `RPR 3.0` normative/informative packets
3. `Space FOM`
   - separate family
   - broader ontology, no RPR dependency

If you remember only one thing, remember this:

- `Link 16` is usually an add-on story
- `RPR` is the main tactical root story
- `Space FOM` is its own independent family story

## Diagram

```text
SISO family relationships in this repo

  Link_16_v2.0.xml
        |
        | extension / add-on
        v
  RPR 2.0 ordered family ------------------> link16-rpr2-integrated
        |
        | older tactical parent family
        |
        +----------------------------------> standalone RPR 2.0 family loading

  RPR 3.0 Annex A normative family --------> rpr3-annex-a-normative
        |
        +----------------------------------> merged informative 1516-2010 stress packet

  Space FOM ordered family ----------------> space-fom-core

Meaning:
  - Link 16 is attached to the RPR 2.0 story here
  - RPR 3.0 is a separate modern tactical branch
  - Space FOM is a separate independent branch
```

## Repo Small Example FOMs

These are the small repo-owned examples and smoke fixtures that sit alongside
the SISO families.

| Example / Fixture | Edition | Classification | Load Shape | What It Is For | Pitch / Runtime Note |
| --- | --- | --- | --- | --- | --- |
| `DemoFOMmodule.xml` | `2010` | `2010-native` | standalone | smallest bundled demo FOM; parser, round-trip, and basic runtime smoke | useful repo baseline, but real Pitch rejects this FDD in the current vendor evidence |
| `TargetRadarFOMmodule.xml` | `cross-edition` | `cross-edition exercised` | standalone | main small practical example; shared scenario/example baseline across 2010 and 2025 repo lanes | important repo-owned runtime story and vendor smoke target |
| `Proto2025_Base.xml` | `2025` | `2025-native` | base-plus-extension | shared base for the small 2025 example family | use with an extension for most practical scenarios |
| `Proto2025_MessageTest.xml` | `2025` | `2025-native` | base-plus-extension | small message/interactions example over `Proto2025_Base` | tooling and direct 2025 runtime example |
| `Proto2025_SpaceLite.xml` | `2025` | `2025-native` | base-plus-extension | small space/reference-frame flavored example over `Proto2025_Base` | small 2025 ontology example, not the full Space FOM family |
| `Proto2025_TimeMgmtTest.xml` | `2025` | `2025-native` | base-plus-extension | small time-management focused example over `Proto2025_Base` | direct 2025 time/test surface |
| `VendorSmokeFOM.xml` | `2010` | `2010-native` | standalone | tiny vendor/runtime smoke fixture | support/smoke fixture rather than main operator story |
| `EncodingSmokeTest-2025.xml` | `2025` | `2025-native` | standalone | tiny encoding/auth parser-schema smoke fixture | tooling/schema fixture, not the main federation story |
| `HLAstandardMIM.xml` | `2010` | `2010-native` | standalone | standard MIM baseline for support/merge/tooling coverage | support/reference surface, not the first demo story |

Practical grouping:

- smallest pure demo:
  - `DemoFOMmodule.xml`
- main repo-owned example:
  - `TargetRadarFOMmodule.xml`
- small modern 2025 example family:
  - `Proto2025_Base.xml` plus one extension
- tiny support/smoke fixtures:
  - `VendorSmokeFOM.xml`
  - `EncodingSmokeTest-2025.xml`
  - `HLAstandardMIM.xml`

Edition classification rule:

- `2010-native`
  - authored and cataloged as a real 2010-facing example/support FOM
- `2025-native`
  - authored and cataloged as a real 2025-facing example/support FOM
- `cross-edition exercised`
  - one XML is exercised by both runtime/validation lanes in the repo
  - this does not mean the file is literally "both standards at once"

## Family Relationship Map

| Family / Packet | What It Is | Relationship | Load Shape | Main Edition Story | Runtime Story |
| --- | --- | --- | --- | --- | --- |
| `link16-standalone-template` | standalone `Link_16_v2.0.xml` | extension/template only | effectively incomplete standalone | `2010`-shaped XML | deliberate fail-fast stressor, not the main runnable story |
| `link16-rpr2-integrated` | `RPR 2.0` ordered family plus `Link_16_v2.0.xml` | `Link 16` added into `RPR 2.0` | ordered-family | practical `2010` tactical-link story | main executable Link 16 story |
| `rpr3-annex-a-normative` | `RPR 3.0` Annex A family | independent RPR family | ordered-family | nominally `2025` family, validated on bounded lanes | main clean RPR 3.0 family story |
| `rpr3-merged-informative-1516-2010` | merged informative `RPR_FOM_v3.0_1516-2010.xml` | same ontology as RPR 3.0, different packet shape | merged stress packet | `2010` compatibility/stress packet | useful for parser/JSON/UI stress and 2010-oriented runtime path |
| `space-fom-core` | Space FOM ordered family | independent family | ordered-family | exercised on both repo edition lanes | independent showcase family |
| `u-fom` | U-FOM ordered family | independent family | ordered-family | support/high-value family, less central than the three above | primarily tooling/validation pressure |
| `standard-mim` / support XMLs | support/schema/reference material | not the main domain story | standalone/support-only | edition-specific support role | support boundary, not the first demo story |

## What Connects To What

### Link 16 and RPR 2.0

This is the most important source of confusion.

In this repo:

- standalone `Link 16` is not treated as a complete federation root
- the main Link 16 story is:
  - `RPR 2.0` family
  - plus `Link_16_v2.0.xml`
  - loaded in explicit order

Practical meaning:

- `Link 16` is an extension slice
- `RPR 2.0` is the parent tactical family
- `link16-rpr2-integrated` is the main combined packet you should think about

That is why:

- `link16-standalone-template` is expected to fail fast
- `link16-rpr2-integrated` is the real showcase/runtime packet

### RPR 2.0 versus RPR 3.0

These are related, but do not think of them as the same packet with a year
switch.

`RPR 2.0`

- practical integrated tactical family used for the Link 16 combined story
- `2010`-shaped in this repo
- ordered-family load

`RPR 3.0`

- current broader RPR family story
- practical repo handling splits by packet shape:
  - `rpr3-annex-a-normative`
  - `rpr3-merged-informative-1516-2010`

Practical meaning:

- `RPR 2.0` is where Link 16 integration is demonstrated
- `RPR 3.0` is the main modern RPR family stress/showcase path

### Space FOM

`Space FOM` is not an RPR extension.

Treat it as:

- independent family
- ordered-family assembly
- broader datatype and hierarchy pressure
- separate runtime showcase story

## Root Versus Extension

| Packet / Family | Root? | Extension? | Notes |
| --- | --- | --- | --- |
| `Link_16_v2.0.xml` by itself | no | yes | useful as template/stressor, not the main root |
| `link16-rpr2-integrated` | yes, as a combined packet | includes Link 16 extension | best mental model for Link 16 in this repo |
| `RPR 2.0` family modules | yes, as ordered family | Link 16 and Link 11 attach near the end | do not load one random member alone |
| `RPR 3.0` Annex A normative family | yes, as ordered family | no separate Link 16 repo showcase extension path here | main modern RPR family path |
| `RPR 3.0` merged informative packet | yes, as one giant packet | stress-oriented packet shape | useful but not the cleanest learning root |
| `Space FOM` family | yes, as ordered family | no | independent family |

## Edition Map

This repo separates:

- source family/version
- effective validator/runtime edition lane

Those are not always the same thing.

| Packet / Family | Source Story | Effective Repo Edition Story |
| --- | --- | --- |
| `Link 16` standalone | `2010`-shaped SISO Link 16 XML | `2010` template/stress lane |
| `link16-rpr2-integrated` | `RPR 2.0` plus Link 16 extension | main `2010` tactical-link story, also exercised by both runtime showcase editions through repo backends |
| `RPR 3.0` Annex A normative | current `RPR 3.0` family | main `2025`-named family story, but some validator/runtime paths still use bounded compatibility handling |
| `RPR 3.0` merged informative `1516-2010` | informative merged stress packet | explicit `2010` compatibility/stress story |
| `Space FOM` | independent SISO family | exercised on both `2010` and `2025` repo lanes |

Practical rule:

- `2010` and `2025` in repo reports mean "which lane we exercised"
- not always "the XML itself only belongs to that one year"

## Parser / Validator / JSON / Workbench Handling

### Out-of-the-box versus normalized

There are two different ideas:

1. ordinary ordered-family assembly
2. parser normalization of family-specific structural labels

The first is expected.
The second is where we had to do real repo work.

### RPR-specific normalization pressure

The main custom datatype pressure came from `RPR`, not from `Space FOM`.

The parser now normalizes RPR family labels such as:

- `RPRnullTerminatedArray`
- `RPRlengthlessArray`
- `RPRpaddingTo32Array`
- `RPRpaddingTo64Array`
- adjacent RPR-flavored structural labels

Into generic internal structural kinds such as:

- `null-terminated-array`
- `lengthless-array`
- `padding-to-32-bit-boundary-array`
- `padding-to-64-bit-boundary-array`

Important boundary:

- the generic datatype engine branches on generic structure
- the original RPR label is preserved only as source metadata for traceability

This means:

- we did have to absorb RPR weirdness
- but we did not leave "RPR family branching" as the long-term core design

Related docs:

- [rpr_type_normalization_notes.md](rpr_type_normalization_notes.md)
- [rpr_siso_feedback_log.md](rpr_siso_feedback_log.md)

## Parser / Validator / Tooling Flow

Use this when the question is:

- does the XML load?
- does the ordered family merge correctly?
- does the repo need source-dialect normalization?
- does the workbench/JSON-cycle/validator story exist yet?

```text
source XML or family load set
        |
        v
inventory/load-shape classification
  - standalone
  - base-plus-extension
  - ordered-family
        |
        v
shared OMT parser
  - parse XML into repo-native catalog
  - normalize source-dialect labels when needed
  - most notably RPR-branded structural encodings
        |
        v
edition-aware validation/reporting
  - 2010 lane
  - 2025 lane
  - edition-scope labeling
        |
        v
tooling surfaces
  - validator report
  - JSON cycle / round-trip
  - workbench / HTML inspector
  - showcase packets
```

Short version by family:

- `Link 16 standalone`
  - parser/tooling stress
  - expected fail-fast template lane
- `link16-rpr2-integrated`
  - parser plus ordered-family assembly plus RPR normalization
- `RPR 3.0`
  - parser plus family assembly or merged-packet stress
- `Space FOM`
  - parser plus family assembly and hierarchy breadth
- `repo small examples`
  - simpler parser/tooling/routing baselines

## Runtime / Pitch Eligibility Flow

Use this when the question is:

- can I run this as a federation scenario?
- is this Python-only or Pitch-eligible?
- is the Pitch lane real vendor runtime or bounded adapter evidence?

```text
chosen packet or family
        |
        v
is there a runnable runtime scenario in the repo?
        |
        +-- no --> parser / validator / tooling only
        |
        +-- yes
             |
             v
        choose edition lane
          - 2010
          - 2025
             |
             v
        choose topology
          - micro-2
          - 5 federates
          - 10 federates
             |
             v
        vendor eligibility decision
          - 2010 + micro-2 --> real Pitch eligible
          - 2025 + micro-2 --> bounded Pitch 202X adapter eligible
          - 5 / 10 federates --> Python-only topology
```

Runtime/Pitch status summary:

| Story | Python Runtime | Real Pitch 2010 | Bounded Pitch 202X | 5 / 10 Federates |
| --- | --- | --- | --- | --- |
| `link16-rpr2-integrated` | yes | yes, `micro-2` only | yes, `micro-2` only | Python-only |
| `rpr-runtime-*` | yes | yes, `micro-2` only | yes, `micro-2` only | Python-only |
| `space-fom-core-*` | yes | yes, `micro-2` only | yes, `micro-2` only | Python-only |
| repo small examples | yes, by fixture/use case | some smoke lanes only | bounded where explicitly wired | usually not the main Pitch topology story |
| `link16-standalone-template` | no main runnable story | no | no | no |

### Family-by-family handling summary

| Family / Packet | Loads cleanly as-is? | Needs ordered family assembly? | Needs parser normalization? | Notes |
| --- | --- | --- | --- | --- |
| `Link 16` standalone | no | n/a | not the main issue | fail-fast because it is not the practical federation root |
| `link16-rpr2-integrated` | yes, after explicit packet assembly | yes | yes, through underlying RPR family datatypes/tags | main Link 16 runtime packet |
| `RPR 2.0` family | yes, as family | yes | yes | main source of custom structural pressure |
| `RPR 3.0` family | yes, as family or merged packet depending lane | yes for Annex A | yes | same family of datatype pressure as RPR 2.0 |
| `Space FOM` | mostly family assembly pressure | yes | much less family-specific normalization pressure | broader ontology rather than branded datatype weirdness |

## Pitch / Vendor Runtime Story

This is the simplest honest answer.

### Real Pitch support versus bounded 202X wrappers

`2010`

- `micro-2` only is the real Pitch lane
- profiles:
  - `pitch-jpype`
  - `pitch-py4j`
- runtime status in showcase matrix:
  - `eligible`

`2025`

- `micro-2` only is allowed as a bounded adapter/vendor-credence lane
- profiles:
  - `pitch-202x-jpype`
  - `pitch-202x-py4j`
- runtime status in showcase matrix:
  - `bounded-eligible`
- this is not claimed as IEEE `1516.1-2025` vendor conformance

`5` and `10` federates

- Python-only in the repo showcase
- runtime status:
  - `python-only-topology`

### Family-by-family Pitch story

| Family / Packet | Real Pitch 2010? | Bounded Pitch 202X wrappers? | 5 / 10 federates on Pitch? |
| --- | --- | --- | --- |
| `link16-rpr2-integrated` | yes, `micro-2` only | yes, `micro-2` only | no |
| `rpr-runtime-*` | yes, `micro-2` only | yes, `micro-2` only | no |
| `space-fom-core-*` | yes, `micro-2` only | yes, `micro-2` only | no |
| `link16-standalone-template` | no, not the runtime packet | no | no |

Important boundary:

- "works with Pitch" means the `micro-2` showcase/parity lane
- it does not mean every packet is a free-form vendor-supported general runtime root

Related doc:

- [fom_siso_pitch_micro_parity.md](fom_siso_pitch_micro_parity.md)

## Which Packet Should I Use?

If you want:

- `Link 16 story`
  - use `link16-rpr2-integrated`
- `modern main tactical family`
  - use `rpr3-annex-a-normative`
- `big parser / JSON / visualizer stress`
  - use `rpr3-merged-informative-1516-2010`
- `independent broad ontology family`
  - use `space-fom-core`
- `show why extensions need parents`
  - use `link16-standalone-template`

## Recommended Mental Model

Use these statements literally:

- `Link 16` is an extension family, not the main federation root in this repo.
- `RPR 2.0` is the parent tactical family that makes the Link 16 story operational.
- `RPR 3.0` is the main modern tactical family, but it appears in more than one practical packet shape.
- `Space FOM` is separate from RPR and should be thought of as its own family.
- `Pitch` support means `micro-2` parity/credence rows first, not unlimited topology/runtime coverage.
- `2010` versus `2025` is a repo exercise lane as much as a source-file label.

## Read Next

- [fom_siso_quirks.md](fom_siso_quirks.md)
- [fom_siso_showcase.md](fom_siso_showcase.md)
- [fom_siso_runtime_showcase.md](fom_siso_runtime_showcase.md)
- [fom_siso_pitch_micro_parity.md](fom_siso_pitch_micro_parity.md)
- [fom_validate.md](fom_validate.md)
- [rpr_type_normalization_notes.md](rpr_type_normalization_notes.md)
