# Certification gates

The agent should treat these as acceptance gates.

## Encoding gates

```text
CERT-ENC-001 Registry discovery
CERT-ENC-002 FOM type graph resolution
CERT-ENC-003 Primitive deterministic bytes
CERT-ENC-004 Primitive round trip
CERT-ENC-005 Composite round trip
CERT-ENC-006 Variant discriminant behavior
CERT-ENC-007 Negative decode validation
CERT-ENC-008 Provider custom codec registration
CERT-ENC-009 Evidence emission
```

## Authentication gates

```text
CERT-AUTH-001 Edition capability matrix
CERT-AUTH-002 NoAuth path
CERT-AUTH-003 2025 typed credential path
CERT-AUTH-004 Custom credential support gating
CERT-AUTH-005 Bad auth fails before federation lifecycle operations
CERT-AUTH-006 Authorizer decisions for fake/proxy hosted mode
CERT-AUTH-007 Secret redaction
CERT-AUTH-008 Evidence emission
```

## Factory pairing gates

```text
CERT-FACT-001 Runtime context assembly
CERT-FACT-002 Incompatible edition/provider/auth combos fail fast
CERT-FACT-003 Incompatible FOM encoding/provider combos fail fast
CERT-FACT-004 Runtime matrix evidence
```
