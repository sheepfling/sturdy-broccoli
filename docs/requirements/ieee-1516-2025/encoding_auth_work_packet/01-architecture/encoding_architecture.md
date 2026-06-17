# Encoding architecture

## Architectural position

Encoding is a factory-paired extension point, not an RTI backend. The runtime factory that selects `edition + provider + transport` must also provide an `EncodingContext` so callers cannot accidentally combine a 2025 RTI stack with a 2010 or provider-incompatible encoding stack.

```text
HlaRuntimeFactory
  -> create_rti_ambassador(...)
  -> create_encoding_context(fom_modules | type_repository | None)
  -> capability_report()
```

The encoding surface should be stable even when RTI providers differ. Provider-specific behavior belongs in registered codec providers and capability flags.

## Target components

```text
EncodingContext
  edition: HlaEdition
  provider: str
  registry: EncodingRegistry
  type_repository: FomTypeRepository | None
  capabilities: EncodingCapabilityReport

EncodingRegistry
  get(name: str) -> Codec
  register(provider: CodecProvider) -> None
  has(name: str) -> bool
  list_capabilities() -> list[CodecCapability]

Codec
  name: str
  encode(value: object, spec: DataTypeSpec | None = None) -> bytes
  decode(data: bytes, spec: DataTypeSpec | None = None, *, strict: bool = True) -> DecodeResult
  encoded_length(value: object, spec: DataTypeSpec | None = None) -> int | None
  octet_boundary(spec: DataTypeSpec | None = None) -> int

FomTypeRepository
  resolve(type_name: str) -> DataTypeSpec
  resolve_attribute(object_class: str, attribute: str) -> DataTypeSpec
  resolve_parameter(interaction_class: str, parameter: str) -> DataTypeSpec
```

## Data type model

Represent FOM data types explicitly instead of passing XML nodes through the encoder.

```text
DataTypeSpec
  BasicDataSpec
    name
    size_bits
    endian
    encoding

  SimpleDataSpec
    name
    representation
    units/resolution/accuracy/semantics

  EnumeratedDataSpec
    name
    representation
    enumerators: name -> literal value

  ReferenceDataSpec
    name
    representation
    reference_class
    referenced_attribute

  ArrayDataSpec
    name
    element_type
    cardinality
    encoding: HLAfixedArray | HLAvariableArray | custom

  FixedRecordDataSpec
    name
    encoding: HLAfixedRecord | custom
    fields: ordered list[(name, type)]

  VariantRecordDataSpec
    name
    discriminant_name
    discriminant_type
    alternatives
    encoding: HLAvariantRecord | HLAextendableVariantRecord | custom
```

## Built-in codec set

Phase 1 must include registry entries for these names:

```text
HLAASCIIchar
HLAASCIIstring
HLAboolean
HLAbyte
HLAfloat32BE
HLAfloat32LE
HLAfloat64BE
HLAfloat64LE
HLAinteger16BE
HLAinteger16LE
HLAinteger32BE
HLAinteger32LE
HLAinteger64BE
HLAinteger64LE
HLAunsignedInteger16BE
HLAunsignedInteger16LE
HLAunsignedInteger32BE
HLAunsignedInteger32LE
HLAunsignedInteger64BE
HLAunsignedInteger64LE
HLAoctet
HLAoctetPairBE
HLAoctetPairLE
HLAopaqueData
HLAunicodeChar
HLAunicodeString
HLAfixedArray
HLAvariableArray
HLAfixedRecord
HLAvariantRecord
HLAextendableVariantRecord
```

`HLAextendableVariantRecord` should be feature-gated. It appears in the 2025 encoding factory/API artifacts and OMT union, but the agent should only mark it supported for editions/providers that can actually encode it.

## Codec selection rules

1. For simple data, resolve `representation`; then delegate to the representation codec.
2. For enumerated data, encode the enumerator's numeric value using the representation codec.
3. For reference data, delegate to `representation`; do not chase object instances during encoding.
4. For fixed record data, preserve the FOM field order exactly.
5. For fixed arrays, enforce exact cardinality.
6. For variable arrays, accept dynamic cardinality and encode count/contents according to the selected codec implementation.
7. For variant records, encode/decode the discriminant first according to the selected HLA codec behavior; select the alternative using enumerator mapping and `HLAother` fallback when present.
8. For custom encoding names, require a registered codec provider. Unknown custom names are not silently treated as opaque bytes.

## Compatibility strategy

Use two validation modes:

```text
portable
  Test primitive deterministic bytes and round trips from our codecs.

provider_oracle
  When a Java/C++/vendor EncoderFactory is available, compare composite encodings against that provider's encoded bytes.
```

The portable suite must not over-specify composite layout until the HLA-X encoder intentionally owns that layout. The provider oracle suite is allowed to be stricter.

## Failure policy

Encoding failures should be local and precise:

```text
UnknownEncodingName
UnsupportedEncodingForEdition
FomTypeNotFound
FomTypeCycle
InvalidCardinality
MissingRecordField
UnexpectedRecordField
UnknownVariantDiscriminant
MalformedEncodedData
TrailingEncodedData
TypeMismatch
CodecProviderConflict
```

## Evidence emitted by implementation

```text
build/hla-evidence/encoding_capabilities.json
build/hla-evidence/fom_type_resolution.json
build/hla-evidence/codec_round_trip_report.json
build/hla-evidence/codec_negative_report.json
build/hla-evidence/provider_oracle_report.json
```
