#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
import threading
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

_TEST_REF_RE = re.compile(r"tests[^ :\n]+\.py(?:::[^ \n]+)?")


def _usage() -> str:
    return "\n".join(
        [
            "test.py: run pytest for the full suite or the selected paths.",
            "Evidence:",
            "- python -m pytest -q",
            "- use `-x` to stop at the first failure",
            "- on failure, this wrapper emits narrow rerun hints when it can identify a test node",
        ]
    )


def _extract_first_reference(output: str) -> tuple[str, str]:
    match = _TEST_REF_RE.search(output)
    if not match:
        return ("", "")
    node = match.group(0)
    file_path = node.split("::", 1)[0]
    return (node, file_path)


def _emit_rerun_hints(output: str) -> None:
    node, file_path = _extract_first_reference(output)
    print("\nrerun hints:", file=sys.stderr)
    if node:
        print(f"- narrowest node: ./tools/test {node}", file=sys.stderr)
    if file_path and file_path != node:
        print(f"- owning file: ./tools/test {file_path}", file=sys.stderr)
    elif file_path:
        print(f"- owning file: ./tools/test {file_path}", file=sys.stderr)
    print("- failed-first retry: ./tools/test --lf", file=sys.stderr)
    print("- stop after first failure: ./tools/test -x", file=sys.stderr)
    print("- focused target discovery: ./tools/test-focus inventory", file=sys.stderr)


def _stream_pipe(pipe: object, sink: object, chunks: list[str]) -> None:
    assert hasattr(pipe, "__iter__")
    assert hasattr(sink, "write")
    for chunk in pipe:  # type: ignore[assignment]
        text = str(chunk)
        chunks.append(text)
        sink.write(text)  # type: ignore[attr-defined]
        sink.flush()  # type: ignore[attr-defined]


def main(argv: list[str]) -> int:
    args = argv[1:]
    if args and args[0] in {"-h", "--help", "help"}:
        print(_usage())
        return 0

    cmd = [sys.executable, "-m", "pytest", "-q", *args]
    process = subprocess.Popen(
        cmd,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    assert process.stdout is not None
    assert process.stderr is not None

    stdout_chunks: list[str] = []
    stderr_chunks: list[str] = []
    stdout_thread = threading.Thread(
        target=_stream_pipe,
        args=(process.stdout, sys.stdout, stdout_chunks),
        daemon=True,
    )
    stderr_thread = threading.Thread(
        target=_stream_pipe,
        args=(process.stderr, sys.stderr, stderr_chunks),
        daemon=True,
    )
    stdout_thread.start()
    stderr_thread.start()
    process.wait()
    stdout_thread.join()
    stderr_thread.join()

    if process.returncode != 0:
        _emit_rerun_hints(f"{''.join(stdout_chunks)}\n{''.join(stderr_chunks)}")

    return process.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
