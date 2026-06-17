# Factory pairing plan

## Rule

The RTI, encoding, and authentication contexts must come from the same selected runtime factory.

```text
selected = HlaRuntimeFactory.select(
    edition='1516-2025',
    provider='fedpro',
    transport='grpc',
)

runtime = selected.create_runtime_context(config)

runtime.rti_ambassador
runtime.encoding_context
runtime.authentication_context
runtime.capabilities
```

Do not allow users to manually mix unrelated contexts unless they opt into an explicit advanced/unsafe path.

## Runtime context

```text
HlaRuntimeContext
  edition
  provider
  transport
  rti_ambassador
  encoding_context
  authentication_context
  capability_report
```

## Compatibility gates

Assembly fails before any RTI connection attempt when:

```text
edition is unsupported by provider
provider requires auth but auth config is absent
standard credential auth is requested on a 2010 profile
custom credential type lacks a provider adapter or authorizer
FOM names an encoding that no codec provider can resolve
FOM uses HLAextendableVariantRecord on a profile that lacks support
codec provider attempts to override a built-in without explicit allow_override
transport requires TLS material that is missing
```

## Why pairing matters

Encoding is clearly factory-associated in the API artifacts through `RtiFactory.getEncoderFactory()` in both 2010 and 2025 Java APIs. Authentication is connection-associated in 2025 through credential connect overloads and FedPro connect messages. Pairing these at the runtime-factory level prevents mismatches like:

```text
1516-2025 RTI + 1516e-2010 auth behavior
FedPro transport + in-process credential injection
provider-specific FOM encoding + generic codec registry
custom authorizer credential type + client provider that emits a different type
```
