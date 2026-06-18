"""C++ RTI SDK profile intake and discovery.

C++ intake is profile-based rather than "load any shared object". The profile
describes headers, libraries, compiler options, runtime paths, and factory
strategy so the workspace can build a generated adapter capsule in a later step.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

from hla.rti.intake import IntakeArtifact, IntakeCheck, intake_status_from_checks

from .cpp_capsule_contract import UNSUPPORTED_SERVICE_LEDGER


@dataclass(frozen=True, slots=True)
class CppApiProfile:
    edition: str
    spec_name: str
    cpp_namespace: str
    required_headers: tuple[str, ...]


CPP_2010 = CppApiProfile(
    edition="2010",
    spec_name="rti1516e",
    cpp_namespace="rti1516e",
    required_headers=("RTI/RTIambassador.h", "RTI1516/RTIambassador.h", "rti1516e/RTIambassador.h"),
)
CPP_2025 = CppApiProfile(
    edition="2025",
    spec_name="rti1516_2025",
    cpp_namespace="rti1516_2025",
    required_headers=("RTI/RTIambassador.h", "RTI1516_2025/RTIambassador.h", "rti1516_2025/RTIambassador.h"),
)

CPP_API_PROFILES = {
    "2010": CPP_2010,
    "rti1516e": CPP_2010,
    "1516e": CPP_2010,
    "2025": CPP_2025,
    "rti1516_2025": CPP_2025,
    "rti1516-2025": CPP_2025,
}


@dataclass(frozen=True, slots=True)
class CppSdkFactoryProfile:
    strategy: str = "standard"
    options: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CppSdkIntakeProfile:
    kind: str
    edition: str
    name: str
    include_dirs: tuple[str, ...] = ()
    library_dirs: tuple[str, ...] = ()
    libraries: tuple[str, ...] = ()
    defines: tuple[str, ...] = ()
    cxx_standard: str = "14"
    runtime_env: dict[str, str] = field(default_factory=dict)
    factory: CppSdkFactoryProfile = field(default_factory=CppSdkFactoryProfile)
    adapter: dict[str, str] = field(default_factory=dict)
    headers: tuple[str, ...] = ()

    def to_json_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["artifact"] = IntakeArtifact(kind="cpp-sdk", name=self.name, edition=cpp_api_profile(self.edition).edition).to_json_dict()
        return payload


@dataclass(frozen=True, slots=True)
class CppSdkIntakeRequest:
    profile_path: str
    transport: str = "grpc"
    build_dir: str | None = None
    timeout_seconds: float = 30.0


@dataclass(frozen=True, slots=True)
class CppSdkIntakeReport:
    artifact: dict[str, Any]
    profile_path: str
    transport: str
    edition: str
    route: str
    status: str
    checks: tuple[dict[str, Any], ...]
    profile: dict[str, Any] | None = None
    capsule_dir: str | None = None
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


def cpp_api_profile(edition: str) -> CppApiProfile:
    key = edition.strip().lower().replace("-", "_")
    try:
        return CPP_API_PROFILES[key]
    except KeyError as exc:
        raise ValueError("C++ RTI edition must be one of: 2010, 2025") from exc


def _strip_comment(line: str) -> str:
    in_quote = False
    quote_char = ""
    for index, char in enumerate(line):
        if char in {"'", '"'} and (index == 0 or line[index - 1] != "\\"):
            if in_quote and char == quote_char:
                in_quote = False
            elif not in_quote:
                in_quote = True
                quote_char = char
        if char == "#" and not in_quote:
            return line[:index]
    return line


def _coerce_scalar(value: str) -> Any:
    text = value.strip()
    if not text:
        return ""
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        return [_coerce_scalar(part) for part in inner.split(",")]
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        return text[1:-1]
    if text.lower() in {"true", "false"}:
        return text.lower() == "true"
    return text


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Parse the profile subset used by the workspace examples without a YAML dependency."""

    data: dict[str, Any] = {}
    current_key: str | None = None
    current_map_key: str | None = None
    for raw_line in text.splitlines():
        line = _strip_comment(raw_line).rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if indent == 0:
            current_map_key = None
            if ":" not in stripped:
                raise ValueError(f"Invalid profile line: {raw_line}")
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            current_key = key
            if value:
                data[key] = _coerce_scalar(value)
            else:
                data[key] = {}
                current_map_key = key
            continue
        if current_key is None:
            raise ValueError(f"Invalid indented profile line: {raw_line}")
        if stripped.startswith("- "):
            if not isinstance(data.get(current_key), list):
                data[current_key] = []
            data[current_key].append(_coerce_scalar(stripped[2:]))
            continue
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            if not isinstance(data.get(current_key), dict):
                data[current_key] = {}
            data[current_key][key.strip()] = _coerce_scalar(value)
            current_map_key = current_key
            continue
        raise ValueError(f"Invalid profile line: {raw_line}")
    return data


