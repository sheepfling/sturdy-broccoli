from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from hla.backends.cpp_shim.cpp_toolchain import CppToolchainArtifact, CppToolchainInventory


ROOT = Path(__file__).resolve().parents[2]


def _load_shim_routes_module():
    spec = importlib.util.spec_from_file_location("shim_routes_module_for_cpp_tests", ROOT / "scripts" / "shim_routes.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_cpp_toolchain_inventory_reports_tools_and_artifacts(tmp_path: Path, monkeypatch, capsys) -> None:
    cxx_bin = tmp_path / "toolchain" / "bin" / "c++"
    ar_bin = tmp_path / "toolchain" / "bin" / "ar"
    cmake_bin = tmp_path / "toolchain" / "bin" / "cmake"
    cxx_bin.parent.mkdir(parents=True)
    cxx_bin.write_text("")
    ar_bin.write_text("")
    cmake_bin.write_text("")

    cpp_2010 = tmp_path / "repo" / "build/shim_routes/cpp-standard-2010/librti1516e_standard_cpp_shim.a"
    cpp_2025 = tmp_path / "repo" / "build/shim_routes/cpp-standard-2025/librti1516_2025_standard_cpp_shim.a"
    cpp_2010.parent.mkdir(parents=True)
    cpp_2025.parent.mkdir(parents=True)
    cpp_2010.write_text("archive")
    cpp_2025.write_text("archive")

    artifact_2010 = CppToolchainArtifact(
        key="cpp-standard-2010",
        label="C++ 2010 standard shim archive",
        path=str(cpp_2010),
        exists=True,
        build_command="./tools/shim-routes build cpp-standard-2010",
    )
    artifact_2025 = CppToolchainArtifact(
        key="cpp-standard-2025",
        label="C++ 2025 standard shim archive",
        path=str(cpp_2025),
        exists=True,
        build_command="./tools/shim-routes build cpp-standard-2025",
    )
    inventory = CppToolchainInventory(
        cxx=str(cxx_bin),
        ar=str(ar_bin),
        cmake=str(cmake_bin),
        cxx_ok=True,
        ar_ok=True,
        cmake_ok=True,
        status="ready",
        artifacts=(artifact_2010, artifact_2025),
        notes=("standard-shim build prerequisites are available",),
    )

    from hla.backends import cpp_shim

    monkeypatch.setattr(cpp_shim, "discover_cpp_toolchain", lambda repo_root_arg: inventory)

    module = _load_shim_routes_module()
    output_dir = tmp_path / "reports"
    rc = module.main(["cpp", "doctor", "--output-dir", str(output_dir)])
    assert rc == 0

    json_path = output_dir / "cpp-toolchain.json"
    md_path = output_dir / "cpp-toolchain.md"
    assert json_path.exists()
    assert md_path.exists()

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["status"] == "ready"
    assert payload["cxx_ok"] is True
    assert payload["ar_ok"] is True
    assert payload["cmake_ok"] is True
    assert payload["artifacts"][0]["exists"] is True

    stdout_payload = json.loads(capsys.readouterr().out)
    assert stdout_payload["evidence_json"] == str(json_path)
    assert stdout_payload["evidence_markdown"] == str(md_path)
    assert stdout_payload["recommended_commands"] == []

    rendered = md_path.read_text(encoding="utf-8")
    assert "# C++ Toolchain Inventory" in rendered
    assert "C++ 2010 standard shim archive" in rendered
    assert "C++ 2025 standard shim archive" in rendered
    assert "./tools/shim-routes build cpp-standard-2010" in rendered
    assert "./tools/shim-routes build cpp-standard-2025" in rendered
