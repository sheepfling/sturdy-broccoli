"""Shared RTI spec, backend registry, and ambassador factory helpers."""
from __future__ import annotations

import importlib
import json
from dataclasses import dataclass, field
from importlib import metadata
from pathlib import Path
from typing import Any, Mapping

from .plugin_api import (
    BACKEND_ENTRY_POINT_GROUP,
    SPEC_ENTRY_POINT_GROUP,
    BackendRequest,
    FactoryComposition,
    HLASpec,
    RTIBackendDiscovery,
    RTIBackendPlugin,
    RTIBackendSpec,
    RTITransportSpec,
    SpecPlugin,
)

_BACKEND_FACTORIES: dict[str, Any] = {}
_BACKEND_PLUGINS: dict[str, RTIBackendPlugin] = {}
_BACKEND_PLUGINS_LOADED = False
_SPEC_PLUGINS: dict[str, SpecPlugin] = {}
_SPEC_PLUGINS_LOADED = False
_SOURCE_CHECKOUT_SPEC_PLUGIN_MODULES: tuple[str, ...] = (
    "hla.rti1516e.plugin",
    "hla.rti1516_2025.plugin",
)
_SOURCE_CHECKOUT_PLUGIN_MODULES: tuple[str, ...] = (
    "hla.backends.inmemory.plugin",
    "hla.backends.python2025.plugin",
    "hla.backends.cpp_shim.plugin",
    "hla.bridges.java.common.java_shim_plugin",
    "hla.bridges.java.jpype.plugin",
    "hla.bridges.java.py4j.plugin",
    "hla.vendors.pitch.jpype.plugin",
    "hla.vendors.pitch.py4j.plugin",
    "hla.vendors.portico.plugin",
    "hla.backends.certi.certi.plugin",
)


@dataclass(frozen=True, slots=True)
class EditionCapabilities:
    spec_name: str
    year: int
    provider: str
    backend_family: str
    capabilities: frozenset[str]
    encoding: str
    auth: str
    fom: str
    notes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class NoAuthProvider:
    """Default permissive auth provider for local and compatibility-wrapper routes."""

    name: str = "none"
    credential_type: str = "HLAnoCredentials"

    def authorize(self, credentials: Any = None, **context: Any) -> bool:
        return True


@dataclass(frozen=True, slots=True)
class CredentialProvider:
    credential_type: str
    credential_data: bytes = field(default=b"", repr=False)
    redacted: str = "<redacted>"

    def get_credentials(self) -> Any:
        if self.credential_type == "legacy-none":
            return None
        if self.credential_type == "HLAnoCredentials":
            auth_module = importlib.import_module("hla.rti1516_2025.auth")
            return auth_module.HLAnoCredentials()
        if self.credential_type == "HLAplainTextPassword":
            auth_module = importlib.import_module("hla.rti1516_2025.auth")
            return auth_module.HLAplainTextPassword(self.credential_data.decode("utf-8"))
        datatypes_module = importlib.import_module("hla.rti1516_2025.datatypes")
        return datatypes_module.Credentials(self.credential_type, self.credential_data)

    def redact(self) -> Mapping[str, str]:
        return {"type": self.credential_type, "data": self.redacted}


