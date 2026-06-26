"""C++ toolchain discovery and inventory reporting."""
from __future__ import annotations

import json
import os
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


CPP_2010_ARTIFACT = Path(
    os.environ.get(
        "HLA_X_CPP_STANDARD_2010_ARTIFACT",
        "build/shim_routes/cpp-standard-2010/librti1516e_standard_cpp_shim.a",
    )
)
CPP_2025_ARTIFACT = Path(
    os.environ.get(
        "HLA_X_CPP_STANDARD_2025_ARTIFACT",
        "build/shim_routes/cpp-standard-2025/librti1516_2025_standard_cpp_shim.a",
    )
)


@dataclass(frozen=True, slots=True)
class CppToolchainArtifact:
    key: str
    label: str
    path: str
    exists: bool
    build_command: str


@dataclass(frozen=True, slots=True)
class CppToolchainInventory:
    cxx: str | None
    ar: str | None
    cmake: str | None
    cxx_ok: bool
    ar_ok: bool
    cmake_ok: bool
    status: str
    artifacts: tuple[CppToolchainArtifact, ...]
    notes: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return self.status == "ready"

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


def _repo_rel(path: str | None, repo_root: Path) -> str | None:
    if path is None:
        return None
    candidate = Path(path)
    try:
        return candidate.relative_to(repo_root).as_posix()
    except ValueError:
        return path


def _artifact(key: str, label: str, path: Path, build_command: str) -> CppToolchainArtifact:
    return CppToolchainArtifact(
        key=key,
        label=label,
        path=str(path),
        exists=path.exists(),
        build_command=build_command,
    )


def discover_cpp_toolchain(repo_root: Path) -> CppToolchainInventory:
    cxx = shutil.which("c++")
    ar = shutil.which("ar")
    cmake = shutil.which("cmake")
    artifacts = (
        _artifact(
            "cpp-standard-2010",
            "C++ 2010 standard shim archive",
            repo_root / CPP_2010_ARTIFACT,
            "./tools/shim-routes build cpp-standard-2010",
        ),
        _artifact(
            "cpp-standard-2025",
            "C++ 2025 standard shim archive",
            repo_root / CPP_2025_ARTIFACT,
            "./tools/shim-routes build cpp-standard-2025",
        ),
    )

    cxx_ok = cxx is not None
    ar_ok = ar is not None
    cmake_ok = cmake is not None
    artifact_ok = all(item.exists for item in artifacts)

    notes: list[str] = []
    warnings: list[str] = []
    if cxx_ok and ar_ok:
        notes.append("standard-shim build prerequisites are available")
    else:
        warnings.append("standard-shim builds require both c++ and ar on PATH")
    if not cmake_ok:
        warnings.append("cmake is missing; C++ SDK capsule generation will stay unavailable")
    if not artifact_ok:
        warnings.append("one or more C++ standard shim archives are missing; build them with ./tools/shim-routes build <target>")

    if cxx_ok and ar_ok and artifact_ok:
        status = "ready"
    elif cxx_ok or ar_ok or cmake_ok or artifact_ok:
        status = "degraded"
    else:
        status = "blocked"

    return CppToolchainInventory(
        cxx=cxx,
        ar=ar,
        cmake=cmake,
        cxx_ok=cxx_ok,
        ar_ok=ar_ok,
        cmake_ok=cmake_ok,
        status=status,
        artifacts=artifacts,
        notes=tuple(notes),
        warnings=tuple(warnings),
    )


def render_cpp_toolchain_markdown(inventory: CppToolchainInventory) -> str:
    def verdict(value: bool) -> str:
        return "PASS" if value else "FAIL"

    lines = [
        "# C++ Toolchain Inventory",
        "",
        f"- Status: `{inventory.status}`",
        f"- c++: `{inventory.cxx or ''}`",
        f"- ar: `{inventory.ar or ''}`",
        f"- cmake: `{inventory.cmake or ''}`",
        "",
        "## Tool Checks",
        "",
        f"- c++: {verdict(inventory.cxx_ok)}",
        f"- ar: {verdict(inventory.ar_ok)}",
        f"- cmake: {verdict(inventory.cmake_ok)}",
        "",
        "## Shim Artifacts",
        "",
        "| key | label | path | exists | build command |",
        "| --- | --- | --- | --- | --- |",
    ]
    for artifact in inventory.artifacts:
        lines.append(
            f"| `{artifact.key}` | {artifact.label} | `{artifact.path}` | {verdict(artifact.exists)} | `{artifact.build_command}` |"
        )
    lines.extend(["", "## Notes", ""])
    if inventory.notes:
        lines.extend(f"- {note}" for note in inventory.notes)
    else:
        lines.append("- none")
    lines.extend(["", "## Warnings", ""])
    if inventory.warnings:
        lines.extend(f"- {warning}" for warning in inventory.warnings)
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def write_cpp_toolchain_reports(inventory: CppToolchainInventory, output_dir: str | Path) -> tuple[Path, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    payload = inventory.to_json_dict()
    rendered_inventory = inventory
    if output.resolve().parts[-3:] == ("docs", "evidence", "shim_routes"):
        repo_root = output.resolve().parents[2]
        payload["cxx"] = _repo_rel(inventory.cxx, repo_root)
        payload["ar"] = _repo_rel(inventory.ar, repo_root)
        payload["cmake"] = _repo_rel(inventory.cmake, repo_root)
        payload["artifacts"] = [
            {
                **artifact,
                "path": _repo_rel(str(artifact["path"]), repo_root),
            }
            for artifact in payload["artifacts"]
        ]
        rendered_inventory = CppToolchainInventory(
            cxx=_repo_rel(inventory.cxx, repo_root),
            ar=_repo_rel(inventory.ar, repo_root),
            cmake=_repo_rel(inventory.cmake, repo_root),
            cxx_ok=inventory.cxx_ok,
            ar_ok=inventory.ar_ok,
            cmake_ok=inventory.cmake_ok,
            status=inventory.status,
            artifacts=tuple(
                CppToolchainArtifact(
                    key=artifact.key,
                    label=artifact.label,
                    path=_repo_rel(artifact.path, repo_root) or artifact.path,
                    exists=artifact.exists,
                    build_command=artifact.build_command,
                )
                for artifact in inventory.artifacts
            ),
            notes=inventory.notes,
            warnings=inventory.warnings,
        )
    json_path = output / "cpp-toolchain.json"
    md_path = output / "cpp-toolchain.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_cpp_toolchain_markdown(rendered_inventory), encoding="utf-8")
    return json_path, md_path


__all__ = [
    "CPP_2010_ARTIFACT",
    "CPP_2025_ARTIFACT",
    "CppToolchainArtifact",
    "CppToolchainInventory",
    "discover_cpp_toolchain",
    "render_cpp_toolchain_markdown",
    "write_cpp_toolchain_reports",
]
