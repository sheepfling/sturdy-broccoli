# Authentication test plan

## P0: Contract tests

Purpose: define a thin auth surface paired with the runtime factory.

Tests:

```text
test_factory_returns_matching_authentication_context
test_authentication_context_exposes_credential_provider_connection_adapter_and_capabilities
test_auth_context_does_not_modify_rti_ambassador_methods
```

Pass criteria:

```text
Auth is represented by AuthenticationContext.
RTI ambassador service API remains provider-owned.
```

## P1: Edition capability tests

Purpose: avoid accidental 2025 auth assumptions in 2010 mode.

Tests:

```text
test_2010_profile_reports_no_standard_credentials
test_2010_profile_allows_no_auth
test_2010_profile_rejects_plain_text_password_without_provider_adapter
test_2025_profile_reports_standard_credentials
test_2025_credentials_are_type_and_bytes
```

Pass criteria:

```text
2010 standard profile fails fast on standard credential auth config.
2025 profile creates HLA-style credential envelopes.
```

## P2: Built-in credential provider tests

Purpose: prove credential bytes/types are constructed and redacted correctly.

Tests:

```text
test_no_auth_provider_returns_hla_no_credentials_for_2025_standard_mode
test_no_auth_provider_uses_plain_connect_for_2010_mode
test_plain_text_password_provider_returns_typed_credentials
test_plain_text_password_rejects_empty_password
test_custom_token_provider_returns_declared_type_or_metadata
test_mtls_auth_requires_cert_and_key
test_secret_redaction_in_repr_logs_and_evidence
```

Pass criteria:

```text
No provider prints or persists raw secret material.
Credential type support is visible in capability report.
```

## P3: Connection adapter tests

Purpose: prove credentials are applied at connect time only.

Tests:

```text
test_2025_adapter_uses_connect_with_credentials
test_2025_adapter_uses_connect_with_configuration_and_credentials_when_configuration_present
test_2010_adapter_rejects_standard_credentials
test_grpc_adapter_maps_credentials_to_fedpro_message_shape
test_transport_metadata_auth_does_not_create_hla_credentials_when_not_required
```

Pass criteria:

```text
Credentials are available before connection.
Auth failure cannot occur after federation join has started.
```

## P4: Authorizer tests

Purpose: verify RTI-hosted/proxy/fake authorization semantics only where applicable.

Tests:

```text
test_fake_authorizer_authorizes_rti_operation
test_fake_authorizer_rejects_invalid_credentials
test_fake_authorizer_rejects_unauthorized_federation
test_fake_authorizer_rejects_unauthorized_federate
test_authorizer_failure_codes_are_mapped
test_non_hosted_provider_has_no_authorizer_provider
```

Pass criteria:

```text
AuthorizationDecision codes distinguish AUTHORIZED, UNAUTHORIZED, INVALID_CREDENTIALS, and AUTHORIZATION_ERROR.
```

## P5: Negative and integration tests

Purpose: ensure bad auth fails early and safely.

Tests:

```text
test_bad_auth_fails_before_federation_created
test_bad_auth_fails_before_join_federation
test_unknown_custom_credential_type_rejected
test_provider_required_auth_missing_rejected_at_factory
test_provider_required_tls_missing_files_rejected_at_factory
test_auth_evidence_files_are_emitted
```

Pass criteria:

```text
No failed auth path calls createFederationExecution or joinFederationExecution.
No secret appears in exception text or evidence.
```
