# Agent backlog

## Epic 1: Encoding context and registry

Deliverables:

```text
EncodingContext
EncodingRegistry
Codec interface
CodecCapabilityReport
built-in codec registration for 2010 and 2025 profiles
```

Acceptance:

```text
test_factory_returns_matching_encoding_context
test_registry_resolves_required_builtins
test_registry_rejects_unknown_encoding_name
```

## Epic 2: FOM type repository

Deliverables:

```text
FomTypeRepository
DataTypeSpec model family
OMT/FOM XML parser for datatype sections
attribute/parameter type lookup helpers
```

Acceptance:

```text
test_fom_type_repository_resolves_all_smoke_types
test_fixed_record_field_order_is_preserved
test_variant_record_uses_discriminant
```

## Epic 3: Primitive codecs

Deliverables:

```text
integer BE/LE codecs
unsigned integer BE/LE codecs
float BE/LE codecs
ASCII/unicode round-trip codecs
opaque data codec
strict DecodeResult with consumed length
```

Acceptance:

```text
test_primitive_known_bytes
test_primitive_vectors_round_trip
test_decode_rejects_truncated_bytes
```

## Epic 4: Composite codecs

Deliverables:

```text
fixed array codec
variable array codec
fixed record codec
variant record codec
extendable variant record capability gate
provider-oracle test hooks
```

Acceptance:

```text
fixed record, fixed array, variable array, nested record, variant, and negative composite tests pass
```

## Epic 5: Authentication context

Deliverables:

```text
AuthenticationContext
CredentialEnvelope
CredentialProvider interface
NoAuthProvider
PlainTextPasswordProvider
TokenCredentialProvider extension point
MutualTlsProvider extension point
redaction model
```

Acceptance:

```text
test_factory_returns_matching_authentication_context
test_no_auth_provider_returns_hla_no_credentials_for_2025
test_2010_profile_rejects_standard_credentials
test_secret_redaction_in_repr_logs_and_evidence
```

## Epic 6: Connection adapter and authorizer gates

Deliverables:

```text
ConnectionAuthAdapter
2025 credentials connect adapter
2010 no-standard-credentials adapter
FedPro credential message adapter
FakeAuthorizerProvider for tests
failure code mapping
```

Acceptance:

```text
test_runtime_context_contains_rti_encoding_and_auth
test_incompatible_auth_fails_at_factory
test_bad_auth_fails_before_federation_created
```

## Epic 7: Evidence and CI

Deliverables:

```text
build/hla-evidence/encoding_capabilities.json
build/hla-evidence/fom_type_resolution.json
build/hla-evidence/codec_round_trip_report.json
build/hla-evidence/codec_negative_report.json
build/hla-evidence/auth_capabilities.json
build/hla-evidence/auth_matrix.json
build/hla-evidence/auth_negative_report.json
build/hla-evidence/secret_redaction_report.json
build/hla-evidence/runtime_matrix.json
```

Acceptance:

```text
Evidence validates against schemas in 08-evidence-templates.
Traceability matrix has no missing requirement/test/evidence links.
```

## Definition of done

A requirement is done only when:

```text
implementation exists
positive test exists
negative test exists when meaningful
evidence row exists
traceability row links requirement -> test -> evidence
factory compatibility failure path is tested when edition/provider mismatch is possible
```
