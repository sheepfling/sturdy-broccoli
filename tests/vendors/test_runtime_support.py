from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
import socket
import pytest

from hla2010.enums import ResignAction

from tests.vendors.runtime_support import (
    assert_all_terminated,
    assert_runtime_process_stopped,
    cleanup_federation,
    close_all,
    require_vendor_preflight,
    reserve_udp_pair,
    shutdown_runtime_resources,
    terminate_all,
    udp_port_pair,
    wait_for_tcp_listener_closed,
)


@dataclass
class _FakeRTI:
    calls: list[tuple[str, object]] = field(default_factory=list)

    def resign_federation_execution(self, action: ResignAction) -> None:
        self.calls.append(("resign", action))

    def destroy_federation_execution(self, federation_name: str) -> None:
        self.calls.append(("destroy", federation_name))

    def disconnect(self) -> None:
        self.calls.append(("disconnect", None))

    def close(self) -> None:
        self.calls.append(("close", None))

    def terminate(self) -> None:
        self.calls.append(("terminate", None))


def test_reserve_udp_pair_returns_distinct_ports_and_releases_them() -> None:
    with reserve_udp_pair() as lease:
        assert len(lease.ports) == 2
        assert lease.ports[0] != lease.ports[1]

    assert lease._sockets == ()


def test_cleanup_federation_runs_best_effort_sequence() -> None:
    owner = _FakeRTI()
    peer = _FakeRTI()

    cleanup_federation(
        "fed",
        destroyer=owner,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((peer, ResignAction.NO_ACTION),),
        disconnect_rtis=(peer, owner),
    )

    assert owner.calls == [
        ("resign", ResignAction.DELETE_OBJECTS),
        ("destroy", "fed"),
        ("disconnect", None),
    ]
    assert peer.calls == [
        ("resign", ResignAction.NO_ACTION),
        ("disconnect", None),
    ]


def test_close_all_and_terminate_all_ignore_none() -> None:
    closable = _FakeRTI()
    terminable = _FakeRTI()

    close_all(None, closable)
    terminate_all(None, terminable)

    assert closable.calls == [("close", None)]
    assert terminable.calls == [("terminate", None)]


def test_shutdown_runtime_resources_closes_terminates_and_asserts() -> None:
    closable = _FakeRTI()

    @dataclass
    class _StoppedRuntime:
        terminated: bool = False

        def terminate(self) -> None:
            self.terminated = True

        def poll(self) -> int | None:
            return 0 if self.terminated else None

    runtime = _StoppedRuntime()
    shutdown_runtime_resources(
        close_resources=(closable,),
        runtime_resources=(runtime,),
        timeout=0.2,
    )

    assert closable.calls == [("close", None)]
    assert runtime.terminated is True


def test_udp_port_pair_can_wrap_static_base() -> None:
    with udp_port_pair(61234) as ports:
        assert ports == (61234, 61235)


def test_wait_for_tcp_listener_closed_detects_listener_shutdown() -> None:
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    host, port = listener.getsockname()
    listener.close()

    wait_for_tcp_listener_closed(str(host), int(port), timeout=1.0)


def test_assert_runtime_process_stopped_waits_for_poll_and_listener_shutdown() -> None:
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    host, port = listener.getsockname()

    @dataclass
    class _FakeRuntime:
        host: str
        tcp_port: int
        polls_remaining: int = 2

        def poll(self) -> int | None:
            if self.polls_remaining > 0:
                self.polls_remaining -= 1
                if self.polls_remaining == 0:
                    listener.close()
                    return 0
                return None
            return 0

    assert_runtime_process_stopped(_FakeRuntime(str(host), int(port)), timeout=1.0)


def test_assert_runtime_process_stopped_times_out_for_lingering_process() -> None:
    @dataclass
    class _LingeringRuntime:
        def poll(self) -> int | None:
            return None

    with pytest.raises(AssertionError, match="Timed out waiting for runtime process shutdown"):
        assert_runtime_process_stopped(_LingeringRuntime(), timeout=0.2)


def test_assert_all_terminated_checks_every_resource() -> None:
    calls: list[str] = []

    @dataclass
    class _StoppedRuntime:
        name: str

        def poll(self) -> int | None:
            calls.append(self.name)
            return 0

    assert_all_terminated(_StoppedRuntime("left"), None, _StoppedRuntime("right"), timeout=0.2)
    assert calls == ["left", "right"]


def test_require_vendor_preflight_skips_when_flag_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HLA2010_CERTI_PREFLIGHT_OK", raising=False)

    with pytest.raises(pytest.skip.Exception, match="certi preflight not confirmed"):
        require_vendor_preflight("certi", operator_hint="./scripts/certi_easy.sh preflight")