def _load_profile_mapping(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        payload = json.loads(text)
    else:
        try:
            import yaml  # type: ignore

            payload = yaml.safe_load(text)
        except ModuleNotFoundError:
            payload = _parse_simple_yaml(text)
    if not isinstance(payload, dict):
        raise ValueError("C++ SDK profile must be a mapping")
    return payload


def _tuple_of_strings(payload: dict[str, Any], key: str) -> tuple[str, ...]:
    value = payload.get(key, ())
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Iterable):
        return tuple(str(item) for item in value if str(item))
    raise ValueError(f"{key} must be a string or list of strings")


def load_cpp_sdk_profile(path: str | Path) -> CppSdkIntakeProfile:
    profile_path = Path(path).expanduser()
    if not profile_path.exists():
        raise FileNotFoundError(f"C++ SDK profile does not exist: {profile_path}")
    payload = _load_profile_mapping(profile_path)
    kind = str(payload.get("kind", ""))
    if kind != "cpp-sdk":
        raise ValueError("C++ SDK profile kind must be 'cpp-sdk'")
    edition = str(payload.get("edition", ""))
    api_profile = cpp_api_profile(edition)
    name = str(payload.get("name", "")).strip()
    if not name:
        raise ValueError("C++ SDK profile requires a non-empty name")
    factory_payload = payload.get("factory") or {}
    if not isinstance(factory_payload, dict):
        raise ValueError("factory must be a mapping")
    runtime_env = payload.get("runtime_env") or {}
    if not isinstance(runtime_env, dict):
        raise ValueError("runtime_env must be a mapping")
    return CppSdkIntakeProfile(
        kind=kind,
        edition=api_profile.edition,
        name=name,
        include_dirs=_tuple_of_strings(payload, "include_dirs"),
        library_dirs=_tuple_of_strings(payload, "library_dirs"),
        libraries=_tuple_of_strings(payload, "libraries"),
        defines=_tuple_of_strings(payload, "defines"),
        cxx_standard=str(payload.get("cxx_standard", "14")),
        runtime_env={str(key): str(value) for key, value in runtime_env.items()},
        factory=CppSdkFactoryProfile(
            strategy=str(factory_payload.get("strategy", "standard")),
            options={str(key): str(value) for key, value in factory_payload.items() if key != "strategy"},
        ),
        adapter={str(key): str(value) for key, value in (payload.get("adapter") or {}).items()} if isinstance(payload.get("adapter") or {}, dict) else {},
        headers=_tuple_of_strings(payload, "headers"),
    )


def _check_paths(name: str, paths: Sequence[str]) -> IntakeCheck:
    missing = [str(Path(item).expanduser()) for item in paths if not Path(item).expanduser().exists()]
    if missing:
        return IntakeCheck(name=name, status="fail", message=f"Missing path(s): {', '.join(missing)}", details={"missing": missing})
    return IntakeCheck(name=name, status="profile-valid", message="all paths exist", details={"paths": tuple(paths)})


def _find_header(include_dirs: Sequence[str], headers: Sequence[str]) -> str | None:
    for include_dir in include_dirs:
        base = Path(include_dir).expanduser()
        for header in headers:
            candidate = base / header
            if candidate.exists():
                return str(candidate)
    return None


def _library_candidates(library: str) -> tuple[str, ...]:
    if library.startswith("lib") and Path(library).suffix:
        return (library,)
    return (f"lib{library}.so", f"lib{library}.dylib", f"lib{library}.a", f"{library}.lib")


