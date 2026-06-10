# hla2010-fom-target-radar Migration

Canonical Target/Radar ownership now lives under:

- `src/hla2010_fom_target_radar/resources/foms/TargetRadarFOMmodule.xml`
- `src/hla2010_fom_target_radar/scenarios/target_radar.py`
- `src/hla2010_fom_target_radar/scenarios/target_radar_cli.py`
- repo-internal verification helpers now live under
  `src/hla2010_repo_internal/verification/`

The root `src/hla2010/scenarios/` modules remain as compatibility facades for
older imports. The root `src/hla2010/resources/foms/TargetRadarFOMmodule.xml`
path is retained as a compatibility symlink for source-checkout workflows while
callers move toward package-owned resource resolution helpers.
