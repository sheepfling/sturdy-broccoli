# Runtime Observer Event Schema

The generic federation subscriber exposes a stable normalized event contract for tools that want to consume live HLA activity without scraping browser-specific UI structure.

- Checked-in schema file: [runtime_observer_event_schema.json](runtime_observer_event_schema.json)
- Live endpoint: `/api/schema`
- Current version: `runtime-observer-event-schema-v1`

The normalized event stream promotes all provider traffic into a small set of categories:

- `scenario.phase`
- `scenario.operation`
- `object.discovered`
- `object.updated`
- `interaction.received`
- `event.raw`

Identity rules:

- Object inspectors use `object_key` as the stable row identity.
- When available, `object_handle_text` is preferred over `object_name`.
- Interaction rows use `interaction_key` plus `interaction_class`.
- `family` is derived generically from the observed class or carried through when the source already knows it.

This contract is intended for subscriber tools, dashboards, and downstream automation. Browser plugin panels remain optional overlays on top of this generic schema.