def _find_library(library_dirs: Sequence[str], library: str) -> str | None:
    explicit = Path(library).expanduser()
    if explicit.exists():
        return str(explicit)
    for library_dir in library_dirs:
        base = Path(library_dir).expanduser()
        for candidate_name in _library_candidates(library):
            candidate = base / candidate_name
            if candidate.exists():
                return str(candidate)
    return None


def _slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower() or "cpp-sdk"


def discover_cpp_sdk(request: CppSdkIntakeRequest) -> CppSdkIntakeReport:
    profile_path = Path(request.profile_path).expanduser()
    checks: list[IntakeCheck] = []
    warnings: list[str] = []
    try:
        profile = load_cpp_sdk_profile(profile_path)
    except Exception as exc:
        artifact = IntakeArtifact(kind="cpp-sdk", name=profile_path.stem or "cpp-sdk", edition="unknown", route=None)
        check = IntakeCheck(name="profile", status="fail", message=str(exc))
        return CppSdkIntakeReport(
            artifact=artifact.to_json_dict(),
            profile_path=str(profile_path),
            transport=request.transport,
            edition="unknown",
            route=f"cpp-unknown-sdk-{request.transport}",
            status="failed",
            checks=(check.to_json_dict(),),
            errors=(str(exc),),
        )

    api_profile = cpp_api_profile(profile.edition)
    route = f"cpp-{api_profile.edition}-sdk-{request.transport}"
    artifact = IntakeArtifact(kind="cpp-sdk", name=profile.name, edition=api_profile.edition, route=route)
    checks.append(IntakeCheck(name="profile", status="profile-valid", message="profile parsed", details={"factory_strategy": profile.factory.strategy}))
    checks.append(_check_paths("include_dirs", profile.include_dirs))
    checks.append(_check_paths("library_dirs", profile.library_dirs))

    headers = profile.headers or api_profile.required_headers
    found_header = _find_header(profile.include_dirs, headers)
    if found_header is None:
        checks.append(
            IntakeCheck(
                name="headers",
                status="fail",
                message="No standard RTIambassador header found in include_dirs",
                details={"required_headers": tuple(headers)},
            )
        )
    else:
        checks.append(IntakeCheck(name="headers", status="header-green", message="standard C++ header found", details={"header": found_header}))

    found_libraries: list[str] = []
    missing_libraries: list[str] = []
    for library in profile.libraries:
        found = _find_library(profile.library_dirs, library)
        if found is None:
            missing_libraries.append(library)
        else:
            found_libraries.append(found)
    if profile.libraries and not missing_libraries:
        checks.append(IntakeCheck(name="libraries", status="link-green", message="declared libraries found", details={"libraries": tuple(found_libraries)}))
    elif missing_libraries:
        checks.append(IntakeCheck(name="libraries", status="fail", message=f"Missing library target(s): {', '.join(missing_libraries)}"))
    else:
        warnings.append("No libraries declared; link probe is pending until profile includes libraries.")
        checks.append(IntakeCheck(name="libraries", status="profile-valid", message="no libraries declared"))

    status = intake_status_from_checks(tuple(checks))
    errors = tuple(check.message or check.name for check in checks if check.status in {"fail", "failed"})
    if errors:
        status = "failed"
    return CppSdkIntakeReport(
        artifact=artifact.to_json_dict(),
        profile_path=str(profile_path),
        transport=request.transport,
        edition=api_profile.edition,
        route=route,
        status=status,
        checks=tuple(check.to_json_dict() for check in checks),
        profile=profile.to_json_dict(),
        errors=errors,
        warnings=tuple(warnings),
    )


def render_cpp_intake_markdown(report: CppSdkIntakeReport) -> str:
    lines = [
        f"# C++ SDK Intake: {report.artifact.get('name')}",
        "",
        f"- Status: `{report.status}`",
        f"- Edition: `{report.edition}`",
        f"- Route: `{report.route}`",
        f"- Transport: `{report.transport}`",
        f"- Profile: `{report.profile_path}`",
        "",
        "## Checks",
        "",
    ]
    for check in report.checks:
        status = str(check.get("status", ""))
        verdict = "PASS" if status.endswith("-green") or status == "profile-valid" else status.upper()
        lines.append(f"- {check.get('name')}: {verdict} - {check.get('message') or ''}")
    lines.extend(["", "## Errors", ""])
    lines.extend(f"- {item}" for item in report.errors)
    if not report.errors:
        lines.append("- none")
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- {item}" for item in report.warnings)
    if not report.warnings:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def report_slug(report: CppSdkIntakeReport) -> str:
    return f"{_slug(str(report.artifact.get('name') or 'cpp-sdk'))}-{report.edition}-{report.transport}"


