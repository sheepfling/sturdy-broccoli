# Python Requirement Disposition

This audit projects the canonical 2010 requirement catalog plus the canonical backend-resolution companion onto `python` so every row has an explicit generated `python` disposition.

## Summary

| Document clause | Total | Verified | Blocked | Vendor divergent | Not yet tested | Not applicable | Classification required |
|---|---:|---:|---:|---:|---:|---:|---:|
| IEEE 1516-2010 unknown | 4 | 3 | 0 | 0 | 0 | 1 | 0 |
| IEEE 1516-2010 §12 | 21 | 21 | 0 | 0 | 0 | 0 | 0 |
| IEEE 1516.1-2010 (2010 edition) §10 | 85 | 84 | 0 | 0 | 0 | 1 | 0 |
| IEEE 1516.1-2010 (2010 edition) §11 | 36 | 35 | 0 | 0 | 0 | 1 | 0 |
| IEEE 1516.1-2010 (2010 edition) §12 | 9 | 9 | 0 | 0 | 0 | 0 | 0 |
| IEEE 1516.1-2010 (2010 edition) §4 | 322 | 321 | 0 | 0 | 0 | 1 | 0 |
| IEEE 1516.1-2010 (2010 edition) §5 | 51 | 50 | 0 | 0 | 0 | 1 | 0 |
| IEEE 1516.1-2010 (2010 edition) §6 | 95 | 94 | 0 | 0 | 0 | 1 | 0 |
| IEEE 1516.1-2010 (2010 edition) §7 | 38 | 37 | 0 | 0 | 0 | 1 | 0 |
| IEEE 1516.1-2010 (2010 edition) §8 | 60 | 59 | 0 | 0 | 0 | 1 | 0 |
| IEEE 1516.1-2010 (2010 edition) §9 | 30 | 29 | 0 | 0 | 0 | 1 | 0 |
| IEEE 1516.2-2010 (2010 edition) unknown | 16 | 16 | 0 | 0 | 0 | 0 | 0 |
| IEEE 1516.2-2010 (2010 edition) §4 | 97 | 97 | 0 | 0 | 0 | 0 | 0 |
| IEEE 1516.2-2010 (2010 edition) §5 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| IEEE 1516.2-2010 (2010 edition) §6 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| IEEE 1516.2-2010 (2010 edition) §7 | 14 | 14 | 0 | 0 | 0 | 0 | 0 |

## Non-Verified Rows

| Document | Clause | Requirement | Disposition | Kind | Title |
|---|---|---|---|---|---|
| IEEE 1516-2010 | unknown | HLA1516-TIME-001 | not-applicable | extracted-requirement | The repo shall map time concepts to 1516.1 time services and grant/order semantics, including logical time and ordering relationships |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-001 | not-applicable | extracted-requirement | The RTI shall implement federation-management services for create, join, resign, destroy, save, restore, synchronization, and related lifecycle behavior |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-001 | not-applicable | extracted-requirement | The RTI shall implement declaration-management services for publication, subscription, registration control, and the associated error and precondition behavior |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-001 | not-applicable | extracted-requirement | The RTI shall implement object-management services for registration, update, delete, discovery, and interaction delivery behavior |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-001 | not-applicable | extracted-requirement | The RTI shall implement ownership-management services for unconditional, negotiated, acquisition, divestiture, and release-request flows |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-001 | not-applicable | extracted-requirement | The RTI shall implement time-management services for regulation, constrained behavior, query services, lookahead, order control, and grant delivery |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-001 | not-applicable | extracted-requirement | The RTI shall implement DDM services for region creation, routing, and filtered delivery behavior |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-001 | not-applicable | extracted-requirement | The RTI shall implement support services for lookups, factories, callback control, advisory behavior, and related support operations |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-001 | not-applicable | extracted-requirement | The RTI shall implement MOM behavior for tables, reports, service actions, observer reconstruction, and service-reporting state |
