"""Generic loader helpers for Python extension modules and shared libraries."""
from __future__ import annotations

import ctypes
import importlib
import importlib.util
import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Any, Mapping


_EXTENSION_SUFFIXES = {".so", ".pyd", ".dylib"}


@dataclass(frozen=True, slots=True)
class BindingTarget:
    """Describe a Python extension module or shared library to load."""

    load_mode: str = "auto"
    module_name: str | None = None
    module_path: str | Path | None = None
    library_path: str | Path | None = None
    symbol_name: str = "create_backend"
    search_path: tuple[str | Path, ...] = ()


@dataclass(frozen=True, slots=True)
class LoadedBinding:
    """Resolved binding target."""

    target: BindingTarget
    kind: str
    module: ModuleType | None = None
    library: ctypes.CDLL | None = None
    details: Mapping[str, Any] = field(default_factory=dict)

    def resolve_callable(self, *names: str) -> Any | None:
        """Return the first callable exported by the loaded module or library."""

        candidates = names or (self.target.symbol_name,)
        if self.module is not None:
            for name in candidates:
                attr = getattr(self.module, name, None)
                if callable(attr):
                    return attr
        if self.library is not None:
            for name in candidates:
                attr = getattr(self.library, name, None)
                if attr is not None:
                    return attr
        return None


def _coerce_path(value: str | Path | None) -> Path | None:
    if value is None:
        return None
    return Path(value).expanduser()


def _load_python_module(target: BindingTarget) -> LoadedBinding:
    module_name = target.module_name
    module_path = _coerce_path(target.module_path)
    if module_name is not None:
        module = importlib.import_module(module_name)
        return LoadedBinding(
            target=target,
            kind="python-module",
            module=module,
            details={"module_name": module.__name__},
        )

    if module_path is None:
        raise ValueError("BindingTarget requires module_name or module_path for a Python module load")

    module_name = module_path.stem
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create an import spec for {module_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return LoadedBinding(
        target=target,
        kind="python-module-file",
        module=module,
        details={"module_name": module.__name__, "module_path": str(module_path)},
    )


def _load_shared_library(target: BindingTarget) -> LoadedBinding:
    library_path = _coerce_path(target.library_path)
    if library_path is None:
        raise ValueError("BindingTarget requires library_path for a shared-library load")
    library = ctypes.CDLL(str(library_path))
    return LoadedBinding(
        target=target,
        kind="shared-library",
        library=library,
        details={"library_path": str(library_path)},
    )


def load_binding(
    target: BindingTarget | str | Path | None,
    *,
    symbol_name: str = "create_backend",
) -> LoadedBinding | None:
    """Load a Python extension module or shared library for the given target."""

    if target is None:
        return None
    if isinstance(target, (str, Path)):
        candidate = Path(target).expanduser()
        if candidate.suffix.lower() in _EXTENSION_SUFFIXES or candidate.exists():
            return load_binding(
                BindingTarget(
                    load_mode="module",
                    module_path=candidate,
                    library_path=candidate,
                    symbol_name=symbol_name,
                ),
            )
        return load_binding(BindingTarget(module_name=str(target), symbol_name=symbol_name))

    if target.load_mode == "library":
        return _load_shared_library(target)
    if target.load_mode == "module":
        return _load_python_module(target)
    if target.module_name is not None or target.module_path is not None:
        return _load_python_module(target)
    if target.library_path is not None:
        return _load_shared_library(target)
    raise ValueError("BindingTarget must define module_name, module_path, or library_path")


def binding_target_from_options(options: Mapping[str, Any]) -> BindingTarget | None:
    """Extract a binding target from backend options."""

    module_name = options.get("module_name")
    module_path = options.get("module_path") or options.get("extension_path")
    library_path = options.get("library_path")
    symbol_name = str(options.get("symbol_name", "create_backend"))
    search_path = tuple(options.get("search_path", ()))
    load_mode = str(options.get("load_mode", "auto"))
    if module_name is None and module_path is None and library_path is None:
        return None
    return BindingTarget(
        load_mode=load_mode,
        module_name=str(module_name) if module_name is not None else None,
        module_path=module_path,
        library_path=library_path,
        symbol_name=symbol_name,
        search_path=search_path,
    )


__all__ = ["BindingTarget", "LoadedBinding", "binding_target_from_options", "load_binding"]
