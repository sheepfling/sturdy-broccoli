# hla2010-spec

Migration scaffold for the pure IEEE 1516.1-2010 Python spec package.

This package should eventually contain:

- `hla2010.spec`
- `hla2010.runtime_api`
- `hla2010.backends.base`
- `hla2010.rti` registry and entry point discovery
- shared `handles`, `types`, `enums`, `time`, `exceptions`, FOM/MOM helpers

It must not depend on concrete RTI backends, Java bridge runtimes, CERTI/Pitch
runtime discovery, examples, or repo-internal testing helpers.