@dataclass(frozen=True, slots=True)
class FakeAuthorizerProvider:
    name: str = "fake"
    allow_rti: bool = True
    allowed_federations: frozenset[str] | None = None
    allowed_federate_types: frozenset[str] | None = None
    fail_mode: str | None = None

    def authorize_rti_operation(self, credentials: Any) -> Any:
        return self._decision(credentials, scope="rti")

    def authorize_federation_operation(self, credentials: Any, federation_name: str) -> Any:
        if self.allowed_federations is not None and federation_name not in self.allowed_federations:
            return self._result("UNAUTHORIZED", f"federation {federation_name!r} is not authorized")
        return self._decision(credentials, scope="federation")

    def authorize_federate_operation(
        self,
        credentials: Any,
        federation_name: str,
        federate_name: str,
        federate_type: str,
    ) -> Any:
        if self.allowed_federations is not None and federation_name not in self.allowed_federations:
            return self._result("UNAUTHORIZED", f"federation {federation_name!r} is not authorized")
        if self.allowed_federate_types is not None and federate_type not in self.allowed_federate_types:
            return self._result("UNAUTHORIZED", f"federate type {federate_type!r} is not authorized")
        return self._decision(credentials, scope="federate")

    def capability_report(self) -> Mapping[str, Any]:
        return {
            "name": self.name,
            "available": True,
            "mode": "fake",
            "allow_rti": self.allow_rti,
            "allowed_federations": sorted(self.allowed_federations) if self.allowed_federations is not None else None,
            "allowed_federate_types": sorted(self.allowed_federate_types) if self.allowed_federate_types is not None else None,
            "fail_mode": self.fail_mode,
        }

    def _decision(self, credentials: Any, *, scope: str) -> Any:
        if self.fail_mode == "error":
            return self._result("AUTHORIZATION_ERROR", f"{scope} authorization provider error")
        credential_type = getattr(credentials, "type", "")
        if not credential_type:
            return self._result("INVALID_CREDENTIALS", "Credentials must declare a type")
        if credential_type == "HLAplainTextPassword":
            try:
                password = importlib.import_module("hla.rti1516_2025.auth").HLAplainTextPassword(credentials.data).decode()
            except Exception:
                return self._result("INVALID_CREDENTIALS", "Encoded HLAplainTextPassword is malformed")
            if not password:
                return self._result("INVALID_CREDENTIALS", "HLAplainTextPassword cannot be empty")
            if password == "bad":
                return self._result("INVALID_CREDENTIALS", "Credential provider rejected HLAplainTextPassword")
        if not self.allow_rti:
            return self._result("UNAUTHORIZED", f"{scope} operation is not authorized")
        return self._result("AUTHORIZED")

    @staticmethod
    def _result(code_name: str, message: str = "") -> Any:
        auth_module = importlib.import_module("hla.rti1516_2025.auth")
        enum_module = importlib.import_module("hla.rti1516_2025.enums")
        return auth_module.AuthorizationResult(getattr(enum_module.AuthorizationResultCode, code_name), message)


@dataclass(frozen=True, slots=True)
class EncodingContext:
    edition: str
    provider: str
    transport: str
    registry: Any
    repository: Any = None

    def capability_report(self) -> Mapping[str, Any]:
        registry_report = getattr(self.registry, "capability_report", lambda: {})()
        repository_report = getattr(self.repository, "capability_report", lambda: None)()
        return {
            "edition": self.edition,
            "provider": self.provider,
            "transport": self.transport,
            "registry": registry_report,
            "repository": repository_report,
        }


@dataclass(frozen=True, slots=True)
class AuthenticationContext:
    edition: str
    provider: str
    transport: str
    credential_provider: CredentialProvider
    supports_standard_credentials: bool
    supports_custom_credentials: bool
    supported_custom_credential_types: tuple[str, ...]
    authorizer_provider: Any = None

    def credentials(self) -> Any:
        return self.credential_provider.get_credentials()

    def authorize_connection(self) -> None:
        credentials = self.credentials()
        authorizer = self.authorizer_provider
        if authorizer is not None:
            decision = authorizer.authorize_rti_operation(credentials)
            code_name = getattr(getattr(decision, "code", None), "name", "")
            if code_name == "INVALID_CREDENTIALS":
                exc = importlib.import_module("hla.rti1516_2025.exceptions").InvalidCredentials
                raise exc(getattr(decision, "message", "Invalid credentials"))
            if code_name == "UNAUTHORIZED":
                exc = importlib.import_module("hla.rti1516_2025.exceptions").Unauthorized
                raise exc(getattr(decision, "message", "Unauthorized"))
            if code_name == "AUTHORIZATION_ERROR":
                exc = importlib.import_module("hla.rti1516_2025.exceptions").ConnectionFailed
                raise exc(getattr(decision, "message", "Authorization error"))
        if credentials is None:
            return
        if getattr(credentials, "type", "") == "HLAplainTextPassword":
            password = importlib.import_module("hla.rti1516_2025.auth").HLAplainTextPassword(credentials.data).decode()
            if not password:
                exc = importlib.import_module("hla.rti1516_2025.exceptions").InvalidCredentials
                raise exc("HLAplainTextPassword cannot be empty")
            if password == "bad":
                exc = importlib.import_module("hla.rti1516_2025.exceptions").InvalidCredentials
                raise exc("Credential provider rejected HLAplainTextPassword")

    def capability_report(self) -> Mapping[str, Any]:
        allowed_auth_modes = ["NoAuth"]
        if self.supports_standard_credentials:
            allowed_auth_modes.extend(["PlainTextPassword", "CustomTypedBytes"])
        return {
            "edition": self.edition,
            "provider": self.provider,
            "transport": self.transport,
            "supports_standard_credentials": self.supports_standard_credentials,
            "supports_custom_credentials": self.supports_custom_credentials,
            "supported_custom_credential_types": list(self.supported_custom_credential_types),
            "allowed_auth_modes": allowed_auth_modes,
            "credential_type": self.credential_provider.credential_type,
            "credential": self.credential_provider.redact(),
            "authorizer_provider": (
                self.authorizer_provider.capability_report()
                if self.authorizer_provider is not None and hasattr(self.authorizer_provider, "capability_report")
                else None
            ),
        }


