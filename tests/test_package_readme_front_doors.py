from __future__ import annotations

from tests.doc_test_helpers import ROOT, assert_contains_all, assert_doc_case, read


def test_packages_readme_stays_a_package_entry_map() -> None:
    path = ROOT / "packages" / "README.md"
    text = read(path)
    assert_contains_all(
        text,
        (
            "## Start Here",
            "## Edit Here First",
            "## Ownership Cards",
            "## Read Next",
            "which package owns the change",
            "shortest safe edit boundary",
        ),
        path=path,
    )


def test_key_package_readmes_keep_start_here_ownership_and_read_next() -> None:
    cases = (
        {
            "path": "packages/hla2010-spec/README.md",
            "must_contain": (
                "## Start Here",
                "## Ownership Card",
                "## Read Next",
                "public contract or shared spec-side",
            ),
        },
        {
            "path": "packages/hla2010-rti-python/README.md",
            "must_contain": (
                "## Start Here",
                "## Ownership Card",
                "## Read Next",
                "reference Python RTI",
            ),
        },
        {
            "path": "packages/hla2010-fom-target-radar/README.md",
            "must_contain": (
                "## Start Here",
                "## Read Next",
                "extend the example itself",
            ),
        },
    )
    for case in cases:
        assert_doc_case(case)
