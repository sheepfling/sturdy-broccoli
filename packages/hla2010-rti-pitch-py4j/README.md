# hla2010-rti-pitch-py4j

Pitch Java RTI adapter through Py4J.

This package owns the `pitch-py4j` backend plugin descriptor and Pitch-specific
runtime wiring. Generic Py4J Java bridge mechanics live in
`hla2010-rti-java-py4j`.

The old `hla2010_rti_pitch_py4j.{runtime,adapter,factory}` and
`hla2010.backends.py4j` modules remain as compatibility facades.