def _cmake_list(items: Sequence[str]) -> str:
    if not items:
        return ""
    return "\n".join(f'  "{Path(item).expanduser().resolve()}"' for item in items)


def _cmake_value_list(items: Sequence[str]) -> str:
    if not items:
        return ""
    return "\n".join(f'  "{item}"' for item in items)


def _render_capsule_cmake(profile: CppSdkIntakeProfile, report: CppSdkIntakeReport) -> str:
    target = f"_{_slug(profile.name).replace('-', '_')}_capsule"
    libraries = " ".join(profile.libraries)
    return "\n".join(
        [
            "cmake_minimum_required(VERSION 3.18)",
            f"project({target} LANGUAGES CXX)",
            "",
            f"set(CMAKE_CXX_STANDARD {profile.cxx_standard})",
            "set(CMAKE_CXX_STANDARD_REQUIRED ON)",
            f"set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${{CMAKE_BINARY_DIR}}/lib)",
            f"set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${{CMAKE_BINARY_DIR}}/bin)",
            "",
            f"add_library({target} SHARED",
            "  generated/shim_routes_cpp_intake_capsule.cpp",
            ")",
            "",
            f"target_include_directories({target} PRIVATE",
            _cmake_list(profile.include_dirs),
            ")",
            f"target_link_directories({target} PRIVATE",
            _cmake_list(profile.library_dirs),
            ")",
            f"target_compile_definitions({target} PRIVATE",
            _cmake_value_list(profile.defines),
            ")",
            f"target_link_libraries({target} PRIVATE {libraries})",
            "",
            f"# Language-shim route: {report.route}",
            f"# Factory strategy: {profile.factory.strategy}",
            "",
        ]
    )


def _render_capsule_header(profile: CppSdkIntakeProfile) -> str:
    return "\n".join(
        [
            "#pragma once",
            "",
            "#include <string>",
            "",
            "namespace shim_routes {",
            "namespace cpp_intake {",
            "",
            "struct DiscoveryResult {",
            "  bool profile_ready;",
            "  const char* edition;",
            "  const char* sdk_name;",
            "  const char* factory_strategy;",
            "};",
            "",
            "DiscoveryResult discover();",
            "const char* capsule_discover_json(const char* request_json);",
            "const char* capsule_create_json(const char* request_json);",
            "const char* capsule_invoke_json(const char* request_json);",
            "const char* capsule_evoke_callbacks_json(const char* request_json);",
            "void capsule_free_string(const char* value);",
            "void capsule_close();",
            "",
            f"// SDK namespace hint: {cpp_api_profile(profile.edition).cpp_namespace}",
            "",
            "}  // namespace cpp_intake",
            "}  // namespace shim_routes",
            "",
        ]
    )


