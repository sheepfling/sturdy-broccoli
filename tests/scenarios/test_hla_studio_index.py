from __future__ import annotations

from pathlib import Path

from hla.verification.repo_internal.verification.hla_studio_index import (
    StudioArtifactLink,
    StudioSurfaceLink,
    relative_href,
    write_hla_studio_index,
)


def test_write_hla_studio_index_emits_surface_and_artifact_cards(tmp_path: Path) -> None:
    output_dir = tmp_path / "studio"
    contract_path = output_dir / "federate_service_contract.json"
    contract_path.parent.mkdir(parents=True, exist_ok=True)
    contract_path.write_text('{"interfaces": {}}\n', encoding="utf-8")

    path = write_hla_studio_index(
        output_dir,
        surfaces=(
            StudioSurfaceLink(
                name="FOM Explorer",
                href="../workbench/fom_workbench.html",
                summary="Inspect FOM load sets.",
                alias="./tools/fom-workbench",
                command="./tools/fom-workbench --html",
            ),
            StudioSurfaceLink(
                name="Federation Visualizer",
                href="../",
                summary="Observe live federation state.",
                alias="./tools/federation-subscriber-api",
                command="./tools/federation-subscriber-api",
            ),
            StudioSurfaceLink(
                name="RTI Bridge API",
                href="http://127.0.0.1:8788/",
                summary="Drive bounded RTIambassador-style sessions.",
                alias="./tools/federate-service-api",
                command="./tools/federate-service-api",
            ),
        ),
        artifacts=(
            StudioArtifactLink(
                label="RTI Bridge API contract export",
                href=relative_href(from_dir=output_dir, target=contract_path),
                description="Generated contract JSON.",
                group="RTI Bridge API",
            ),
        ),
    )

    text = path.read_text(encoding="utf-8")
    assert "HLA Studio" in text
    assert "FOM Explorer" in text
    assert "Federation Visualizer" in text
    assert "RTI Bridge API" in text
    assert "federate_service_contract.json" in text
