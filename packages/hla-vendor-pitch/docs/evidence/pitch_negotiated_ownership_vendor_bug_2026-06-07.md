# Pitch negotiated ownership vendor bug note

Date: `2026-06-07`

Scope:
- Vendor: `Pitch pRTI Free 5.5.10 build 9905`
- Runtime mode: Docker-backed CRC/FedPro
- Bridges tested:
  - `pitch-jpype`
  - `pitch-py4j`

## Summary

Negotiated ownership is still not promotable against Pitch. The failure is not one single uniform behavior across bridges:
- `pitch-jpype` and `pitch-py4j` diverge on both tested ownership branches
- both show incomplete callback sequences
- `pitch-jpype` additionally shows explicit client-side FedPro session-drop / failed-resume log lines during the problematic runs

## Reproducer commands

```bash
HLA2010_PITCH_CRC_MODE=docker HLA2010_PITCH_DOCKER_BUILD=0 python3 scripts/diagnose_pitch_negotiated_ownership.py pitch-jpype --mode offer --tail-lines 60
HLA2010_PITCH_CRC_MODE=docker HLA2010_PITCH_DOCKER_BUILD=0 python3 scripts/diagnose_pitch_negotiated_ownership.py pitch-jpype --mode release-request --tail-lines 60
HLA2010_PITCH_CRC_MODE=docker HLA2010_PITCH_DOCKER_BUILD=0 python3 scripts/diagnose_pitch_negotiated_ownership.py pitch-py4j --mode offer --tail-lines 60
HLA2010_PITCH_CRC_MODE=docker HLA2010_PITCH_DOCKER_BUILD=0 python3 scripts/diagnose_pitch_negotiated_ownership.py pitch-py4j --mode release-request --tail-lines 60
```

## Expected behavior

Negotiated ownership offer path should progress from offer/request through either a release callback or immediate acquisition callback, then continue consistently to a promotable ownership transfer sequence.

Owned-attribute release-request path should progress through:
- `requestAttributeOwnershipRelease`
- `attributeOwnershipAcquisitionNotification`
- `informAttributeOwnership`

## Observed callback history

Offer path, `pitch-jpype`:
```text
owner callbacks:
1: requestDivestitureConfirmation

acquirer callbacks:
0: discoverObjectInstance
1: requestAttributeOwnershipAssumption
```

Offer path, `pitch-py4j`:
```text
owner callbacks:
<none>

acquirer callbacks:
0: discoverObjectInstance
1: requestAttributeOwnershipAssumption
```

Release-request path, `pitch-jpype`:
```text
owner callbacks:
<none>

acquirer callbacks:
0: discoverObjectInstance
```

Release-request path, `pitch-py4j`:
```text
owner callbacks:
1: requestAttributeOwnershipRelease

acquirer callbacks:
0: discoverObjectInstance
1: attributeOwnershipAcquisitionNotification
```

## Observed FedPro / session evidence

`pitch-jpype --mode offer`
```text
Client Session -4946547292664644858: Session dropped: java.io.EOFException: Could only read 0 of 4 bytes
Client Session -4946547292664644858: Failed to resume: se.pitch.oss.fedpro.common.exceptions.SessionLost: java.io.EOFException: Could only read 0 of 4 bytes
Server Session -4946547292664644858: New session initialized from /172.17.0.1:62802
```

`pitch-jpype --mode release-request`
```text
Client Session -472440421083109370: Session dropped: java.io.EOFException: Could only read 0 of 4 bytes
Client Session -472440421083109370: Failed to resume: se.pitch.oss.fedpro.common.exceptions.SessionLost: java.io.EOFException: Could only read 0 of 4 bytes
Server Session -472440421083109370: New session initialized from /172.17.0.1:56116
```

`pitch-py4j --mode offer`
```text
Connection from /172.17.0.1:59506: Client closed connection: java.io.EOFException: Could only read 0 of 4 bytes
Server Session 1498854728846224973: New session initialized from /172.17.0.1:59518
Server Session 5018336356415234451: New session initialized from /172.17.0.1:59520
```

`pitch-py4j --mode release-request`
```text
Connection from /172.17.0.1:55356: Client closed connection: java.io.EOFException: Could only read 0 of 4 bytes
Server Session -8976395060380369277: New session initialized from /172.17.0.1:61972
Server Session -837493047470418177: New session initialized from /172.17.0.1:61978
```

## Interpretation

The issue is broader than one missing callback:
- the negotiated-offer branch diverges across bridges
- the release-request branch diverges across bridges
- `pitch-jpype` exhibits explicit FedPro client-session drop / failed-resume events during the failing runs
- `pitch-py4j` can progress farther on release-request but still stops before `informAttributeOwnership`

This should be treated as a vendor/runtime interoperability bug until Pitch can complete the ownership callback sequence consistently across both Java bridge routes.