def _render_capsule_source(profile: CppSdkIntakeProfile) -> str:
    header = (profile.headers or cpp_api_profile(profile.edition).required_headers)[0]
    adapter_strategy = profile.adapter.get("strategy", "probe-only")
    unsupported = ",".join(f'\\"{service}\\"' for service in UNSUPPORTED_SERVICE_LEDGER)
    return "\n".join(
        [
            '#include "shim_routes_cpp_intake_capsule.hpp"',
            "",
            f"#include <{header}>",
            "#include <cstdlib>",
            "#include <cstring>",
            "#include <string>",
            "",
            "namespace shim_routes {",
            "namespace cpp_intake {",
            "namespace {",
            "bool created = false;",
            "bool connected = false;",
            "int invocation_count = 0;",
            "int callback_count = 0;",
            "",
            "const char* duplicate_json(const std::string& payload) {",
            "  char* copy = static_cast<char*>(std::malloc(payload.size() + 1));",
            "  if (copy == nullptr) {",
            "    return nullptr;",
            "  }",
            "  std::memcpy(copy, payload.c_str(), payload.size() + 1);",
            "  return copy;",
            "}",
            "",
            "bool contains(const char* text, const char* needle) {",
            "  return text != nullptr && std::strstr(text, needle) != nullptr;",
            "}",
            "}  // namespace",
            "",
            "DiscoveryResult discover() {",
            "  return DiscoveryResult{",
            "      true,",
            f'      "{profile.edition}",',
            f'      "{profile.name}",',
            f'      "{profile.factory.strategy}",',
            "  };",
            "}",
            "",
            "const char* capsule_discover_json(const char*) {",
            "  std::string payload = \"{\\\"ok\\\":true,\\\"kind\\\":\\\"shim_routes_cpp_capsule\\\",\\\"contract\\\":\\\"shim_capsule_v1\\\",\\\"edition\\\":\\\"\";",
            f"  payload += \"{profile.edition}\";",
            "  payload += \"\\\",\\\"sdk_name\\\":\\\"\";",
            f"  payload += \"{profile.name}\";",
            "  payload += \"\\\",\\\"adapter_strategy\\\":\\\"\";",
            f"  payload += \"{adapter_strategy}\";",
            "  payload += \"\\\",\\\"unsupported_services\\\":[\";",
            f"  payload += \"{unsupported}\";",
            "  payload += \"]}\";",
            "  return duplicate_json(payload);",
            "}",
            "",
            "const char* capsule_create_json(const char*) {",
            "  created = true;",
            "  return duplicate_json(\"{\\\"ok\\\":true,\\\"session_id\\\":\\\"capsule-session-1\\\",\\\"ambassador\\\":\\\"shim_capsule_v1\\\"}\");",
            "}",
            "",
            "const char* capsule_invoke_json(const char* request_json) {",
            "  invocation_count += 1;",
            "  if (contains(request_json, \"disconnect\")) {",
            "    connected = false;",
            "    return duplicate_json(\"{\\\"ok\\\":true,\\\"method\\\":\\\"disconnect\\\"}\");",
            "  }",
            "  if (contains(request_json, \"connect\")) {",
            "    if (!created) {",
            "      return duplicate_json(\"{\\\"ok\\\":false,\\\"error_type\\\":\\\"NoAmbassador\\\",\\\"message\\\":\\\"create_rti_ambassador must be called before connect\\\"}\");",
            "    }",
            "    connected = true;",
            "    return duplicate_json(\"{\\\"ok\\\":true,\\\"method\\\":\\\"connect\\\"}\");",
            "  }",
            "  return duplicate_json(\"{\\\"ok\\\":false,\\\"error_type\\\":\\\"UnsupportedService\\\",\\\"message\\\":\\\"requestFederationSave is not implemented by this capsule\\\",\\\"method\\\":\\\"requestFederationSave\\\"}\");",
            "}",
            "",
            "const char* capsule_evoke_callbacks_json(const char*) {",
            "  callback_count += 1;",
            "  if (callback_count == 1) {",
            "    return duplicate_json(\"{\\\"ok\\\":true,\\\"events\\\":[{\\\"event\\\":\\\"capsuleCallbackPoll\\\",\\\"label\\\":\\\"adapter-smoke\\\"}],\\\"callback_count\\\":1}\");",
            "  }",
            "  return duplicate_json(\"{\\\"ok\\\":true,\\\"events\\\":[],\\\"callback_count\\\":0}\");",
            "}",
            "",
            "void capsule_free_string(const char* value) {",
            "  std::free(const_cast<char*>(value));",
            "}",
            "",
            "void capsule_close() {",
            "  created = false;",
            "  connected = false;",
            "}",
            "",
            "}  // namespace cpp_intake",
            "}  // namespace shim_routes",
            "",
            "extern \"C\" const char* shim_capsule_discover_json(const char* request_json) {",
            "  return shim_routes::cpp_intake::capsule_discover_json(request_json);",
            "}",
            "",
            "extern \"C\" const char* shim_capsule_create_json(const char* request_json) {",
            "  return shim_routes::cpp_intake::capsule_create_json(request_json);",
            "}",
            "",
            "extern \"C\" const char* shim_capsule_invoke_json(const char* request_json) {",
            "  return shim_routes::cpp_intake::capsule_invoke_json(request_json);",
            "}",
            "",
            "extern \"C\" const char* shim_capsule_evoke_callbacks_json(const char* request_json) {",
            "  return shim_routes::cpp_intake::capsule_evoke_callbacks_json(request_json);",
            "}",
            "",
            "extern \"C\" void shim_capsule_free_string(const char* value) {",
            "  shim_routes::cpp_intake::capsule_free_string(value);",
            "}",
            "",
            "extern \"C\" void shim_capsule_close() {",
            "  shim_routes::cpp_intake::capsule_close();",
            "}",
            "",
        ]
    )


