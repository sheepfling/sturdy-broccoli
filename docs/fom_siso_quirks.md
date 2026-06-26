# FOM SISO Quirks

Use this page when you are trying to understand why a SISO FOM family loads
the way it does in this repo.

If you are still confused about how Link 16, RPR, and Space relate before you
even get to parser quirks, start with
[`fom_siso_family_map.md`](fom_siso_family_map.md).

This is the shortest explanation of:

- which XMLs are meant to stand alone
- which XMLs are really extensions or add-ons
- which families only make sense as an ordered module set
- which quirks are parser/runtime pressure versus ordinary operator mistakes

## First Mental Model

There are three load shapes in the repo inventory:

- `standalone`
  - one XML is supposed to be the whole load root
  - examples: repo demo FOM, Target/Radar, standard MIM
- `base-plus-extension`
  - one base module is the main root and the others are add-on deltas
  - the repo `Proto2025_Base.xml` is the base
  - the message/time/space-lite variants are extensions, not independent roots
- `ordered-family`
  - the family is the unit, not any one XML
  - order matters because later modules assume earlier datatype, dimension, or
    class declarations already exist

If you are wondering which XML is the main one and which are the add-ons, that
question maps directly to `load_mode`.

## Family-by-Family Quirks

### Link 16

- family: `siso-link-16`
- load shape in practice: not a good standalone federation root
- learning point:
  - Link 16 is most useful here as a tactical comms add-on inside the broader
    RPR 2.0 integrated family
- operator takeaway:
  - treat standalone Link 16 as a template/stressor
  - treat `link16-rpr2-integrated` as the main executable story

### RPR 2.0

- family: `siso-rpr-2.0`
- load mode: `ordered-family`
- main shape:
  - foundation and enumerations come first
  - base and the domain modules layer on top
  - Link 16 and Link 11 are optional tactical additions near the end
- repo quirk:
  - default-load resolution de-duplicates duplicate members by basename so the
    same module is not loaded twice when the corpus layout repeats it
- operator takeaway:
  - do not pick one RPR 2.0 XML at random and expect a meaningful load

### RPR 3.0

- family: `siso-rpr-3.0`
- load mode: `ordered-family`
- main shape:
  - Annex A normative modules are the main family
  - large merged or informative packets are useful stressors, but they are not
    the cleanest default learning surface
- repo quirk:
  - the default load set intentionally prefers the normative Annex A path and
    excludes the informative merged `RPR_FOM_v3.0_1516-*` packets from the
    default load family
- operator takeaway:
  - use the normative family to learn the ontology
  - use the merged packets to stress parser, round-trip, and UI surfaces

### Space FOM

- family: `siso-space-fom`
- load mode: `ordered-family`
- main shape:
  - datatypes
  - environment
  - switches
  - management
  - entity
- learning point:
  - this family is broader and more hierarchical than the repo demo FOMs
  - many useful concepts are declared in one module and consumed later in the
    ordered set
- current runtime quirk:
  - the Space FOM family is a good example where family load and later runtime
    lookup success are not the same claim

### U-FOM

- family: `siso-u-fom`
- load mode: `ordered-family`
- main shape:
  - enumerations and base pieces come first
  - merged or convenience forms are not the cleanest learning surface
- operator takeaway:
  - treat it as another family where module order is part of the definition

### OMT and Standard/MIM Support Families

- families:
  - `siso-omt`
  - `siso-standard-mim`
  - `standard-mim`
- learning point:
  - these are often support/reference surfaces rather than the first place to
    look for runtime scenario richness
- operator takeaway:
  - they are good for schema, tooling, and support-boundary checks
  - they are usually not the main demo-federation story

## Current High-Value Learning Families

The default high-value SISO scope is intentionally narrow:

- `siso-rpr-2.0`
- `siso-rpr-3.0`
- `siso-link-16`
- `siso-space-fom`
- `siso-standard-mim`
- `siso-u-fom`

That is the repo saying:

- these are the families we think teach the most
- these are also the ones worth validating, round-tripping, and showcasing
  first

## How To Explore

- inventory and family metadata:
  - [fom-examples/fom_inventory.md](fom-examples/fom_inventory.md)
- validator:
  - [fom_validate.md](fom_validate.md)
- showcase:
  - [fom_siso_showcase.md](fom_siso_showcase.md)
- workbench:
  - [fom_workbench.md](fom_workbench.md)
- standards-backed reading map:
  - [fom_reading_map.md](fom_reading_map.md)

For Pitch-specific runtime-backed comparison on the same example packets, use:

- `./tools/pitch fom-smoke`
- `./tools/pitch fom-smoke-compare`
