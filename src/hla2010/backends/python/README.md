# Python Backend Compatibility Layout

The pure-Python RTI backend implementation has moved to the split plugin
package `hla2010_rti_python`.

This directory is now a compatibility facade for existing imports such as
`hla2010.backends.python` and `hla2010.backends.python.state`.

Canonical implementation modules now live under:

- `packages/hla2010-rti-python/src/hla2010_rti_python/state.py`
- `packages/hla2010-rti-python/src/hla2010_rti_python/engine.py`
- `packages/hla2010-rti-python/src/hla2010_rti_python/backend.py`
- `packages/hla2010-rti-python/src/hla2010_rti_python/factory.py`

New code should prefer imports from `hla2010_rti_python`.
