# hla2010-fom-target-radar Migration

Canonical Target/Radar ownership now lives under:

- `src/hla2010_fom_target_radar/resources/foms/TargetRadarFOMmodule.xml`
- `src/hla2010_fom_target_radar/scenarios/target_radar.py`
- `src/hla2010_fom_target_radar/scenarios/target_radar_cli.py`
- `src/hla2010_fom_target_radar/testing/target_radar_backend_matrix.py`
- `src/hla2010_fom_target_radar/testing/target_radar_proof.py`
- `src/hla2010_fom_target_radar/testing/two_federate_target_radar.py`
- `src/hla2010_fom_target_radar/testing/two_federate_target_radar_artifacts.py`
- `src/hla2010_fom_target_radar/testing/two_federate_suite_profiles.py`

The root `src/hla2010/scenarios/` modules remain as compatibility facades for
older imports. The root `src/hla2010/resources/foms/TargetRadarFOMmodule.xml`
path is retained as a compatibility symlink for source-checkout workflows while
callers move toward package-owned resource resolution helpers.
