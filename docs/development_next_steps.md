# Development next steps

Good next slices for the fresh repository:

1. split the large pure-Python RTI backend into federation-management, declaration-management, object-management, ownership, time, DDM, and MOM modules;
2. wire CI to run the Python tests and optional JPype/Py4J bridge smoke tests when dependencies are present;
3. regenerate conformance/verification outputs from source into build artifacts rather than storing them in the repo seed;
4. extend the new `pitch-jpype` and `pitch-py4j` runtime profiles from version discovery to create/join/resign interoperability checks;
5. add a native CERTI Python binding or transport adapter so `CERTI` can participate in the same backend-neutral ambassador factory instead of only daemon launch scripts;
6. tighten remaining negative-path exception semantics service by service.
