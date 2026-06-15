#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
from dataclasses import dataclass
from shutil import which


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve repo-local Pitch host ports.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--preferred-crc-port", type=int, default=8989)
    parser.add_argument("--preferred-fedpro-port", type=int, default=15164)
    parser.add_argument("--docker-container-name", default=os.environ.get("HLA2010_PITCH_DOCKER_NAME", "hla2010-pitch-crc"))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--shell", action="store_true")
    return parser.parse_args(argv)


@dataclass(frozen=True)
class SelectedPort:
    port: int
    source: str
    preferred_port: int


def _try_bind(host: str, port: int) -> socket.socket | None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((host, port))
        sock.listen(1)
        return sock
    except OSError:
        sock.close()
        return None


def _reserve_ephemeral(host: str, forbidden: set[int]) -> socket.socket:
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, 0))
        sock.listen(1)
        port = int(sock.getsockname()[1])
        if port not in forbidden:
            return sock
        sock.close()


def _select_port(
    host: str,
    *,
    explicit_env_name: str,
    preferred_port: int,
    forbidden: set[int],
) -> tuple[SelectedPort, socket.socket]:
    explicit_value = os.environ.get(explicit_env_name)
    if explicit_value:
        port = int(explicit_value)
        sock = _try_bind(host, port)
        if sock is None:
            raise SystemExit(f"{explicit_env_name}={port} is already in use on {host}")
        return SelectedPort(port=port, source="explicit", preferred_port=port), sock

    if preferred_port not in forbidden:
        sock = _try_bind(host, preferred_port)
        if sock is not None:
            return (
                SelectedPort(port=preferred_port, source="preferred", preferred_port=preferred_port),
                sock,
            )

    sock = _reserve_ephemeral(host, forbidden)
    return (
        SelectedPort(port=int(sock.getsockname()[1]), source="fallback", preferred_port=preferred_port),
        sock,
    )


def _render_payload(host: str, crc: SelectedPort, fedpro: SelectedPort) -> dict[str, object]:
    return {
        "host": host,
        "crc_port": crc.port,
        "crc_port_source": crc.source,
        "crc_preferred_port": crc.preferred_port,
        "fedpro_port": fedpro.port,
        "fedpro_port_source": fedpro.source,
        "fedpro_preferred_port": fedpro.preferred_port,
    }


def _docker_available() -> bool:
    return which("docker") is not None


def _running_container_host_ports(container_name: str) -> tuple[int, int] | None:
    if not _docker_available():
        return None
    ps = subprocess.run(
        ["docker", "ps", "--filter", f"name=^{container_name}$", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if ps.returncode != 0 or container_name not in ps.stdout.splitlines():
        return None

    def port_for(container_port: int) -> int | None:
        proc = subprocess.run(
            ["docker", "port", container_name, f"{container_port}/tcp"],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            return None
        for raw in proc.stdout.splitlines():
            text = raw.strip()
            if not text:
                continue
            try:
                return int(text.rsplit(":", 1)[1])
            except (IndexError, ValueError):
                continue
        return None

    crc_port = port_for(8989)
    fedpro_port = port_for(15164)
    if crc_port is None or fedpro_port is None:
        return None
    return crc_port, fedpro_port


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    reused = _running_container_host_ports(args.docker_container_name)
    if reused is not None:
        crc = SelectedPort(port=reused[0], source="managed-container", preferred_port=args.preferred_crc_port)
        fedpro = SelectedPort(port=reused[1], source="managed-container", preferred_port=args.preferred_fedpro_port)
        payload = _render_payload(args.host, crc, fedpro)
        if args.json:
            json.dump(payload, sys.stdout, indent=2, sort_keys=True)
            sys.stdout.write("\n")
            return 0
        if args.shell:
            sys.stdout.write(f"export HLA2010_PITCH_CRC_PORT={crc.port}\n")
            sys.stdout.write(f"export HLA2010_PITCH_CRC_PORT_SOURCE={crc.source}\n")
            sys.stdout.write(f"export HLA2010_PITCH_CRC_PREFERRED_PORT={crc.preferred_port}\n")
            sys.stdout.write(f"export HLA2010_PITCH_FEDPRO_PORT={fedpro.port}\n")
            sys.stdout.write(f"export HLA2010_PITCH_FEDPRO_PORT_SOURCE={fedpro.source}\n")
            sys.stdout.write(f"export HLA2010_PITCH_FEDPRO_PREFERRED_PORT={fedpro.preferred_port}\n")
            return 0
        sys.stdout.write(f"{crc.port} {fedpro.port}\n")
        return 0

    crc, crc_sock = _select_port(
        args.host,
        explicit_env_name="HLA2010_PITCH_CRC_PORT",
        preferred_port=args.preferred_crc_port,
        forbidden=set(),
    )
    try:
        fedpro, fedpro_sock = _select_port(
            args.host,
            explicit_env_name="HLA2010_PITCH_FEDPRO_PORT",
            preferred_port=args.preferred_fedpro_port,
            forbidden={crc.port},
        )
    finally:
        pass
    try:
        payload = _render_payload(args.host, crc, fedpro)
        if args.json:
            json.dump(payload, sys.stdout, indent=2, sort_keys=True)
            sys.stdout.write("\n")
            return 0
        if args.shell:
            sys.stdout.write(f"export HLA2010_PITCH_CRC_PORT={crc.port}\n")
            sys.stdout.write(f"export HLA2010_PITCH_CRC_PORT_SOURCE={crc.source}\n")
            sys.stdout.write(f"export HLA2010_PITCH_CRC_PREFERRED_PORT={crc.preferred_port}\n")
            sys.stdout.write(f"export HLA2010_PITCH_FEDPRO_PORT={fedpro.port}\n")
            sys.stdout.write(f"export HLA2010_PITCH_FEDPRO_PORT_SOURCE={fedpro.source}\n")
            sys.stdout.write(f"export HLA2010_PITCH_FEDPRO_PREFERRED_PORT={fedpro.preferred_port}\n")
            return 0
        sys.stdout.write(f"{crc.port} {fedpro.port}\n")
        return 0
    finally:
        crc_sock.close()
        fedpro_sock.close()


if __name__ == "__main__":
    raise SystemExit(main())