def test_require_vendor_preflight_accepts_confirmed_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HLA2010_PITCH_PREFLIGHT_OK", "1")

    require_vendor_preflight("pitch", operator_hint="./scripts/pitch_docker_easy.sh preflight")


def test_require_vendor_preflight_accepts_successful_artifact(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    artifact_dir = tmp_path / "preflight"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "certi-preflight.json").write_text(
        json.dumps(
            {
                "tool": "certi-preflight",
                "environment": "loopback-ok",
                "result": "real CERTI runnable",
                "exit_code": 0,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("HLA2010_CERTI_PREFLIGHT_OK", raising=False)
    monkeypatch.setenv("HLA2010_PREFLIGHT_ARTIFACT_DIR", str(artifact_dir))

    require_vendor_preflight("certi", operator_hint="./scripts/certi_easy.sh preflight")


def test_require_vendor_preflight_ignores_failed_artifact(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    artifact_dir = tmp_path / "preflight"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "pitch-preflight.json").write_text(
        json.dumps(
            {
                "tool": "pitch-preflight",
                "environment": "ready",
                "result": "ready to run ./scripts/pitch_docker_easy.sh install or ./scripts/pitch_docker_easy.sh all",
                "exit_code": 1,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("HLA2010_PITCH_PREFLIGHT_OK", raising=False)
    monkeypatch.setenv("HLA2010_PREFLIGHT_ARTIFACT_DIR", str(artifact_dir))

    with pytest.raises(pytest.skip.Exception, match="pitch preflight not confirmed"):
        require_vendor_preflight("pitch", operator_hint="./scripts/pitch_docker_easy.sh preflight")


def test_require_vendor_preflight_ignores_wrong_tool_artifact(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    artifact_dir = tmp_path / "preflight"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "certi-preflight.json").write_text(
        json.dumps(
            {
                "tool": "pitch-preflight",
                "environment": "loopback-ok",
                "result": "real CERTI runnable",
                "exit_code": 0,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("HLA2010_CERTI_PREFLIGHT_OK", raising=False)
    monkeypatch.setenv("HLA2010_PREFLIGHT_ARTIFACT_DIR", str(artifact_dir))

    with pytest.raises(pytest.skip.Exception, match="certi preflight not confirmed"):
        require_vendor_preflight("certi", operator_hint="./scripts/certi_easy.sh preflight")


def test_require_vendor_preflight_ignores_wrong_environment_artifact(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    artifact_dir = tmp_path / "preflight"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "pitch-preflight.json").write_text(
        json.dumps(
            {
                "tool": "pitch-preflight",
                "environment": "ports-blocked",
                "result": "ready to run ./scripts/pitch_docker_easy.sh install or ./scripts/pitch_docker_easy.sh all",
                "exit_code": 0,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("HLA2010_PITCH_PREFLIGHT_OK", raising=False)
    monkeypatch.setenv("HLA2010_PREFLIGHT_ARTIFACT_DIR", str(artifact_dir))

    with pytest.raises(pytest.skip.Exception, match="pitch preflight not confirmed"):
        require_vendor_preflight("pitch", operator_hint="./scripts/pitch_docker_easy.sh preflight")


def test_require_vendor_preflight_ignores_wrong_result_artifact(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    artifact_dir = tmp_path / "preflight"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "certi-preflight.json").write_text(
        json.dumps(
            {
                "tool": "certi-preflight",
                "environment": "loopback-ok",
                "result": "real CERTI will skip",
                "exit_code": 0,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("HLA2010_CERTI_PREFLIGHT_OK", raising=False)
    monkeypatch.setenv("HLA2010_PREFLIGHT_ARTIFACT_DIR", str(artifact_dir))

    with pytest.raises(pytest.skip.Exception, match="certi preflight not confirmed"):
        require_vendor_preflight("certi", operator_hint="./scripts/certi_easy.sh preflight")


def test_require_vendor_preflight_ignores_stale_artifact(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    artifact_dir = tmp_path / "preflight"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_dir / "certi-preflight.json"
    artifact_path.write_text(
        json.dumps(
            {
                "tool": "certi-preflight",
                "environment": "loopback-ok",
                "result": "real CERTI runnable",
                "exit_code": 0,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    stale_time = artifact_path.stat().st_mtime - 600
    os.utime(artifact_path, (stale_time, stale_time))
    monkeypatch.delenv("HLA2010_CERTI_PREFLIGHT_OK", raising=False)
    monkeypatch.setenv("HLA2010_PREFLIGHT_ARTIFACT_DIR", str(artifact_dir))
    monkeypatch.setenv("HLA2010_PREFLIGHT_MAX_AGE_SECONDS", "60")

    with pytest.raises(pytest.skip.Exception, match="certi preflight not confirmed"):
        require_vendor_preflight("certi", operator_hint="./scripts/certi_easy.sh preflight")
