from __future__ import annotations

from dataclasses import dataclass

from conftest import load_json_fixture


@dataclass(frozen=True)
class PitchVendorDivergenceGroup:
    ids: frozenset[str]
    refs: tuple[str, ...]


@dataclass(frozen=True)
class PitchVendorDivergenceCase:
    expected_ids: frozenset[str]
    shared_refs: tuple[str, ...]
    groups: dict[str, PitchVendorDivergenceGroup]


@dataclass(frozen=True)
class PitchMatrixPolicy:
    tranche_clauses_no_not_yet_tested: tuple[str, ...]
    clause4_summary_counts: dict[str, int]
    vendor_divergence_cases: dict[str, PitchVendorDivergenceCase]

    @classmethod
    def from_mapping(cls, payload: dict[str, object]) -> PitchMatrixPolicy:
        return cls(
            tranche_clauses_no_not_yet_tested=tuple(
                str(item) for item in payload["tranche_clauses_no_not_yet_tested"]
            ),
            clause4_summary_counts={
                str(key): int(value)
                for key, value in payload["clause4_summary_counts"].items()
            },
            vendor_divergence_cases={
                str(clause): PitchVendorDivergenceCase(
                    expected_ids=frozenset(str(item) for item in spec["expected_ids"]),
                    shared_refs=tuple(str(item) for item in spec["shared_refs"]),
                    groups={
                        str(name): PitchVendorDivergenceGroup(
                            ids=frozenset(str(item) for item in group["ids"]),
                            refs=tuple(str(item) for item in group["refs"]),
                        )
                        for name, group in spec["groups"].items()
                    },
                )
                for clause, spec in payload["vendor_divergence_cases"].items()
            },
        )


PITCH_MATRIX_POLICY = PitchMatrixPolicy.from_mapping(
    load_json_fixture("pitch_matrix_policy.json")
)
