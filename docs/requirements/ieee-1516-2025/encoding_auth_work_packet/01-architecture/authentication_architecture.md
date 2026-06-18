# Authentication architecture

## Architectural position

Authentication should be a thin factory-paired context. It should not become an RTI-sized backend and it should not modify ambassador service semantics.

```text
HlaRuntimeFactory
  -> create_authentication_context(config)
  -> create_rti_ambassador(auth_context=...)
```

Authentication has two different roles that must not be blurred:

1. **Client connection credentials**: what a federate supplies when connecting to an RTI.
2. **Authorizer behavior**: what an RTI-hosted or proxy-hosted environment uses to decide whether a credential may connect, create/destroy a federation, or join a federation.

The workspace should always implement the client-side credential surface. It should implement authorizer behavior only for fake/in-process/proxy RTI modes that host authorization decisions.

## Target components

```text
AuthenticationContext
  edition: HlaEdition
  provider: str
  transport: str
  credential_provider: CredentialProvider
  connection_adapter: ConnectionAuthAdapter
  authorizer_provider: AuthorizerProvider | None
  capabilities: AuthCapabilityReport

CredentialProvider
  credential_type: str
  get_credentials() -> CredentialEnvelope
  redact() -> RedactedCredentialSummary

CredentialEnvelope
  type: str
  data: bytes
  metadata: dict[str, str]

ConnectionAuthAdapter
  apply_connect(rti_ambassador, federate_ambassador, callback_model, configuration, credentials)
  supports_standard_credentials: bool
  supports_transport_metadata: bool

AuthorizerProvider
  authorize_rti_operation(credentials) -> AuthorizationDecision
  authorize_federation_operation(credentials, federation_name) -> AuthorizationDecision
  authorize_federate_operation(credentials, federation_name, federate_name, federate_type) -> AuthorizationDecision
```

## Edition capability model

```text
1516e-2010
  standard credential-connect support: false
  standard authorizer support: false
  supported auth mode: NoAuth
  adapter-specific auth mode: allowed, provider-gated

1516-2025
  standard credential-connect support: true
  standard credential envelope: type + bytes
  standard credential types: HLAnoCredentials, HLAplainTextPassword
  custom credential types: allowed when provider/authorizer supports them
  authorizer provider: available only for RTI-hosted/proxy modes
```

## Built-in auth providers

```text
NoAuthProvider
  2010: maps to normal connect/local settings path.
  2025: maps to HLAnoCredentials when standard credentials are requested; otherwise normal connect is allowed.

PlainTextPasswordProvider
  2025 only unless a provider adapter explicitly supports it.
  Produces type HLAplainTextPassword and encoded bytes.
  Never logs the raw password.

TokenCredentialProvider
  Provider extension.
  Produces a custom credential type or transport metadata depending on adapter.

MutualTlsProvider
  Transport extension.
  Produces TLS material references/policy, not HLA Credentials bytes unless the provider also requires typed credentials.

FakeAuthProvider
  Test-only.
  Produces deterministic accept/reject decisions.
```

## Connection flow

```text
factory = HlaRuntimeFactory.select(edition='1516-2025', provider='fedpro')
auth_context = factory.create_authentication_context(auth_config)
rti = factory.create_rti_ambassador()

credentials = auth_context.credential_provider.get_credentials()
auth_context.connection_adapter.apply_connect(
    rti_ambassador=rti,
    federate_ambassador=fedamb,
    callback_model=callback_model,
    configuration=rti_configuration,
    credentials=credentials,
)
```

The call above is the only place client authentication should touch the RTI ambassador.

## Authorization decision model

```text
AuthorizationDecision
  code: AUTHORIZED | UNAUTHORIZED | INVALID_CREDENTIALS | AUTHORIZATION_ERROR
  message: str
```

Map failures carefully:

```text
invalid structure, unknown credential type, missing secret -> INVALID_CREDENTIALS
known principal without permission -> UNAUTHORIZED
I/O, provider crash, policy exception -> AUTHORIZATION_ERROR
transport cannot connect -> CONNECTION_FAILED/transport-specific error
```

## Security requirements

1. No raw secrets in `repr`, logs, pytest failure messages, or evidence JSON.
2. Credential bytes may appear only in memory and in test fixtures explicitly marked safe.
3. Capability reports include credential type names, not secret values.
4. A provider that does not support credential-connect must reject credential config during factory assembly, not after federation join begins.
5. The auth context must not add methods or behavior to the RTI ambassador. It only selects the correct connect path and credentials.

## Evidence emitted by implementation

```text
build/hla-evidence/auth_capabilities.json
build/hla-evidence/auth_matrix.json
build/hla-evidence/auth_negative_report.json
build/hla-evidence/secret_redaction_report.json
```
