from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from conftest import REPO_ROOT, load_json_fixture as _load_json_fixture, read_repo_text
ROOT = REPO_ROOT


@dataclass(frozen=True)
class DocCase:
    case_id: str
    path: str
    must_contain: tuple[object, ...]
    must_not_contain: tuple[object, ...]

    @classmethod
    def from_mapping(cls, case: dict[str, object]) -> DocCase:
        must_contain = case.get("must_contain", [])
        must_not_contain = case.get("must_not_contain", [])
        return cls(
            case_id=str(case.get("id", "")).strip(),
            path=str(case["path"]),
            must_contain=tuple(must_contain) if isinstance(must_contain, (list, tuple)) else (),
            must_not_contain=tuple(must_not_contain) if isinstance(must_not_contain, (list, tuple)) else (),
        )


@dataclass(frozen=True)
class MultiPathDocCase:
    case_id: str
    paths: tuple[str, ...]
    must_contain: tuple[object, ...]
    must_not_contain: tuple[object, ...]

    @classmethod
    def from_mapping(cls, case: dict[str, object]) -> MultiPathDocCase:
        paths = case.get("paths", [])
        must_contain = case.get("must_contain", [])
        must_not_contain = case.get("must_not_contain", [])
        return cls(
            case_id=str(case.get("id", "")).strip(),
            paths=tuple(str(path) for path in paths) if isinstance(paths, (list, tuple)) else (),
            must_contain=tuple(must_contain) if isinstance(must_contain, (list, tuple)) else (),
            must_not_contain=tuple(must_not_contain) if isinstance(must_not_contain, (list, tuple)) else (),
        )


def load_doc_cases(fixture_name: str, key: str) -> list[DocCase]:
    fixture = load_json_fixture(fixture_name)
    cases = fixture[key]
    assert isinstance(cases, list)
    return [DocCase.from_mapping(case) for case in cases]


def load_multi_path_doc_cases(fixture_name: str, key: str) -> list[MultiPathDocCase]:
    fixture = load_json_fixture(fixture_name)
    cases = fixture[key]
    assert isinstance(cases, list)
    return [MultiPathDocCase.from_mapping(case) for case in cases]


def read(path: Path) -> str:
    return read_repo_text(path)


def primary_text(path: Path) -> str:
    text = read(path)
    historical_index = text.find("## Historical / Provenance")
    return text if historical_index == -1 else text[:historical_index]


def normalized_text(path: Path) -> str:
    return " ".join(read(path).split())


def normalized_primary_text(path: Path) -> str:
    return " ".join(primary_text(path).split())


def assert_contains_all(text: str, snippets: tuple[str, ...] | list[str], *, path: Path | None = None) -> None:
    for snippet in snippets:
        assert snippet in text, (
            f"{path.relative_to(ROOT) if path is not None else '<text>'} missing {snippet!r}"
        )


def assert_absent_all(text: str, snippets: tuple[str, ...] | list[str], *, path: Path | None = None) -> None:
    for snippet in snippets:
        assert snippet not in text, (
            f"{path.relative_to(ROOT) if path is not None else '<text>'} unexpectedly contains {snippet!r}"
        )


def load_json_fixture(name: str) -> dict[str, object]:
    return _load_json_fixture(name)


def _load_requirements_source() -> dict[str, object]:
    return json.loads(read_repo_text("requirements/source_of_truth.json"))


def resolve_fixture_snippet(snippet: object) -> str:
    if isinstance(snippet, str):
        return snippet
    if not isinstance(snippet, dict):
        raise TypeError(f"unsupported snippet type: {type(snippet)!r}")

    data = _load_requirements_source()
    if "trace_example" in snippet:
        spec = snippet["trace_example"]
        if not isinstance(spec, dict):
            raise TypeError("trace_example snippet must be an object")
        example_id = str(spec["id"])
        field = str(spec["field"])
        index = int(spec.get("index", 0))
        examples = data.get("trace_examples", [])
        if not isinstance(examples, list):
            raise KeyError("trace_examples")
        example = next(
            item for item in examples if isinstance(item, dict) and str(item.get("id", "")) == example_id
        )
        value = example.get(field)
        if isinstance(value, list):
            return str(value[index])
        return str(value)

    if "doc_projection" in snippet:
        spec = snippet["doc_projection"]
        if not isinstance(spec, dict):
            raise TypeError("doc_projection snippet must be an object")
        projection_id = str(spec["id"])
        index = int(spec.get("index", 0))
        projections = data.get("doc_projections", {})
        if not isinstance(projections, dict):
            raise KeyError("doc_projections")
        values = projections[projection_id]
        if not isinstance(values, list):
            raise TypeError(f"doc projection {projection_id!r} is not a list")
        return str(values[index])

    raise KeyError(f"unsupported snippet mapping: {snippet}")


def assert_doc_case(
    case: DocCase | dict[str, object],
    *,
    reader: Callable[[Path], str] = read,
) -> None:
    if isinstance(case, dict):
        case = DocCase.from_mapping(case)
    path = ROOT / case.path
    text = reader(path)
    must_contain = tuple(resolve_fixture_snippet(snippet) for snippet in case.must_contain)
    must_not_contain = tuple(resolve_fixture_snippet(snippet) for snippet in case.must_not_contain)
    assert_contains_all(text, must_contain, path=path)
    assert_absent_all(text, must_not_contain, path=path)


def assert_doc_case_across_paths(
    case: MultiPathDocCase,
    *,
    reader: Callable[[Path], str] = read,
) -> None:
    must_contain = tuple(resolve_fixture_snippet(snippet) for snippet in case.must_contain)
    must_not_contain = tuple(resolve_fixture_snippet(snippet) for snippet in case.must_not_contain)
    for rel_path in case.paths:
        path = ROOT / rel_path
        text = reader(path)
        assert_contains_all(text, must_contain, path=path)
        assert_absent_all(text, must_not_contain, path=path)


def doc_relative_reference(doc_path: Path, expected_path: Path) -> tuple[str, str]:
    repo_rel = expected_path.relative_to(ROOT).as_posix()
    if doc_path.parent == ROOT:
        return repo_rel, repo_rel
    doc_rel = Path(os.path.relpath(expected_path, start=doc_path.parent)).as_posix()
    return repo_rel, doc_rel


def documented_tool_inventory() -> set[str]:
    text = read(ROOT / "tools" / "README.md")
    return {
        line.strip().split("./tools/", 1)[1][:-1]
        for line in text.splitlines()
        if line.strip().startswith("- `./tools/") and line.strip().endswith("`")
    }


def scripts_readme_supported_tool_inventory() -> set[str]:
    lines = read(ROOT / "scripts" / "README.md").splitlines()
    start = next(
        index
        for index, line in enumerate(lines)
        if "Supported human-facing entrypoints live under `tools/`" in line
    )
    inventory: set[str] = set()
    for line in lines[start + 1 :]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped == "Repo setup entrypoints that still live under `scripts/`:":
            break
        if stripped.startswith("- `./tools/"):
            inventory.add(stripped.split("./tools/", 1)[1].split("`", 1)[0])
    return inventory


def actual_top_level_tool_wrappers() -> set[str]:
    return {
        path.name
        for path in (ROOT / "tools").iterdir()
        if path.is_file() and path.name != "README.md" and "." not in path.name
    }


def actual_repo_root_files() -> set[str]:
    return {path.name for path in ROOT.iterdir() if path.is_file()}
