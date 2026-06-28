#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEST_ROOTS = (ROOT / "tests" / "requirements", ROOT / "tests" / "verification")


@dataclass(frozen=True)
class FileScore:
    path: str
    bucket: str
    lines: int
    exact_contains_asserts: int
    normalized_refs: int
    counter_equality_asserts: int
    literal_equality_asserts: int
    raw_any_contains_asserts: int
    grouped_helper_asserts: int
    helper_wrapped: bool

    @property
    def score(self) -> int:
        raw = (
            self.exact_contains_asserts * 3
            + self.raw_any_contains_asserts * 2
            + self.normalized_refs * 2
            + self.literal_equality_asserts
            + self.counter_equality_asserts * 2
            + max(0, self.lines - 250) // 50
        )
        raw = max(0, raw - (self.grouped_helper_asserts * 3))
        if self.helper_wrapped:
            raw = max(0, raw - 36)
        return raw

    @property
    def tier(self) -> str:
        if self.score >= 500:
            return "critical"
        if self.score >= 200:
            return "high"
        if self.score >= 75:
            return "medium"
        return "low"


def _bucket_for(path: Path, text: str) -> str:
    if "2025" in path.name or "python1516_2025" in text or "/2025" in text:
        return "2025"
    if "2010" in path.name or "1516.1-2010" in text or "/2010" in text:
        return "2010"
    return "mixed"


def _is_literal_string(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and isinstance(node.value, str)


def _contains_normalized_name(node: ast.AST) -> bool:
    return any(
        isinstance(child, ast.Name) and "normalized" in child.id.lower()
        for child in ast.walk(node)
    )


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _is_counter_call(node: ast.AST) -> bool:
    return isinstance(node, ast.Call) and _call_name(node.func) == "Counter"


def _is_literalish(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) or (
        isinstance(node, (ast.List, ast.Tuple, ast.Set, ast.Dict))
        and all(_is_literalish(child) for child in ast.iter_child_nodes(node))
    )


def _is_any_contains_generator(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call) or _call_name(node.func) != "any" or len(node.args) != 1:
        return False
    generator = node.args[0]
    if not isinstance(generator, ast.GeneratorExp):
        return False
    elt = generator.elt
    return (
        isinstance(elt, ast.Compare)
        and len(elt.ops) == 1
        and isinstance(elt.ops[0], ast.In)
        and _is_literal_string(elt.left)
    )


def _count_assert_patterns(tree: ast.AST) -> tuple[int, int, int, int, int]:
    exact_contains = 0
    counter_eq = 0
    literal_eq = 0
    raw_any_contains = 0
    grouped_helper_asserts = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _call_name(node.func) in {
            "_assert_contains_all",
            "_assert_any_contains",
            "_assert_anchor_row",
            "_assert_disposition_row",
        }:
            grouped_helper_asserts += 1
        if not isinstance(node, ast.Assert):
            continue
        test = node.test
        if isinstance(test, ast.Compare) and len(test.ops) == 1 and len(test.comparators) == 1:
            left = test.left
            right = test.comparators[0]
            op = test.ops[0]
            if isinstance(op, ast.In) and _is_literal_string(left):
                exact_contains += 1
            if isinstance(op, ast.Eq):
                if _is_counter_call(left) and _is_counter_call(right):
                    counter_eq += 1
                if _is_literalish(right):
                    literal_eq += 1
        elif _is_any_contains_generator(test):
            raw_any_contains += 1
        elif _contains_normalized_name(test):
            # Treat normalized prose assertions as a distinct fragility vector
            pass
    return exact_contains, counter_eq, literal_eq, raw_any_contains, grouped_helper_asserts


def _score_file(path: Path) -> FileScore:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(path))
    exact_contains, counter_eq, literal_eq, raw_any_contains, grouped_helper_asserts = _count_assert_patterns(tree)
    normalized_refs = text.count("normalized = ") + text.count("normalized_")
    helper_wrapped = "_assert_contains_all" in text or "_normalize(" in text
    return FileScore(
        path=str(path.relative_to(ROOT)),
        bucket=_bucket_for(path, text),
        lines=len(text.splitlines()),
        exact_contains_asserts=exact_contains,
        normalized_refs=normalized_refs,
        counter_equality_asserts=counter_eq,
        literal_equality_asserts=literal_eq,
        raw_any_contains_asserts=raw_any_contains,
        grouped_helper_asserts=grouped_helper_asserts,
        helper_wrapped=helper_wrapped,
    )


def _iter_files() -> list[Path]:
    files: list[Path] = []
    for root in TEST_ROOTS:
        files.extend(sorted(root.rglob("test_*.py")))
    return files


def _summarize(scores: list[FileScore]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for bucket in ("2010", "2025", "mixed"):
        bucket_scores = [score for score in scores if score.bucket == bucket]
        if not bucket_scores:
            continue
        summary[bucket] = {
            "files": len(bucket_scores),
            "total_score": sum(score.score for score in bucket_scores),
            "avg_score": round(sum(score.score for score in bucket_scores) / len(bucket_scores)),
            "critical_files": sum(score.tier == "critical" for score in bucket_scores),
            "high_files": sum(score.tier == "high" for score in bucket_scores),
            "medium_files": sum(score.tier == "medium" for score in bucket_scores),
            "low_files": sum(score.tier == "low" for score in bucket_scores),
            "exact_contains_asserts": sum(score.exact_contains_asserts for score in bucket_scores),
            "raw_any_contains_asserts": sum(score.raw_any_contains_asserts for score in bucket_scores),
            "normalized_refs": sum(score.normalized_refs for score in bucket_scores),
        }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank requirement/verification tests by string-fragility signals.")
    parser.add_argument("--top", type=int, default=15, help="number of highest-risk files to print")
    args = parser.parse_args()

    scores = sorted((_score_file(path) for path in _iter_files()), key=lambda item: (-item.score, item.path))
    summary = _summarize(scores)

    print("Fragility summary")
    for bucket in ("2010", "2025", "mixed"):
        data = summary.get(bucket)
        if data is None:
            continue
        print(
            f"- {bucket}: files={data['files']} total_score={data['total_score']} avg_score={data['avg_score']} "
            f"critical={data['critical_files']} high={data['high_files']} medium={data['medium_files']} low={data['low_files']} "
            f"exact_contains={data['exact_contains_asserts']} any_contains={data['raw_any_contains_asserts']} normalized_refs={data['normalized_refs']}"
        )

    print("\nTop fragile files")
    for score in scores[: args.top]:
        print(
            f"- {score.score:>4} [{score.tier:<8}] {score.path} "
            f"(bucket={score.bucket}, lines={score.lines}, exact_in={score.exact_contains_asserts}, "
            f"any_in={score.raw_any_contains_asserts}, normalized_refs={score.normalized_refs}, "
            f"counter_eq={score.counter_equality_asserts}, literal_eq={score.literal_equality_asserts}, "
            f"grouped_helpers={score.grouped_helper_asserts}, helper_wrapped={str(score.helper_wrapped).lower()})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
