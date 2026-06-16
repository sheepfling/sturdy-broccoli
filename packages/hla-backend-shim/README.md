# hla-backend-shim

`hla-backend-shim` provides a deliberately small, spec-shaped RTI backend for
the IEEE 1516.1-2025 Python API package.

It is not a 2010 backend and it is not a vendor adapter. It exists so the
version-neutral `hla.rti` factory can create a real `hla.rti1516_2025`
ambassador object while 2025 vendor integrations are developed.
