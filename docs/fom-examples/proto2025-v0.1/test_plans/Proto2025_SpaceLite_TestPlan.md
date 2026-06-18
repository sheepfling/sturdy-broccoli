# Proto2025 SpaceLite v0.1 Test Plan

| ID | Test | Federates | Procedure | Pass criteria | Evidence |
|---|---|---|---|---|---|
| SL-001 | Mode initialization | Master, Pacing, ReferenceFrame, VehicleDynamics | Join required federates and transition `Uninitialized -> Initializing -> Run`. | Each federate acknowledges with `ModeTransitionComplete`; `ExecutionConfiguration.Mode` is correct. | Mode trace |
| SL-002 | Reference-frame tree | ReferenceFrameFederate, ViewerFederate | Publish root frame and two child frames. | Exactly one root; every non-root parent exists; no cycles detected by viewer. | Frame graph report |
| SL-003 | Entity state update | VehicleDynamics, Viewer | Publish one `DynamicalEntity` at each time step. | Entity state timestamps are monotonic and position changes according to profile. | Entity state log |
| SL-004 | Sensor observation | Sensor, VehicleDynamics, Command | Sensor subscribes to entity state and publishes `SensorTrack`. | Track target ID matches entity; range and bearing are within tolerance. | Track validation report |
| SL-005 | Attach/detach | Command, VehicleDynamics, Viewer | Command two physical interfaces to attach and detach. | Both interfaces report reciprocal attached state, then free state. | Interface state log |
| SL-006 | Freeze/resume | Master, Pacing, VehicleDynamics, Sensor | Request `Freeze`; hold; request `Run`. | No entity dynamic updates during freeze; updates resume with monotonic logical time. | Freeze interval report |
| SL-007 | Pacing profiles | Pacing, VehicleDynamics, Viewer | Run 1x, 2x, and as-fast-as-possible profiles. | Logical-time/wall-clock ratio is within profile tolerance for paced modes. | Pacing metrics |
| SL-008 | Late-joining viewer | Viewer joins after run begins. | Start viewer after several state updates. | Viewer discovers frames/entities and receives current state refresh. | Late-join viewer log |

## Minimum v0.1 scenario

- Root frame: `SolarSystemBarycentric`.
- Child frame: `EarthMJ2000Eq`.
- Entity: `SAT-001`, type `Satellite`, circular two-dimensional toy trajectory.
- Sensor: `GroundSensor-001`, single range/bearing track.
- Time step: 100 ms logical time unless test overrides it.
