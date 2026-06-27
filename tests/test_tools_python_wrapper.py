from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_tools_python_help_describes_example_smoke_commands() -> None:
    result = subprocess.run(
        ["bash", "tools/python", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "./tools/python verify-smoke" in result.stdout
    assert "./tools/python verify-gold" in result.stdout
    assert "./tools/python verify-fast --with-gold" in result.stdout
    assert "./tools/python smoke-examples --edition 2010" in result.stdout
    assert "./tools/python smoke-examples --edition 2025" in result.stdout
    assert "./tools/python smoke-examples --all" in result.stdout
    assert "./tools/python test-examples" in result.stdout


def test_tools_python_verify_smoke_delegate_is_supported(tmp_path: Path) -> None:
    log_path = tmp_path / "verify-smoke.log"
    delegate = tmp_path / "delegate.sh"
    delegate.write_text(f"#!/usr/bin/env bash\nprintf '%s\\n' verify-smoke > '{log_path}'\n", encoding="utf-8")
    delegate.chmod(0o755)

    result = subprocess.run(
        ["bash", "tools/python", "verify-smoke"],
        cwd=ROOT,
        env={"PATH": str(Path("/usr/bin:/bin:/usr/sbin:/sbin")), "HLA2010_PYTHON_VERIFY_SMOKE_DELEGATE": str(delegate)},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    assert log_path.read_text(encoding="utf-8").strip() == "verify-smoke"


def test_tools_python_verify_gold_delegate_is_supported(tmp_path: Path) -> None:
    log_path = tmp_path / "verify-gold.log"
    delegate = tmp_path / "delegate.sh"
    delegate.write_text(f"#!/usr/bin/env bash\nprintf '%s\\n' verify-gold > '{log_path}'\n", encoding="utf-8")
    delegate.chmod(0o755)

    result = subprocess.run(
        ["bash", "tools/python", "verify-gold"],
        cwd=ROOT,
        env={"PATH": str(Path("/usr/bin:/bin:/usr/sbin:/sbin")), "HLA2010_PYTHON_VERIFY_GOLD_DELEGATE": str(delegate)},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    assert log_path.read_text(encoding="utf-8").strip() == "verify-gold"


def test_tools_python_verify_gold_uses_workspace_pythonpath(tmp_path: Path) -> None:
    log_path = tmp_path / "python.log"
    fake_python = tmp_path / "fake-python"
    fake_python.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from pathlib import Path",
                "import os",
                "import sys",
                f"log_path = Path({str(log_path)!r})",
                "with log_path.open('a', encoding='utf-8') as handle:",
                "    handle.write(' '.join(sys.argv[1:]) + '\\n')",
                "    handle.write(os.environ.get('PYTHONPATH', '') + '\\n')",
                "sys.exit(0)",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    fake_python.chmod(0o755)

    result = subprocess.run(
        ["bash", "tools/python", "verify-gold"],
        cwd=ROOT,
        env={"PATH": str(Path("/usr/bin:/bin:/usr/sbin:/sbin")), "HLA2010_PYTHON_VERIFY_ROUTES_PYTHON": str(fake_python)},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    lines = [line.strip() for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert lines[0] == (
        "scripts/package_hygiene_score.py --top 10 --fail-under 70 --max-stringy 0 "
        "--max-init-side-effects 0 --max-path-sniffing 0"
    )
    assert str(ROOT / "packages/hla-rti1516-2025/src") in lines[1]


def test_tools_python_verify_fast_with_gold_runs_fast_then_gold(tmp_path: Path) -> None:
    log_path = tmp_path / "python.log"
    fake_python = tmp_path / "fake-python"
    fake_python.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from pathlib import Path",
                "import sys",
                f"log_path = Path({str(log_path)!r})",
                "with log_path.open('a', encoding='utf-8') as handle:",
                "    handle.write(' '.join(sys.argv[1:]) + '\\n')",
                "sys.exit(0)",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    fake_python.chmod(0o755)

    result = subprocess.run(
        ["bash", "tools/python", "verify-fast", "--with-gold"],
        cwd=ROOT,
        env={"PATH": str(Path("/usr/bin:/bin:/usr/sbin:/sbin")), "HLA2010_PYTHON_VERIFY_ROUTES_PYTHON": str(fake_python)},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    lines = [line.strip() for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert lines[0] == (
        "-m pytest -q tests/test_operator_surface_policy.py "
        "tests/scenarios/test_test_surface_wrapper.py "
        "tests/scenarios/test_ci_green_wrappers.py "
        "tests/requirements/test_2025_route_parity_matrix.py "
        "tests/requirements/test_ieee_1516_2025_requirements_registry.py"
    )
    assert lines[1] == (
        "scripts/package_hygiene_score.py --top 10 --fail-under 70 --max-stringy 0 "
        "--max-init-side-effects 0 --max-path-sniffing 0"
    )


def test_tools_python_verify_fast_does_not_pass_with_gold_to_pytest(tmp_path: Path) -> None:
    log_path = tmp_path / "python.log"
    fake_python = tmp_path / "fake-python"
    fake_python.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from pathlib import Path",
                "import sys",
                f"log_path = Path({str(log_path)!r})",
                "with log_path.open('a', encoding='utf-8') as handle:",
                "    handle.write(' '.join(sys.argv[1:]) + '\\n')",
                "sys.exit(0)",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    fake_python.chmod(0o755)

    result = subprocess.run(
        ["bash", "tools/python", "verify-fast", "--with-gold"],
        cwd=ROOT,
        env={"PATH": str(Path("/usr/bin:/bin:/usr/sbin:/sbin")), "HLA2010_PYTHON_VERIFY_ROUTES_PYTHON": str(fake_python)},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    assert "--with-gold" not in log_path.read_text(encoding="utf-8")


def test_tools_python_verify_smoke_validates_manifest_before_pytest(tmp_path: Path) -> None:
    log_path = tmp_path / "python.log"
    fake_python = tmp_path / "fake-python"
    fake_python.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from pathlib import Path",
                "import sys",
                f"log_path = Path({str(log_path)!r})",
                "with log_path.open('a', encoding='utf-8') as handle:",
                "    handle.write(' '.join(sys.argv[1:]) + '\\n')",
                "sys.exit(0)",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    fake_python.chmod(0o755)

    result = subprocess.run(
        ["bash", "tools/python", "verify-smoke"],
        cwd=ROOT,
        env={"PATH": str(Path("/usr/bin:/bin:/usr/sbin:/sbin")), "HLA2010_PYTHON_VERIFY_ROUTES_PYTHON": str(fake_python)},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    lines = [line.strip() for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert lines[0].endswith("scripts/detect_workspace_duplicates.py clean-same-content")
    assert lines[1].endswith("scripts/detect_workspace_duplicates.py")
    assert lines[2].endswith("scripts/validate_test_surface_manifest.py")
    assert lines[3].startswith("-m pytest -q ")


def test_tools_python_smoke_examples_all_dry_run_lists_both_editions() -> None:
    result = subprocess.run(
        ["bash", "tools/python", "smoke-examples", "--all", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) == 2
    assert "examples/python_route_federate.py --edition 2010" in lines[0]
    assert "examples/python_route_federate.py --edition 2025" in lines[1]


def test_tools_python_test_examples_dry_run_targets_focused_test_file() -> None:
    result = subprocess.run(
        ["bash", "tools/python", "test-examples", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    assert lines == ["+ hla2010_shell_run_workspace_python python3 -m pytest -q tests/test_python_route_examples.py"]
