from __future__ import annotations

import subprocess
from pathlib import Path

from conftest import workspace_python_bin, workspace_python_env
from hla2010.fom import parse_fom_xml
from hla2010_fom_minimal_demo.scenarios import (
    make_minimal_demo_factory,
    minimal_demo_fom_path,
    run_minimal_demo_scenario,
)


ROOT = Path(__file__).resolve().parents[2]


def test_minimal_demo_fom_path_resolves_to_package_resource() -> None:
    path = Path(minimal_demo_fom_path()).resolve()
    assert path.name == "MinimalDemoFOMmodule.xml"
    assert "packages/hla2010-fom-minimal-demo/src/hla2010_fom_minimal_demo/resources/foms" in str(path)


def test_minimal_demo_fom_declares_one_object_and_one_interaction() -> None:
    module = parse_fom_xml(minimal_demo_fom_path())
    assert module.name == "Minimal Demo FOM Module"
    assert "HLAobjectRoot.DemoObject" in {spec.full_name for spec in module.object_classes}
    assert "HLAinteractionRoot.DemoAnnouncement" in {spec.full_name for spec in module.interaction_classes}


def test_minimal_demo_runs_against_python_rti() -> None:
    result = run_minimal_demo_scenario(
        make_minimal_demo_factory("python"),
        fom_modules=[minimal_demo_fom_path()],
    )
    assert result.backend_kinds == ("python/in-memory", "python/in-memory")
    assert len(result.object_updates) == 1
    assert result.object_updates[0].object_name == "Publisher-1"
    assert result.object_updates[0].message == "hello-object"
    assert len(result.interactions) == 1
    assert result.interactions[0].sender == "Publisher-1"
    assert result.interactions[0].message == "hello-interaction"


def test_minimal_demo_records_publish_subscribe_callbacks() -> None:
    result = run_minimal_demo_scenario(
        make_minimal_demo_factory("python"),
        object_message="demo-object",
        interaction_message="demo-interaction",
        fom_modules=[minimal_demo_fom_path()],
    )
    subscriber_event_names = [name for name, _payload in result.subscriber_events]
    assert "discover_object_instance" in subscriber_event_names
    assert "reflect_attribute_values" in subscriber_event_names
    assert "receive_interaction" in subscriber_event_names


def test_minimal_demo_example_script_runs() -> None:
    python_bin = workspace_python_bin()
    result = subprocess.run(
        [str(python_bin), "examples/minimal_fom_demo.py", "--backend", "python"],
        cwd=ROOT,
        env=workspace_python_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "backend=python/in-memory,python/in-memory" in result.stdout
    assert "object name=Publisher-1 message=hello-object" in result.stdout
    assert "interaction sender=Publisher-1 message=hello-interaction" in result.stdout


def test_minimal_demo_example_accepts_in_memory_factory_alias() -> None:
    python_bin = workspace_python_bin()
    result = subprocess.run(
        [str(python_bin), "examples/minimal_fom_demo.py", "--backend", "in-memory"],
        cwd=ROOT,
        env=workspace_python_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[0].startswith("backend=python/in-memory,python/in-memory")
