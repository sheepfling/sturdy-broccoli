# HLA-X Encoding and Authentication Work Packet

This packet turns the encoding/authentication discussion into an executable implementation and test plan for an agent.

The intended architecture is:

```text
HlaRuntimeFactory
  -> RtiProvider / RTI ambassador
  -> EncodingContext / FOM type resolver / codec registry
  -> AuthenticationContext / credential provider / connection policy
```

Encoding is a cross-edition core surface. Authentication is edition/provider/transport capability gated. The agent should not implement authentication as a peer RTI backend; it should implement a thin auth context that the runtime factory composes with the selected RTI provider.

## Immediate completion target

The agent should stop only when these gates are satisfied:

1. `EncodingContext` exists and is returned from the same runtime factory selection as the RTI provider.
2. The encoding registry reports built-in codec capabilities for 1516e-2010 and 1516-2025 profiles.
3. The FOM type resolver handles simple, enumerated, array, fixed record, variant record, and reference data types.
4. Primitive codec tests pass for deterministic BE/LE integer and float vectors.
5. Composite codec tests pass for fixed record, fixed array, variable array, variant record, and extendable variant record where supported.
6. `AuthenticationContext` exists and is returned from the same runtime factory selection as the RTI provider.
7. 1516e-2010 profiles explicitly report no standard credential-connect support unless a provider adapter supplies it.
8. 1516-2025 profiles support standard credential envelopes: `HLAnoCredentials`, `HLAplainTextPassword`, and custom typed bytes.
9. Invalid credentials fail before federation creation or join.
10. Evidence files are emitted in `build/hla-evidence/`.

## Packet layout

```text
00-source-anchors/     Standards/API surfaces used to ground the plan
01-architecture/       Target design for encoding, auth, and factory pairing
02-requirements/       Requirements and traceability tables
03-test-plan/          Detailed test plan and certification gates
04-test-data/          YAML vectors for codec and auth testing
05-example-foms/       Small FOM type inputs for resolver tests
06-pytest-skeleton/    Contract-style pytest skeletons
07-agent-tasks/        Agent backlog, sequencing, and definition of done
08-evidence-templates/ JSON schema templates for emitted evidence
09-standards-subset/ Small XSD subset needed for local FOM/parser validation
```

## Agent instruction

Implement the smallest design that makes the traceability matrix true. Do not add a general-purpose plugin framework beyond these extension points:

```text
EncodingRegistry
CodecProvider
FomTypeRepository
CredentialProvider
ConnectionAuthAdapter
AuthorizerProvider, only when the selected RTI mode hosts or simulates authorizer behavior
```

Keep RTI service semantics out of auth and encoding. Encoding returns bytes/values. Auth returns credentials/connection policy/authorization decisions. The RTI provider performs HLA service calls.