def _run_cmake_capsule_build(capsule_root: Path, timeout_seconds: float) -> tuple[tuple[IntakeCheck, ...], tuple[str, ...]]:
    cmake = shutil.which("cmake")
    if cmake is None:
        message = "cmake is required to compile a C++ SDK intake capsule"
        return (IntakeCheck(name="capsule_configure", status="fail", message=message),), (message,)
    build_dir = capsule_root / "build"
    configure = subprocess.run(
        [cmake, "-S", str(capsule_root), "-B", str(build_dir)],
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    if configure.returncode != 0:
        message = "CMake configure failed"
        return (
            IntakeCheck(
                name="capsule_configure",
                status="fail",
                message=message,
                details={"stdout": configure.stdout[-4000:], "stderr": configure.stderr[-4000:]},
            ),
        ), (message,)
    build = subprocess.run(
        [cmake, "--build", str(build_dir)],
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    if build.returncode != 0:
        message = "C++ capsule compile/link failed"
        return (
            IntakeCheck(name="capsule_configure", status="compile-green", message="CMake configured capsule project"),
            IntakeCheck(
                name="capsule_build",
                status="fail",
                message=message,
                details={"stdout": build.stdout[-4000:], "stderr": build.stderr[-4000:]},
            ),
        ), (message,)
    return (
        IntakeCheck(name="capsule_configure", status="compile-green", message="CMake configured capsule project"),
        IntakeCheck(name="capsule_build", status="capsule-built", message="C++ capsule compiled and linked"),
    ), ()


def generate_cpp_sdk_capsule(request: CppSdkIntakeRequest, output_root: str | Path) -> CppSdkIntakeReport:
    report = discover_cpp_sdk(request)
    if report.errors:
        return report
    profile = load_cpp_sdk_profile(request.profile_path)
    capsule_root = Path(output_root).expanduser() / _slug(profile.name)
    generated = capsule_root / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    (capsule_root / "CMakeLists.txt").write_text(_render_capsule_cmake(profile, report), encoding="utf-8")
    (generated / "shim_routes_cpp_intake_capsule.hpp").write_text(_render_capsule_header(profile), encoding="utf-8")
    (generated / "shim_routes_cpp_intake_capsule.cpp").write_text(_render_capsule_source(profile), encoding="utf-8")
    build_checks, build_errors = _run_cmake_capsule_build(capsule_root, request.timeout_seconds)
    checks = tuple(report.checks) + tuple(check.to_json_dict() for check in build_checks)
    errors = tuple(report.errors) + build_errors
    status = "failed" if errors else intake_status_from_checks(tuple(IntakeCheck(**check) for check in checks))
    return CppSdkIntakeReport(
        artifact=report.artifact,
        profile_path=report.profile_path,
        transport=report.transport,
        edition=report.edition,
        route=report.route,
        status=status,
        checks=checks,
        profile=report.profile,
        capsule_dir=str(capsule_root),
        errors=errors,
        warnings=report.warnings,
    )


def write_cpp_intake_reports(report: CppSdkIntakeReport, output_dir: str | Path) -> tuple[Path, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    slug = report_slug(report)
    json_path = output / f"{slug}.json"
    md_path = output / f"{slug}.md"
    json_path.write_text(json.dumps(report.to_json_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_cpp_intake_markdown(report), encoding="utf-8")
    return json_path, md_path


__all__ = [
    "CPP_2010",
    "CPP_2025",
    "CppApiProfile",
    "CppSdkFactoryProfile",
    "CppSdkIntakeProfile",
    "CppSdkIntakeReport",
    "CppSdkIntakeRequest",
    "cpp_api_profile",
    "discover_cpp_sdk",
    "generate_cpp_sdk_capsule",
    "load_cpp_sdk_profile",
    "render_cpp_intake_markdown",
    "write_cpp_intake_reports",
]
