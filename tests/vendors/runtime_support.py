from __future__ import annotations

import socket
from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass
from typing import Any, Iterator, Sequence

from hla2010.enums import ResignAction


@dataclass
class ReservedUDPPorts(AbstractContextManager["ReservedUDPPorts"]):
    host: str
    ports: tuple[int, ...]
    _sockets: tuple[socket.socket, ...]

    def close(self) -> None:
        for sock in self._sockets:
            try:
                sock.close()
            except OSError:
                pass
        self._sockets = ()

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
        return None


def reserve_udp_ports(count: int, *, host: str = "127.0.0.1") -> ReservedUDPPorts:
    sockets: list[socket.socket] = []
    ports: list[int] = []
    try:
        for _ in range(count):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((host, 0))
            sockets.append(sock)
            ports.append(int(sock.getsockname()[1]))
    except Exception:
        for sock in sockets:
            try:
                sock.close()
            except OSError:
                pass
        raise
    return ReservedUDPPorts(host=host, ports=tuple(ports), _sockets=tuple(sockets))


def reserve_udp_pair(*, host: str = "127.0.0.1") -> ReservedUDPPorts:
    return reserve_udp_ports(2, host=host)


@contextmanager
def udp_port_pair(udp_base: int | None = None, *, host: str = "127.0.0.1") -> Iterator[tuple[int, int]]:
    if udp_base is not None:
        yield (udp_base, udp_base + 1)
        return
    with reserve_udp_pair(host=host) as lease:
        yield (lease.ports[0], lease.ports[1])


def cleanup_federation(
    federation_name: str,
    *,
    destroyer: Any | None = None,
    destroyer_resign_action: ResignAction | None = None,
    remaining_resignations: Sequence[tuple[Any | None, ResignAction]] = (),
    disconnect_rtis: Sequence[Any | None] = (),
) -> None:
    if destroyer is not None and destroyer_resign_action is not None:
        try:
            destroyer.resign_federation_execution(destroyer_resign_action)
        except BaseException:
            pass
    for rti, action in remaining_resignations:
        if rti is None:
            continue
        try:
            rti.resign_federation_execution(action)
        except BaseException:
            pass
    if destroyer is not None:
        try:
            destroyer.destroy_federation_execution(federation_name)
        except BaseException:
            pass
    for rti in disconnect_rtis:
        if rti is None:
            continue
        try:
            rti.disconnect()
        except BaseException:
            pass


def close_all(*resources: Any | None) -> None:
    for resource in resources:
        if resource is None:
            continue
        try:
            resource.close()
        except BaseException:
            pass


def terminate_all(*resources: Any | None) -> None:
    for resource in resources:
        if resource is None:
            continue
        try:
            resource.terminate()
        except BaseException:
            pass
