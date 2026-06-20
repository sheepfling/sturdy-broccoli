# hla-backend-shim docs

The shim backend is the current executable Python runtime lane for
`rti1516_2025`.

It still carries shim responsibilities, but the repo now validates it as more
than a thin adapter: the 2025 verification surface exercises federation
lifecycle, object exchange, ownership, time management, save/restore, callback
normalization, and bounded route/time-window proofs against this backend.

The architectural intent remains explicit. Shim concerns and RTI concerns
should stay separable enough that this lane can either remain the promoted
Python 2025 RTI or later be split into a narrower shim plus a dedicated 2025
backend without losing the shared verification evidence.