@dataclass(frozen=True, slots=True)
class FomLoadResult:
    modules: tuple[Any, ...]
    codecs: Any
    repository: Any = None
    status: str = "loaded"
    diagnostics: tuple[str, ...] = ()
    validation_issues: tuple[Mapping[str, Any], ...] = ()
    strict_identification: bool = False

    def capability_report(self) -> Mapping[str, Any]:
        return {
            "status": self.status,
            "strict_identification": self.strict_identification,
            "diagnostics": list(self.diagnostics),
            "validation_issues": list(self.validation_issues),
        }


@dataclass(slots=True)
class HlaRuntimeContext:
    edition: str
    provider: str
    transport: str
    rti_ambassador: Any
    federate_ambassador: Any
    encoding_context: EncodingContext
    authentication_context: AuthenticationContext
    callback_model: Any
    fom_load_result: FomLoadResult | None = None

    def capability_report(self) -> Mapping[str, Any]:
        report = {
            "edition": self.edition,
            "provider": self.provider,
            "transport": self.transport,
            "encoding": self.encoding_context.capability_report(),
            "auth": self.authentication_context.capability_report(),
        }
        if self.fom_load_result is not None:
            report["fom"] = self.fom_load_result.capability_report()
        return report

    def connect(self, configuration: Any = None) -> Any:
        self.authentication_context.authorize_connection()
        return self.rti_ambassador.connect(
            self.federate_ambassador,
            self.callback_model,
            configuration=configuration,
            credentials=self.authentication_context.credentials(),
        )

    def write_evidence(self, output_dir: str | Path) -> Mapping[str, str]:
        directory = Path(output_dir)
        directory.mkdir(parents=True, exist_ok=True)
        artifacts = {
            "encoding_capabilities": directory / "encoding_capabilities.json",
            "auth_capabilities": directory / "auth_capabilities.json",
            "runtime_matrix": directory / "runtime_matrix.json",
        }
        if self.fom_load_result is not None:
            artifacts["fom_validation"] = directory / "fom_validation.json"
        artifacts["encoding_capabilities"].write_text(
            json.dumps(self.encoding_context.capability_report(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        artifacts["auth_capabilities"].write_text(
            json.dumps(self.authentication_context.capability_report(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        artifacts["runtime_matrix"].write_text(
            json.dumps(self.capability_report(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        if self.fom_load_result is not None:
            artifacts["fom_validation"].write_text(
                json.dumps(self.fom_load_result.capability_report(), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        return {key: str(path) for key, path in artifacts.items()}


@dataclass(slots=True)
class HlaFactory:
    spec: HLASpec
    provider: str
    options: Mapping[str, Any] = field(default_factory=dict)

    def create_rti_ambassador(self, **options: Any) -> Any:
        merged = dict(self.options)
        merged.update(options)
        # Composition-layer helpers such as auth belong to the factory/runtime
        # context, not the backend constructor surface.
        for key in ("auth", "auth_provider", "encoding_registry"):
            merged.pop(key, None)
        composition = self._composition()
        merged.setdefault("factory_composition", composition)
        return create_rti_ambassador(spec=self.spec, backend=self.provider, **merged)

    def create_federate_ambassador_proxy(self, ambassador: Any = None, **options: Any) -> Any:
        if ambassador is not None:
            return ambassador
        spec_package = importlib.import_module(self.spec.python_package)
        null_ambassador = getattr(spec_package, "NullFederateAmbassador", None)
        if null_ambassador is None:
            null_ambassador = getattr(importlib.import_module(f"{self.spec.python_package}.federate_ambassador"), "NullFederateAmbassador", None)
        if null_ambassador is None:
            raise ValueError(f"HLA spec {self.spec.name!r} does not expose a null federate ambassador proxy")
        return null_ambassador()

    def encoding_registry(self) -> Any:
        if self.spec.name == "rti1516_2025":
            return importlib.import_module("hla.rti1516_2025").create_encoder_factory()
        if self.spec.name == "rti1516e":
            return importlib.import_module("hla.rti1516e.encoding")
        raise ValueError(f"No encoding registry is registered for HLA spec {self.spec.name!r}")

    def auth_provider(self, config: Any = None) -> Any:
        config = config or {}
        mode = config.get("mode") if isinstance(config, Mapping) else getattr(config, "mode", None)
        if mode in {"PlainTextPassword", "CustomTypedBytes"} and self.spec.name != "rti1516_2025":
            raise ValueError("Standard credentials are unsupported for the 1516e-2010 profile")
        if self.spec.name == "rti1516_2025":
            return NoAuthProvider()
        return NoAuthProvider(credential_type="legacy-none")

    def create_encoding_context(self, *, transport: str = "inproc", fom_modules: Any = None) -> EncodingContext:
        repository = None
        if self.spec.name == "rti1516_2025":
            foms = importlib.import_module("hla.rti1516_2025.foms")
            repository = (
                foms.FomTypeRepository.empty()
                if fom_modules is None
                else foms.FomTypeRepository.from_modules(fom_modules)
            )
        return EncodingContext(
            edition=self.spec.name,
            provider=self.provider,
            transport=transport,
            registry=self.encoding_registry(),
            repository=repository,
        )

    def create_authentication_context(self, config: Any = None, *, transport: str = "inproc") -> AuthenticationContext:
        mode = _auth_config_value(config, "mode", "NoAuth")
        supports_standard = self.spec.name == "rti1516_2025"
        supports_custom_credentials = supports_standard and self.provider == "python2025"
        supported_custom_credential_types = tuple(_auth_config_value(config, "supported_custom_credential_types", ()))
        if mode != "NoAuth" and not supports_standard:
            raise ValueError("Standard credentials are unsupported for the 1516e-2010 profile")
        if mode == "NoAuth":
            credential_type = "HLAnoCredentials" if supports_standard else "legacy-none"
            provider = CredentialProvider(credential_type, redacted="<no credentials>")
        elif mode == "PlainTextPassword":
            password = str(_auth_config_value(config, "password", ""))
            if not password:
                exc = importlib.import_module("hla.rti1516_2025.exceptions").InvalidCredentials
                raise exc("HLAplainTextPassword cannot be empty")
            provider = CredentialProvider(
                "HLAplainTextPassword",
                password.encode("utf-8"),
                redacted="<redacted:HLAplainTextPassword>",
            )
        elif mode == "CustomTypedBytes":
            credential_type = str(_auth_config_value(config, "credential_type", ""))
            if not credential_type:
                raise ValueError("CustomTypedBytes auth requires credential_type")
            if not supports_custom_credentials:
                exc = importlib.import_module("hla.rti1516_2025.exceptions").InvalidCredentials
                raise exc(f"Provider {self.provider!r} does not advertise custom credential support")
            if supported_custom_credential_types and credential_type not in supported_custom_credential_types:
                exc = importlib.import_module("hla.rti1516_2025.exceptions").InvalidCredentials
                raise exc(f"Credential type {credential_type!r} is not advertised by provider {self.provider!r}")
            data = _auth_config_value(config, "data", b"")
            provider = CredentialProvider(
                credential_type,
                bytes(data),
                redacted=f"<redacted:{credential_type}>",
            )
        else:
            raise ValueError(f"Unsupported auth mode: {mode!r}")
        authorizer_provider = None
        authorizer_mode = _auth_config_value(config, "authorizer_mode", None)
        if authorizer_mode is not None:
            if not (supports_standard and self.provider == "python2025"):
                raise ValueError("Authorizer providers are available only for the 2025 python2025 RTI provider")
            if authorizer_mode != "Fake":
                raise ValueError(f"Unsupported authorizer mode: {authorizer_mode!r}")
            allowed_federations = _auth_config_value(config, "allowed_federations", None)
            allowed_federate_types = _auth_config_value(config, "allowed_federate_types", None)
            authorizer_provider = FakeAuthorizerProvider(
                allow_rti=bool(_auth_config_value(config, "allow_rti", True)),
                allowed_federations=(
                    frozenset(str(item) for item in allowed_federations)
                    if allowed_federations is not None
                    else None
                ),
                allowed_federate_types=(
                    frozenset(str(item) for item in allowed_federate_types)
                    if allowed_federate_types is not None
                    else None
                ),
                fail_mode=_auth_config_value(config, "fail_mode", None),
            )
        return AuthenticationContext(
            edition=self.spec.name,
            provider=self.provider,
            transport=transport,
            credential_provider=provider,
            supports_standard_credentials=supports_standard,
            supports_custom_credentials=supports_custom_credentials,
            supported_custom_credential_types=supported_custom_credential_types,
            authorizer_provider=authorizer_provider,
        )

    def create_runtime_context(
        self,
        *,
        auth_config: Any = None,
        transport: str = "inproc",
        callback_model: Any = None,
        fom_modules: Any = None,
        **rti_options: Any,
    ) -> HlaRuntimeContext:
        if callback_model is None and self.spec.name == "rti1516_2025":
            callback_model = importlib.import_module("hla.rti1516_2025").CallbackModel.HLA_EVOKED
        auth_context = self.create_authentication_context(auth_config, transport=transport)
        strict_identification = bool(rti_options.pop("strict_identification", False))
        fom_load_result = None
        if fom_modules is not None and self.spec.name == "rti1516_2025":
            fom_load_result = self.load_fom(
                fom_modules,
                strict_identification=strict_identification,
            )
        return HlaRuntimeContext(
            edition=self.spec.name,
            provider=self.provider,
            transport=transport,
            rti_ambassador=self.create_rti_ambassador(**rti_options),
            federate_ambassador=self.create_federate_ambassador_proxy(),
            encoding_context=self.create_encoding_context(transport=transport, fom_modules=fom_modules),
            authentication_context=auth_context,
            callback_model=callback_model,
            fom_load_result=fom_load_result,
        )

    def edition_capabilities(self) -> EditionCapabilities:
        plugin = self._provider_plugin()
        notes: list[str] = []
        if self.spec.name == "rti1516_2025":
            notes.append("2025 factory composes BasicEncoderFactory and HLAnoCredentials auth by default")
        return EditionCapabilities(
            spec_name=self.spec.name,
            year=self.spec.year,
            provider=plugin.name,
            backend_family=plugin.family,
            capabilities=self.spec.capabilities,
            encoding="hla.rti1516_2025.BasicEncoderFactory" if self.spec.name == "rti1516_2025" else "hla.rti1516e.encoding",
            auth="HLAnoCredentials" if self.spec.name == "rti1516_2025" else "legacy-none",
            fom="edition-scoped-loader",
            notes=tuple(notes),
        )

    def load_fom(self, modules: Any, *, codecs: Any | None = None, **options: Any) -> FomLoadResult:
        if isinstance(modules, (str, bytes)):
            normalized = (modules,)
        else:
            normalized = tuple(modules)
        active_codecs = codecs or self.encoding_registry()
        if self.spec.name == "rti1516_2025":
            validation_module = importlib.import_module("hla.rti1516_2025.validation")
            repository = importlib.import_module("hla.rti1516_2025.foms").FomTypeRepository.from_modules(normalized)
            strict_identification = bool(options.get("strict_identification", False))
            issues = validation_module.validate_fom_modules(
                repository.modules,
                strict_identification=strict_identification,
            )
            issue_payloads = tuple(issue.as_dict() if hasattr(issue, "as_dict") else dict(issue) for issue in issues)
            diagnostics = (
                f"modules={len(repository.modules)}",
                f"datatypes={len(getattr(repository.catalog, 'datatype_names', ())) if repository.catalog is not None else 0}",
                f"object_classes={len(getattr(repository.catalog, 'object_classes', {})) if repository.catalog is not None else 0}",
                f"interaction_classes={len(getattr(repository.catalog, 'interaction_classes', {})) if repository.catalog is not None else 0}",
                f"validation_issues={len(issues)}",
                f"strict_identification={str(strict_identification).lower()}",
            )
            return FomLoadResult(
                modules=normalized,
                codecs=active_codecs,
                repository=repository,
                status="validated" if not issues else "invalid",
                diagnostics=diagnostics,
                validation_issues=issue_payloads,
                strict_identification=strict_identification,
            )
        return FomLoadResult(modules=normalized, codecs=active_codecs)

    def _composition(self) -> FactoryComposition:
        capabilities = self.edition_capabilities()
        return FactoryComposition(
            encoding_registry=self.encoding_registry(),
            auth_provider=self.auth_provider(),
            capabilities={
                "spec": capabilities.spec_name,
                "provider": capabilities.provider,
                "encoding": capabilities.encoding,
                "auth": capabilities.auth,
            },
        )

    def _provider_plugin(self) -> RTIBackendPlugin:
        _load_backend_plugins()
        plugin = _BACKEND_PLUGINS.get(_normalize_kind(self.provider))
        if plugin is None:
            raise ValueError(f"Unknown RTI provider: {self.provider!r}")
        if self.spec.name not in plugin.supports:
            raise ValueError(f"RTI provider {plugin.name!r} does not support HLA spec {self.spec.name!r}")
        return plugin


class HlaFactoryRegistry:
    @staticmethod
    def get(spec: str | HLASpec, *, provider: str = "inmemory", **options: Any) -> HlaFactory:
        return create_hla_factory(spec=spec, provider=provider, **options)


def _normalize_kind(kind: str) -> str:
    return kind.strip().lower().replace("_", "-")


def _normalize_spec(spec: str) -> str:
    return spec.strip().lower().replace("-", "_")


def _auth_config_value(config: Any, key: str, default: Any = None) -> Any:
    if config is None:
        return default
    if isinstance(config, Mapping):
        return config.get(key, default)
    return getattr(config, key, default)


def register_backend_factory(kind: str, factory: Any, *, aliases: tuple[str, ...] = ()) -> None:
    """Register a backend factory for a normalized backend kind and aliases."""

    for name in (kind, *aliases):
        _BACKEND_FACTORIES[_normalize_kind(name)] = factory


def register_backend_plugin(plugin: RTIBackendPlugin) -> None:
    """Register an RTI backend plugin and all of its aliases."""

    for name in (plugin.name, *plugin.aliases):
        normalized = _normalize_kind(name)
        _BACKEND_PLUGINS[normalized] = plugin
        _BACKEND_FACTORIES[normalized] = plugin.create_backend


def register_spec_plugin(plugin: SpecPlugin) -> None:
    """Register an HLA spec plugin and all of its aliases."""

    for name in (plugin.spec.name, *plugin.spec.aliases):
        _SPEC_PLUGINS[_normalize_spec(name)] = plugin


def _load_spec_plugins() -> None:
    global _SPEC_PLUGINS_LOADED
    if _SPEC_PLUGINS_LOADED:
        return
    loaded_plugins = [*_iter_entry_point_spec_plugins(), *_iter_source_checkout_spec_plugins()]
    for plugin in loaded_plugins:
        register_spec_plugin(plugin)
    _SPEC_PLUGINS_LOADED = True


def _load_backend_plugins() -> None:
    global _BACKEND_PLUGINS_LOADED
    if _BACKEND_PLUGINS_LOADED:
        return
    loaded_plugins = [*_iter_entry_point_backend_plugins(), *_iter_source_checkout_backend_plugins()]
    for plugin in loaded_plugins:
        register_backend_plugin(plugin)
    _BACKEND_PLUGINS_LOADED = True


def _iter_entry_point_backend_plugins() -> list[RTIBackendPlugin]:
    plugins: list[RTIBackendPlugin] = []
    try:
        entry_points = metadata.entry_points()
        selected = entry_points.select(group=BACKEND_ENTRY_POINT_GROUP)
    except Exception:
        return plugins
    for entry_point in selected:
        try:
            loaded = entry_point.load()
        except ModuleNotFoundError:
            continue
        plugin = loaded() if callable(loaded) else loaded
        if not isinstance(plugin, RTIBackendPlugin):
            raise TypeError(f"Backend entry point {entry_point.name!r} did not return RTIBackendPlugin")
        plugins.append(plugin)
    return plugins


def _iter_entry_point_spec_plugins() -> list[SpecPlugin]:
    plugins: list[SpecPlugin] = []
    try:
        entry_points = metadata.entry_points()
        selected = entry_points.select(group=SPEC_ENTRY_POINT_GROUP)
    except Exception:
        return plugins
    for entry_point in selected:
        try:
            loaded = entry_point.load()
        except ModuleNotFoundError:
            continue
        plugin = loaded() if callable(loaded) else loaded
        if not isinstance(plugin, SpecPlugin):
            raise TypeError(f"Spec entry point {entry_point.name!r} did not return SpecPlugin")
        plugins.append(plugin)
    return plugins


def _iter_source_checkout_spec_plugins() -> list[SpecPlugin]:
    plugins: list[SpecPlugin] = []
    for module_name in _SOURCE_CHECKOUT_SPEC_PLUGIN_MODULES:
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            if exc.name == module_name or module_name.startswith(f"{exc.name}."):
                continue
            raise
        plugin = getattr(module, "plugin")()
        if not isinstance(plugin, SpecPlugin):
            raise TypeError(f"Source checkout spec module {module_name!r} returned a non-plugin object")
        plugins.append(plugin)
    return plugins


def _iter_source_checkout_backend_plugins() -> list[RTIBackendPlugin]:
    plugins: list[RTIBackendPlugin] = []
    for module_name in _SOURCE_CHECKOUT_PLUGIN_MODULES:
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            # Source-checkout plugin discovery is opportunistic. When the caller
            # only exposes a subset of split-package roots on PYTHONPATH, missing
            # transitive package roots for optional plugins should skip cleanly
            # instead of breaking unrelated backend creation.
            missing_name = exc.name
            if missing_name is not None and (
                missing_name == module_name
                or module_name.startswith(f"{missing_name}.")
                or missing_name.startswith("hla.")
            ):
                continue
            raise
        for plugin in getattr(module, "backend_plugins", lambda: ())():
            if not isinstance(plugin, RTIBackendPlugin):
                raise TypeError(f"Source checkout backend module {module_name!r} returned a non-plugin object")
            plugins.append(plugin)
    return plugins


def available_spec_plugins() -> Mapping[str, SpecPlugin]:
    """Return registered spec plugins keyed by normalized names and aliases."""

    _load_spec_plugins()
    return dict(_SPEC_PLUGINS)


def iter_hla_spec_plugins() -> tuple[SpecPlugin, ...]:
    """Return unique installed HLA spec plugins sorted by spec name."""

    _load_spec_plugins()
    unique: dict[str, SpecPlugin] = {}
    for plugin in _SPEC_PLUGINS.values():
        unique[_normalize_spec(plugin.spec.name)] = plugin
    return tuple(unique[name] for name in sorted(unique))


def discover_specs() -> tuple[HLASpec, ...]:
    """Return installed HLA spec descriptors."""

    return tuple(plugin.spec for plugin in iter_hla_spec_plugins())


def resolve_spec(spec: str | HLASpec) -> HLASpec:
    """Resolve a spec name or alias to an installed HLA spec descriptor."""

    if isinstance(spec, HLASpec):
        return spec
    _load_spec_plugins()
    plugin = _SPEC_PLUGINS.get(_normalize_spec(spec))
    if plugin is None:
        raise ValueError(f"Unknown HLA spec: {spec!r}")
    return plugin.spec


def available_backend_plugins() -> Mapping[str, RTIBackendPlugin]:
    """Return registered backend plugins keyed by normalized names and aliases."""

    _load_backend_plugins()
    return dict(_BACKEND_PLUGINS)


def iter_rti_backend_plugins() -> tuple[RTIBackendPlugin, ...]:
    """Return unique installed RTI backend plugins sorted by plugin name."""

    _load_backend_plugins()
    unique: dict[str, RTIBackendPlugin] = {}
    for plugin in _BACKEND_PLUGINS.values():
        unique[_normalize_kind(plugin.name)] = plugin
    return tuple(unique[name] for name in sorted(unique))


def discover_rti_backends(*, spec: str | HLASpec | None = None, probe: bool = False) -> tuple[RTIBackendDiscovery, ...]:
    """Return installed RTI backend descriptors, optionally probing runtimes."""

    resolved_spec = resolve_spec(spec) if spec is not None else None
    rows: list[RTIBackendDiscovery] = []
    for plugin in iter_rti_backend_plugins():
        if resolved_spec is not None and resolved_spec.name not in plugin.supports:
            continue
        available: bool | None = None
        info: Any = None
        error: str | None = None
        if probe and plugin.discover is not None:
            try:
                discovered = plugin.discover()
                if isinstance(discovered, RTIBackendDiscovery):
                    available = True if discovered.available is None else discovered.available
                    info = discovered.info
                    error = discovered.error
                else:
                    info = discovered
                    available = info is not None
            except Exception as exc:
                available = False
                error = str(exc)
        rows.append(
            RTIBackendDiscovery(
                name=plugin.name,
                aliases=plugin.aliases,
                family=plugin.family,
                supports=plugin.supports,
                description=plugin.description,
                available=available,
                info=info,
                error=error,
            )
        )
    return tuple(rows)


def create_backend(
    backend: str | RTIBackendSpec = "inmemory",
    *,
    spec: str | HLASpec,
    **options: Any,
):
    """Create a backend by registered name."""

    if isinstance(backend, RTIBackendSpec):
        merged = dict(backend.options)
        merged.update(options)
        options = merged
        backend = backend.kind

    resolved_spec = resolve_spec(spec)
    _load_backend_plugins()
    normalized = _normalize_kind(backend)
    plugin = _BACKEND_PLUGINS.get(normalized)
    if plugin is None:
        raise ValueError(f"Unknown RTI backend kind: {backend!r}")
    if resolved_spec.name not in plugin.supports:
        raise ValueError(f"RTI backend {plugin.name!r} does not support HLA spec {resolved_spec.name!r}")
    composition = options.pop("factory_composition", None)
    return plugin.create_backend(BackendRequest(spec=resolved_spec, options=dict(options), composition=composition))


def create_hla_factory(
    *,
    spec: str | HLASpec,
    provider: str = "inmemory",
    **options: Any,
) -> HlaFactory:
    resolved_spec = resolve_spec(spec)
    factory = HlaFactory(spec=resolved_spec, provider=provider, options=dict(options))
    factory._provider_plugin()
    return factory


def create_rti_ambassador(
    *,
    spec: str | HLASpec,
    backend: str | RTIBackendSpec = "inmemory",
    **options: Any,
) -> Any:
    """Create a backend-neutral RTI ambassador."""

    backend_instance = create_backend(backend, spec=spec, **options)
    create_native_ambassador = getattr(backend_instance, "create_rti_ambassador", None)
    if callable(create_native_ambassador):
        return create_native_ambassador()
    make_rti_ambassador = importlib.import_module("hla.backends.common").make_rti_ambassador
    return make_rti_ambassador(backend_instance)


def register_transport_factory(kind: str, factory: Any, *, aliases: tuple[str, ...] = ()) -> None:
    """Register a transport factory without importing transport support at module load."""

    _register_transport_factory = importlib.import_module("hla.transports.common").register_transport_factory
    for name in (kind, *aliases):
        _register_transport_factory(name, factory)


__all__ = [
    "BACKEND_ENTRY_POINT_GROUP",
    "AuthenticationContext",
    "CredentialProvider",
    "EditionCapabilities",
    "EncodingContext",
    "FomLoadResult",
    "HlaFactory",
    "HlaFactoryRegistry",
    "HlaRuntimeContext",
    "NoAuthProvider",
    "RTIBackendDiscovery",
    "RTIBackendPlugin",
    "RTIBackendSpec",
    "RTITransportSpec",
    "available_spec_plugins",
    "available_backend_plugins",
    "create_backend",
    "create_hla_factory",
    "create_rti_ambassador",
    "discover_specs",
    "discover_rti_backends",
    "iter_hla_spec_plugins",
    "iter_rti_backend_plugins",
    "register_backend_factory",
    "register_backend_plugin",
    "register_spec_plugin",
    "register_transport_factory",
    "resolve_spec",
]
