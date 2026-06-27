from __future__ import annotations

import importlib
from pathlib import Path


def _module_names_for_package(package_root: Path) -> list[str]:
    src_root = package_root / "src"
    if not src_root.exists():
        raise AssertionError(f"package is missing src/: {package_root}")
    module_names: list[str] = []
    for path in sorted(src_root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(src_root).with_suffix("")
        parts = list(rel.parts)
        if parts[-1] == "__init__":
            parts = parts[:-1]
        if not parts:
            continue
        module_names.append(".".join(parts))
    return sorted(set(module_names), key=lambda name: (name.count("."), name))


def _module_origin_matches(module: object, src_root: Path) -> bool:
    module_file = getattr(module, "__file__", None)
    if module_file is not None:
        return Path(module_file).resolve().is_relative_to(src_root.resolve())
    module_path = getattr(module, "__path__", None)
    if module_path is None:
        return False
    return any(Path(entry).resolve().is_relative_to(src_root.resolve()) for entry in module_path)


def assert_package_tree_importable(package_root: Path) -> None:
    src_root = (package_root / "src").resolve()
    failures: list[str] = []
    importlib.invalidate_caches()
    for module_name in _module_names_for_package(package_root):
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:
            failures.append(f"{module_name}: {type(exc).__name__}: {exc}")
            continue
        if not _module_origin_matches(module, src_root):
            failures.append(
                f"{module_name}: imported from unexpected location "
                f"{getattr(module, '__file__', getattr(module, '__path__', None))!r}"
            )
    if failures:
        joined = "\n".join(f"- {failure}" for failure in failures)
        raise AssertionError(f"package import smoke failed for {package_root.name}\n{joined}")


def package_root_from_test_file(test_file: str) -> Path:
    return Path(test_file).resolve().parent.parent
