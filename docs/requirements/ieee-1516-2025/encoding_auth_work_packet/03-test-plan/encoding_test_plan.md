# Encoding test plan

## P0: Contract tests

Purpose: lock the extension boundary before implementation expands.

Tests:

```text
test_factory_returns_matching_encoding_context
test_encoding_context_exposes_registry_repository_and_capabilities
test_registry_lookup_is_deterministic
test_registry_rejects_unknown_encoding_name
```

Pass criteria:

```text
Runtime factory returns one EncodingContext per selected edition/provider/transport.
Capabilities list edition, provider, built-ins, provider extensions, and unsupported names.
```

## P1: FOM type resolution

Purpose: parse OMT/FOM data type metadata into a stable internal graph.

Tests:

```text
test_fom_type_repository_resolves_basic_simple_enum_reference_array_record_variant
test_simple_data_delegates_to_representation
test_enumerated_data_maps_names_to_values
test_reference_data_delegates_to_representation
test_fom_type_repository_rejects_unknown_reference
test_fom_type_repository_rejects_type_cycles
```

Pass criteria:

```text
DataTypeSpec graph is deterministic and independent of XML library node ordering.
Fixed record field order equals FOM order.
Variant alternatives include named alternatives and HLAother fallback when declared.
```

## P2: Primitive codecs

Purpose: prove deterministic bytes for primitives where layout is unambiguous.

Tests:

```text
test_integer16be_known_bytes
test_integer16le_known_bytes
test_integer32be_known_bytes
test_integer32le_known_bytes
test_integer64be_known_bytes
test_integer64le_known_bytes
test_unsigned_range_validation
test_float32be_known_bytes
test_float64be_known_bytes
test_octet_and_octet_pair_round_trip
test_opaque_data_preserves_bytes
test_ascii_string_round_trip
test_unicode_string_round_trip
```

Pass criteria:

```text
Integer and float known vectors match expected hex.
String codecs round-trip and reject invalid Python/native values.
Opaque data returns exactly the bytes supplied.
```

Note: string and composite golden bytes should be compared against provider oracle before permanently freezing portable expected bytes.

## P3: Composite codecs

Purpose: verify FOM-driven composition.

Tests:

```text
test_fixed_record_field_order_is_preserved
test_fixed_record_rejects_missing_field
test_fixed_record_rejects_unexpected_field
test_fixed_array_round_trip
test_fixed_array_rejects_wrong_length
test_variable_array_round_trip
test_nested_record_round_trip
test_variant_record_uses_discriminant
test_variant_record_rejects_unknown_discriminant
test_variant_record_hlaother_fallback
test_extendable_variant_record_is_capability_gated
```

Pass criteria:

```text
Composite encoders use DataTypeSpec, not ad hoc dictionaries.
Decode returns value plus consumed length.
Strict decode rejects trailing bytes.
```

## P4: Provider oracle tests

Purpose: compare HLA-X bytes to an actual RTI EncoderFactory when configured.

Tests:

```text
test_java_2010_encoder_factory_primitive_oracle_when_available
test_java_2025_encoder_factory_primitive_oracle_when_available
test_java_2025_encoder_factory_composite_oracle_when_available
test_cpp_2025_encoder_oracle_when_available
```

Pass criteria:

```text
Oracle tests are skipped with a clear reason when provider runtime is unavailable.
When available, primitive and selected composite bytes match the provider output.
```

## P5: Negative and fuzz-like tests

Purpose: prevent silent corrupt decode.

Tests:

```text
test_decode_rejects_truncated_bytes
test_decode_rejects_extra_bytes_when_strict
test_decode_allows_extra_bytes_when_non_strict_and_reports_consumed_length
test_encode_rejects_wrong_python_type
test_provider_registers_custom_codec_without_overriding_builtin
test_provider_override_builtin_requires_explicit_allow_override
```

Pass criteria:

```text
No malformed bytes produce a silently accepted wrong value in strict mode.
Error messages include type name and offset but not raw giant payloads.
```

## P6: Integration tests

Purpose: prove encoding is usable at HLA service boundaries.

Tests:

```text
test_update_attribute_values_uses_encoding_context
test_reflect_attribute_values_decodes_with_encoding_context
test_send_interaction_encodes_parameters
test_receive_interaction_decodes_parameters
test_bad_codec_fails_before_update_attribute_values
```

Pass criteria:

```text
The RTI provider never needs to know FOM type details beyond attribute/parameter handles and byte payloads.
```
