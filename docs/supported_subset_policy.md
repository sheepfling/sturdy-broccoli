# Supported-Subset Policy

This repo now distinguishes between two kinds of compliance claim:

- `broad-spec`: the full IEEE 1516.1-2010 (2010 edition) requirement wording
- `supported-subset`: a narrower requirement row that matches the behavior the
  current Python reference backend actually implements and evidences

That split is intentional. It prevents us from claiming full compliance for
behavior we have not actually modeled.

## Evidence rule

Every promoted row needs a testable proof shape:

- a positive test for the exact supported subset, or
- a negative test that fixes the boundary of what is not claimed

If the repo only proves a narrower implementation than the broad spec text,
keep the broad row partial and record the narrower supported-subset row
separately. Do not use vendor parity language unless the row has a matching
vendor-backed proof anchor.

## Update-rate policy

Policy ID: `logical-time-update-rate-only`

Supported subset:

- explicit update-rate designators
- FOM-declared default update-rate designators
- direct subscriptions
- inherited/superclass subscriptions
- regioned subscriptions
- throttling when there is a logical-time basis
- no accidental suppression of receive-order traffic when there is no
  logical-time basis

Not claimed:

- wall-clock throttling
- unmanaged receive-order throttling policies
- broader vendor-specific update-rate semantics not grounded in logical time

Broad rows that remain partial because of this policy:

- `HLA1516.1-DM-5.1.6-001`
- `HLA1516.1-OM-6.1.12-001`

## Transportation policy

Policy ID: `reliable-best-effort-transport-only`

Supported subset:

- `HLAreliable`
- `HLAbestEffort`
- FOM-declared defaults when they map to those standard transport types
- explicit transport overrides for those standard transport types
- callback/query/report semantics for those overrides
- restore persistence for transport override state

Not claimed:

- arbitrary custom transportation-type semantics beyond the reliable /
  best-effort pair

Broad rows that remain partial because of this policy include:

- `HLA1516.1-OM-6.1.10-001`
- `HLA1516.1-OM-6.23-001`
- `HLA1516.1-OM-6.24-001`
- `HLA1516.1-OM-6.25-001`
- `HLA1516.1-OM-6.26-001`
- `HLA1516.1-OM-6.27-001`
- `HLA1516.1-OM-6.28-001`
- `HLA1516.1-OM-6.29-001`
- `HLA1516.1-OM-6.30-001`

Supported-subset rows under this policy are carried alongside those broad rows
in the requirements matrix and Clause 5/6 packet.

## Delivery batching policy

Policy ID: `unbatched-callback-delivery-only`

Supported subset:

- direct unbatched callback delivery with preserved externally visible
  semantics

Not claimed:

- message combination
- packaging
- passelization

Broad row that remains partial because of this policy:

- `HLA1516.1-OM-6.1.11-001`

## Where this appears

Generated compliance artifacts:

- `analysis/compliance/extracted_requirements_clause5_6.json`
- `analysis/compliance/extracted_requirements_clause5_6.md`
- `analysis/compliance/extracted_requirements_clause7_9.json`
- `analysis/compliance/extracted_requirements_clause7_9.md`
- `analysis/compliance/supported_subset_policy.json`
- `analysis/compliance/supported_subset_policy.md`
- `analysis/compliance/defended_partials_index.json`
- `analysis/compliance/defended_partials_index.md`

The generated artifacts now include:

- `claim_scope`
- `policy_basis`
- `supported_subset_for`

Those fields make the remaining partial rows easier to defend because they show
whether the row is:

- a deliberately broad requirement kept partial by policy, or
- a narrower supported-subset requirement that is actually implemented and
  evidenced
