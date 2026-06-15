# Requirements Schema Contract

## Master requirements CSV

Expected canonical file: `hla_1516_requirements_master_v1_0.csv`

Required columns:

- requirement_id
- standard
- clause
- source_title
- capability
- feature
- requirement_text
- normative_keyword
- implementation_area
- verification_method
- test_id
- status
- priority
- source_note
- requirement_type
- parent_requirement_id
- source_detail
- service_name
- service_direction
- transport_scope
- mom_observable
- verification_notes

Minimum validation rules:

- `requirement_id` must be nonempty and unique.
- `standard` should be one of IEEE 1516-2010 (2010 edition), IEEE 1516.1-2010 (2010 edition), IEEE 1516.2-2010 (2010 edition), or a clearly documented artifact/binding source.
- `priority` should be a bounded categorical value such as P0, P1, P2, P3.
- `status` should be a bounded categorical value such as Draft, Reviewed, Implemented, Verified, Deferred, or Superseded.
- `normative_keyword` should preserve shall/shall not/should/may/derived/artifact when known.
- `parent_requirement_id`, when present, must reference an existing `requirement_id`.

## Verification matrix CSV

Expected canonical file: `hla_1516_verification_matrix_v1_0.csv`

Required columns:

- test_id
- requirement_id
- capability
- feature
- test_level
- transport
- status
- expected_evidence
- verification_notes

Minimum validation rules:

- `requirement_id` must reference the master catalog.
- `transport` should be one of static, native, grpc, rest, native/grpc/rest-equivalence, or another documented transport category.
- P0/P1 requirements should eventually have at least one verification row.

## Clause tracker CSV

Expected canonical file: `hla_1516_clause_tracker_v1_0.csv`

Required columns:

- standard
- clause
- title
- document_area
- normative_status
- priority
- detail_status_v1_0
- rows_in_catalog_v1_0
- decomposition_level
- next_action
- notes
