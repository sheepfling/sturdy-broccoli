from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MINIMAL_DEMO_PYPROJECT = ROOT / "packages" / "hla2010-fom-minimal-demo" / "pyproject.toml"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    if not slug:
        raise ValueError("package name must contain at least one ASCII letter or digit")
    return slug


def _snake_to_words(value: str) -> list[str]:
    return [part for part in re.split(r"[-_]+", value) if part]


def _camel_name(slug: str) -> str:
    return "".join(part.capitalize() for part in _snake_to_words(slug))


def _repo_version() -> str:
    text = MINIMAL_DEMO_PYPROJECT.read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"$', text, flags=re.MULTILINE)
    if match is None:
        raise ValueError(f"could not determine repo package version from {MINIMAL_DEMO_PYPROJECT}")
    return match.group(1)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _assert_missing(path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing path: {path}")


def _fom_xml(display_name: str, object_class: str, interaction_class: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<objectModel
    xmlns="http://standards.ieee.org/IEEE1516-2010"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://standards.ieee.org/IEEE1516-2010 IEEE1516-2010.xsd">
  <modelIdentification>
    <name>{display_name} FOM Module</name>
    <type>FOM</type>
    <version>1.0</version>
    <modificationDate>2026-06-13</modificationDate>
    <securityClassification>UNCLASSIFIED</securityClassification>
    <purpose>Package-scaffolded starter FOM for {display_name}</purpose>
    <applicationDomain>HLA package scaffolding and Python RTI-first onboarding</applicationDomain>
    <description>Minimal packaged FOM created by ./tools/new-fom-package.</description>
  </modelIdentification>

  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>{object_class}</name>
        <sharing>PublishSubscribe</sharing>
        <semantics>Starter object for the {display_name} package.</semantics>
        <attribute>
          <name>Message</name>
          <dataType>HLAunicodeString</dataType>
          <updateType>Conditional</updateType>
          <updateRate>NA</updateRate>
          <ownership>DivestAcquire</ownership>
          <sharing>PublishSubscribe</sharing>
          <transportation>HLAreliable</transportation>
          <order>Receive</order>
          <semantics>Starter text payload.</semantics>
        </attribute>
      </objectClass>
    </objectClass>
  </objects>

  <interactions>
    <interactionClass>
      <name>HLAinteractionRoot</name>
      <interactionClass>
        <name>{interaction_class}</name>
        <sharing>PublishSubscribe</sharing>
        <transportation>HLAreliable</transportation>
        <order>Receive</order>
        <semantics>Starter interaction for the {display_name} package.</semantics>
        <parameter>
          <name>Sender</name>
          <dataType>HLAunicodeString</dataType>
          <semantics>Originating federate name.</semantics>
        </parameter>
        <parameter>
          <name>Message</name>
          <dataType>HLAunicodeString</dataType>
          <semantics>Starter interaction payload.</semantics>
        </parameter>
      </interactionClass>
    </interactionClass>
  </interactions>

  <dataTypes>
    <basicDataRepresentations>
      <basicData name="HLAASCIIchar" size="8" endian="NA" encoding="ASCII"/>
      <basicData name="HLAunicodeChar" size="16" endian="Big" encoding="Unicode"/>
    </basicDataRepresentations>
    <simpleDataTypes>
      <simpleData name="HLAunicodeStringElement">
        <representation>HLAunicodeChar</representation>
      </simpleData>
    </simpleDataTypes>
    <arrayDataTypes>
      <arrayData name="HLAunicodeString" dataType="HLAunicodeStringElement" cardinality="Dynamic" encoding="HLAvariableArray"/>
    </arrayDataTypes>
  </dataTypes>
</objectModel>
"""


def _scenario_module(module_name: str, scenario_stem: str, display_name: str, object_class: str, interaction_class: str) -> str:
    upper = scenario_stem.upper()
    class_prefix = _camel_name(scenario_stem)
    return f'''"""Starter publisher/subscriber HLA smoke scenario for {display_name}."""
from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from typing import Any, Callable, Iterable, Mapping, Protocol

from hla2010.enums import CallbackModel, OrderType, ResignAction, TransportationType
from hla2010.exceptions import FederatesCurrentlyJoined, FederationExecutionAlreadyExists, FederationExecutionDoesNotExist, RTIexception
from hla2010.handles import AttributeHandle, InteractionClassHandle, ObjectClassHandle, ObjectInstanceHandle, ParameterHandle
from hla2010.spec import FederateAmbassadorSpec

{upper}_OBJECT_CLASS = "HLAobjectRoot.{object_class}"
{upper}_INTERACTION_CLASS = "HLAinteractionRoot.{interaction_class}"
MESSAGE_ATTRIBUTE = "Message"
SENDER_PARAMETER = "Sender"
MESSAGE_PARAMETER = "Message"


@dataclass(frozen=True)
class {class_prefix}ObjectUpdate:
    object_name: str
    message: str


@dataclass(frozen=True)
class {class_prefix}Interaction:
    sender: str
    message: str


@dataclass
class {class_prefix}ScenarioResult:
    federation_name: str
    backend_kinds: tuple[str, str]
    object_updates: list[{class_prefix}ObjectUpdate]
    interactions: list[{class_prefix}Interaction]
    publisher_events: list[tuple[str, Any]] = field(default_factory=list)
    subscriber_events: list[tuple[str, Any]] = field(default_factory=list)


class RTIAmbassadorLike(Protocol):
    def connect(self, *args: Any, **kwargs: Any) -> Any: ...
    def create_federation_execution(self, *args: Any, **kwargs: Any) -> Any: ...
    def join_federation_execution(self, *args: Any, **kwargs: Any) -> Any: ...
    def resign_federation_execution(self, *args: Any, **kwargs: Any) -> Any: ...
    def disconnect(self, *args: Any, **kwargs: Any) -> Any: ...
    def destroy_federation_execution(self, *args: Any, **kwargs: Any) -> Any: ...
    def evoke_multiple_callbacks(self, *args: Any, **kwargs: Any) -> Any: ...


RtiFactory = Callable[[str], RTIAmbassadorLike]


def encode_text(value: str) -> bytes:
    return value.encode("utf-8")


def decode_text(data: bytes) -> str:
    return bytes(data).decode("utf-8")


class PublisherFederate(FederateAmbassadorSpec):
    """Federate that publishes one object update and one interaction."""

    def __init__(self, *, name: str = "Publisher-1") -> None:
        self.name = name
        self.rti: Any | None = None
        self.object_class: ObjectClassHandle | None = None
        self.message_attr: AttributeHandle | None = None
        self.interaction_class: InteractionClassHandle | None = None
        self.sender_param: ParameterHandle | None = None
        self.message_param: ParameterHandle | None = None
        self.object_handle: ObjectInstanceHandle | None = None
        self.events: list[tuple[str, Any]] = []

    def setup(self, rti: Any) -> None:
        self.rti = rti
        self.object_class = rti.get_object_class_handle({upper}_OBJECT_CLASS)
        self.message_attr = rti.get_attribute_handle(self.object_class, MESSAGE_ATTRIBUTE)
        self.interaction_class = rti.get_interaction_class_handle({upper}_INTERACTION_CLASS)
        self.sender_param = rti.get_parameter_handle(self.interaction_class, SENDER_PARAMETER)
        self.message_param = rti.get_parameter_handle(self.interaction_class, MESSAGE_PARAMETER)
        rti.publish_object_class_attributes(self.object_class, {{self.message_attr}})
        rti.publish_interaction_class(self.interaction_class)
        self.object_handle = rti.register_object_instance(self.object_class, self.name)
        self.events.append(("register_object_instance", self.name))

    def publish(self, *, object_message: str, interaction_message: str) -> None:
        assert self.rti is not None
        assert self.object_handle is not None
        assert self.message_attr is not None
        assert self.interaction_class is not None
        assert self.sender_param is not None
        assert self.message_param is not None

        self.rti.update_attribute_values(
            self.object_handle,
            {{self.message_attr: encode_text(object_message)}},
            b"{scenario_stem}-object",
        )
        self.events.append(("update_attribute_values", object_message))

        self.rti.send_interaction(
            self.interaction_class,
            {{
                self.sender_param: encode_text(self.name),
                self.message_param: encode_text(interaction_message),
            }},
            b"{scenario_stem}-interaction",
        )
        self.events.append(("send_interaction", interaction_message))


class SubscriberFederate(FederateAmbassadorSpec):
    """Federate that subscribes to the starter object and interaction."""

    def __init__(self, *, name: str = "Subscriber-1") -> None:
        self.name = name
        self.rti: Any | None = None
        self.object_class: ObjectClassHandle | None = None
        self.message_attr: AttributeHandle | None = None
        self.interaction_class: InteractionClassHandle | None = None
        self.sender_param: ParameterHandle | None = None
        self.message_param: ParameterHandle | None = None
        self.object_names: dict[ObjectInstanceHandle, str] = {{}}
        self.object_updates: list[{class_prefix}ObjectUpdate] = []
        self.interactions: list[{class_prefix}Interaction] = []
        self.events: list[tuple[str, Any]] = []

    def setup(self, rti: Any) -> None:
        self.rti = rti
        self.object_class = rti.get_object_class_handle({upper}_OBJECT_CLASS)
        self.message_attr = rti.get_attribute_handle(self.object_class, MESSAGE_ATTRIBUTE)
        self.interaction_class = rti.get_interaction_class_handle({upper}_INTERACTION_CLASS)
        self.sender_param = rti.get_parameter_handle(self.interaction_class, SENDER_PARAMETER)
        self.message_param = rti.get_parameter_handle(self.interaction_class, MESSAGE_PARAMETER)
        rti.subscribe_object_class_attributes(self.object_class, {{self.message_attr}})
        rti.subscribe_interaction_class(self.interaction_class)

    def discover_object_instance(self, the_object: ObjectInstanceHandle, the_object_class: ObjectClassHandle, object_name: str, *extra: Any) -> None:
        if self.object_class is not None and the_object_class == self.object_class:
            self.object_names[the_object] = str(object_name)
            self.events.append(("discover_object_instance", object_name))

    def reflect_attribute_values(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: Mapping[AttributeHandle, bytes],
        user_supplied_tag: bytes,
        sent_ordering: Any = OrderType.RECEIVE,
        transportation_type: Any = TransportationType.RELIABLE,
        *extra: Any,
    ) -> None:
        if self.message_attr is None or self.message_attr not in the_attributes:
            return
        update = {class_prefix}ObjectUpdate(
            object_name=self.object_names.get(the_object, f"Object-{{the_object.value}}"),
            message=decode_text(the_attributes[self.message_attr]),
        )
        self.object_updates.append(update)
        self.events.append(("reflect_attribute_values", (update.object_name, update.message, user_supplied_tag)))

    def receive_interaction(
        self,
        interaction_class: InteractionClassHandle,
        the_parameters: Mapping[ParameterHandle, bytes],
        user_supplied_tag: bytes,
        sent_ordering: Any = OrderType.RECEIVE,
        transportation_type: Any = TransportationType.RELIABLE,
        *extra: Any,
    ) -> None:
        if self.interaction_class is None or interaction_class != self.interaction_class:
            return
        assert self.sender_param is not None
        assert self.message_param is not None
        interaction = {class_prefix}Interaction(
            sender=decode_text(the_parameters[self.sender_param]),
            message=decode_text(the_parameters[self.message_param]),
        )
        self.interactions.append(interaction)
        self.events.append(("receive_interaction", (interaction.sender, interaction.message, user_supplied_tag)))


def create_python_pair() -> tuple[Any, Any]:
    """Create publisher/subscriber RTI ambassadors sharing one Python engine."""

    return import_module("hla2010_rti_python").create_python_pair()


def _python_pair_factory() -> RtiFactory:
    pair_by_role: dict[str, RTIAmbassadorLike] = {{}}

    def factory(role: str) -> RTIAmbassadorLike:
        if role not in pair_by_role:
            publisher_rti, subscriber_rti = create_python_pair()
            pair_by_role.update({{"publisher": publisher_rti, "subscriber": subscriber_rti}})
        return pair_by_role[role]

    return factory


def _call_factory(factory: RtiFactory, role: str) -> RTIAmbassadorLike:
    try:
        return factory(role)
    except TypeError:
        return factory()  # type: ignore[misc]


def _drain_callbacks(*rtis: Any, cycles: int = 6) -> None:
    for _ in range(cycles):
        for rti in rtis:
            rti.evoke_multiple_callbacks(0.0, 0.1)


def run_{scenario_stem}_scenario(
    rti_factory: RtiFactory | None = None,
    *,
    federation_name: str = "{display_name}Federation",
    object_message: str = "hello-object",
    interaction_message: str = "hello-interaction",
    publisher: PublisherFederate | None = None,
    subscriber: SubscriberFederate | None = None,
    fom_modules: Iterable[Any] | None = None,
    cleanup: bool = True,
) -> {class_prefix}ScenarioResult:
    """Run the starter publisher/subscriber scenario with any backend-neutral RTI pair."""

    if rti_factory is None:
        rti_factory = _python_pair_factory()

    publisher = publisher or PublisherFederate()
    subscriber = subscriber or SubscriberFederate()
    publisher_rti = _call_factory(rti_factory, "publisher")
    subscriber_rti = _call_factory(rti_factory, "subscriber")

    publisher_rti.connect(publisher, CallbackModel.HLA_EVOKED)
    subscriber_rti.connect(subscriber, CallbackModel.HLA_EVOKED)

    try:
        publisher_rti.create_federation_execution(federation_name, list(fom_modules or []))
    except FederationExecutionAlreadyExists:
        pass

    publisher_rti.join_federation_execution("Publisher", "{scenario_stem}-publisher", federation_name)
    subscriber_rti.join_federation_execution("Subscriber", "{scenario_stem}-subscriber", federation_name)

    subscriber.setup(subscriber_rti)
    publisher.setup(publisher_rti)
    _drain_callbacks(publisher_rti, subscriber_rti)

    publisher.publish(object_message=object_message, interaction_message=interaction_message)
    _drain_callbacks(publisher_rti, subscriber_rti)

    result = {class_prefix}ScenarioResult(
        federation_name=federation_name,
        backend_kinds=(
            getattr(getattr(publisher_rti, "backend_info", None), "kind", "unknown"),
            getattr(getattr(subscriber_rti, "backend_info", None), "kind", "unknown"),
        ),
        object_updates=list(subscriber.object_updates),
        interactions=list(subscriber.interactions),
        publisher_events=list(publisher.events),
        subscriber_events=list(subscriber.events),
    )

    if cleanup:
        for rti in (subscriber_rti, publisher_rti):
            try:
                rti.resign_federation_execution(ResignAction.NO_ACTION)
            except RTIexception:
                pass
        try:
            publisher_rti.destroy_federation_execution(federation_name)
        except (FederationExecutionDoesNotExist, FederatesCurrentlyJoined, RTIexception):
            pass
        for rti in (subscriber_rti, publisher_rti):
            try:
                rti.disconnect()
            except RTIexception:
                pass
        for rti in (subscriber_rti, publisher_rti):
            close = getattr(rti, "close", None)
            if callable(close):
                close()

    return result


__all__ = [
    "{class_prefix}Interaction",
    "{class_prefix}ObjectUpdate",
    "{class_prefix}ScenarioResult",
    "PublisherFederate",
    "SubscriberFederate",
    "create_python_pair",
    "decode_text",
    "encode_text",
    "run_{scenario_stem}_scenario",
]
'''


def _factory_module(module_name: str, scenario_stem: str, display_name: str, fom_filename: str) -> str:
    return f'''"""Shared backend-factory helpers for the {display_name} starter example."""
from __future__ import annotations

from collections.abc import Callable, Sequence
from importlib import import_module
from importlib import resources
from typing import Any


def {scenario_stem}_fom_path() -> str:
    """Return the packaged {display_name} FOM module path."""

    return str(resources.files("{module_name}.resources.foms").joinpath("{fom_filename}"))


def make_{scenario_stem}_factory(
    backend: str,
    *,
    classpath: Sequence[str] = (),
    rti_factory_name: str | None = None,
    py4j_address: str = "127.0.0.1",
    py4j_port: int = 25333,
    py4j_callback_port: int = 0,
    backend_options: dict[str, Any] | None = None,
) -> Callable[[str], Any]:
    """Build a backend factory for the {display_name} starter example."""

    normalized = backend.strip().lower()
    backend_options = dict(backend_options or {{}})
    if normalized in {{"python", "inmemory", "in-memory"}}:
        pair_by_role: dict[str, Any] = {{}}
        create_python_pair = import_module("hla2010_rti_python").create_python_pair

        def factory(role: str) -> Any:
            if role not in pair_by_role:
                publisher_rti, subscriber_rti = create_python_pair()
                pair_by_role.update({{"publisher": publisher_rti, "subscriber": subscriber_rti}})
            return pair_by_role[role]

        return factory

    if normalized in {{"jpype", "java-jpype"}}:
        java_jpype = import_module("hla2010_rti_java_jpype")
        jpype_options = dict(backend_options)
        classpath_list = [item for item in classpath if item]
        if classpath_list and "classpath" not in jpype_options:
            jpype_options["classpath"] = classpath_list
        if rti_factory_name is not None and "rti_factory_name" not in jpype_options:
            jpype_options["rti_factory_name"] = rti_factory_name
        config = jpype_options.pop("config", None) or java_jpype.JPypeConfig(**jpype_options)

        def factory(_role: str) -> Any:
            return java_jpype.rti_ambassador(config)

        return factory

    if normalized in {{"py4j", "java-py4j"}}:
        java_py4j = import_module("hla2010_rti_java_py4j")
        py4j_options = dict(backend_options)
        py4j_options.setdefault("gateway_parameters", {{"address": py4j_address, "port": py4j_port}})
        py4j_options.setdefault("callback_server_parameters", {{"port": py4j_callback_port}})
        if rti_factory_name is not None and "rti_factory_name" not in py4j_options:
            py4j_options["rti_factory_name"] = rti_factory_name
        config = py4j_options.pop("config", None) or java_py4j.Py4JConfig(**py4j_options)

        def factory(_role: str) -> Any:
            return java_py4j.rti_ambassador(config)

        return factory

    create_rti_ambassador = import_module("hla2010_rti_runtime_common").create_rti_ambassador

    def factory(_role: str) -> Any:
        return create_rti_ambassador(normalized, **backend_options)

    return factory


__all__ = ["make_{scenario_stem}_factory", "{scenario_stem}_fom_path"]
'''


def _scenarios_init(scenario_stem: str) -> str:
    class_prefix = _camel_name(scenario_stem)
    return f'''"""Starter scenario helpers."""

from .{scenario_stem} import (
    {class_prefix}Interaction,
    {class_prefix}ObjectUpdate,
    {class_prefix}ScenarioResult,
    PublisherFederate,
    SubscriberFederate,
    run_{scenario_stem}_scenario,
)
from .{scenario_stem}_factory import make_{scenario_stem}_factory, {scenario_stem}_fom_path

__all__ = [
    "{class_prefix}Interaction",
    "{class_prefix}ObjectUpdate",
    "{class_prefix}ScenarioResult",
    "PublisherFederate",
    "SubscriberFederate",
    "make_{scenario_stem}_factory",
    "{scenario_stem}_fom_path",
    "run_{scenario_stem}_scenario",
]
'''


def _package_init(scenario_stem: str) -> str:
    class_prefix = _camel_name(scenario_stem)
    return f'''"""Starter FOM and scenario package."""

from .scenarios import (
    {class_prefix}Interaction,
    {class_prefix}ObjectUpdate,
    {class_prefix}ScenarioResult,
    PublisherFederate,
    SubscriberFederate,
    make_{scenario_stem}_factory,
    {scenario_stem}_fom_path,
    run_{scenario_stem}_scenario,
)

__all__ = [
    "{class_prefix}Interaction",
    "{class_prefix}ObjectUpdate",
    "{class_prefix}ScenarioResult",
    "PublisherFederate",
    "SubscriberFederate",
    "make_{scenario_stem}_factory",
    "{scenario_stem}_fom_path",
    "run_{scenario_stem}_scenario",
]
'''


def _package_readme(dist_name: str, module_name: str, scenario_stem: str, fom_filename: str, display_name: str) -> str:
    return f"""# {dist_name}

Starter packaged FOM and two-federate scenario helpers for the `hla2010`
workspace.

This package owns:

- the packaged `{fom_filename}` resource
- a tiny publisher/subscriber scenario under `{module_name}`
- a scaffolded example of how to add one FOM package without touching backend
  internals
- a starter split-package test under `tests/examples/test_{scenario_stem}_demo.py`

Import the canonical implementation from `{module_name}`.

Use this package when you want:

- a package-backed FOM starting point for {display_name}
- a reference layout for `resources/foms` plus `scenarios`
- a tutorial-sized scenario that runs against the Python RTI first

This package depends on `hla2010-spec` and `hla2010-rti-runtime-common`. It
does not own RTI backend implementations or a package-local command. The human
operator surface stays the repo-level example
[`examples/{scenario_stem}_demo.py`](../../examples/{scenario_stem}_demo.py).

For setup, bootstrap the repo root first:

```bash
./tools/bootstrap python
source .venv/bin/activate
```

Then run the starter example:

```bash
python examples/{scenario_stem}_demo.py --backend python
```

If you are extending the scaffold, the useful imports are:

```python
from {module_name}.scenarios import (
    make_{scenario_stem}_factory,
    {scenario_stem}_fom_path,
    run_{scenario_stem}_scenario,
)
```
"""


def _package_docs_readme(dist_name: str, module_name: str, scenario_stem: str) -> str:
    return f"""# {dist_name} docs

This package owns a concrete starter example FOM, packaged `resources.foms`
assets, and the smallest supported scenario helpers for copying a new
example/FOM package.

Key owned surfaces:

- `{module_name}.resources.foms`: packaged starter FOM assets
- `{module_name}.scenarios`: canonical publisher/subscriber scenario and
  factory helpers
- `tests/examples/test_{scenario_stem}_demo.py`: split-package guard coverage
  for the installable starter package

This package does not own RTI backend implementations or generic shared
verification-harness scenarios.
"""


def _pyproject(dist_name: str, module_name: str, version: str) -> str:
    return f"""[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{dist_name}"
version = "{version}"
description = "Starter packaged FOM and two-federate scenario helpers for hla2010-spec"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
  "hla2010-spec=={version}",
  "hla2010-rti-runtime-common=={version}",
]

[project.optional-dependencies]
python-rti = ["hla2010-rti-python=={version}"]
test = ["pytest"]

[tool.setuptools.package-dir]
"" = "src"

[tool.setuptools.packages.find]
where = ["src"]
include = ["{module_name}*"]

[tool.setuptools.package-data]
{module_name} = ["resources/foms/*.xml"]

[tool.hla2010.package-split]
status = "implementation-owned"
role = "fom-example"
source_roots = [
  "packages/{dist_name}/src/{module_name}",
]
"""


def _example_script(module_name: str, scenario_stem: str, display_name: str) -> str:
    return f'''#!/usr/bin/env python3
"""Run the package-backed {display_name} publisher/subscriber example."""
from __future__ import annotations

import argparse

from {module_name}.scenarios import (
    make_{scenario_stem}_factory,
    {scenario_stem}_fom_path,
    run_{scenario_stem}_scenario,
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=["python", "java-shim-jpype", "java-shim-py4j", "jpype", "py4j"], default="python")
    parser.add_argument("--federation-name", default="{display_name}Federation")
    parser.add_argument("--object-message", default="hello-object")
    parser.add_argument("--interaction-message", default="hello-interaction")
    args = parser.parse_args(argv)

    result = run_{scenario_stem}_scenario(
        make_{scenario_stem}_factory(args.backend),
        federation_name=args.federation_name,
        object_message=args.object_message,
        interaction_message=args.interaction_message,
        fom_modules=[{scenario_stem}_fom_path()],
    )

    print(
        f"backend={{','.join(result.backend_kinds)}} federation={{result.federation_name}} "
        f"object_updates={{len(result.object_updates)}} interactions={{len(result.interactions)}}"
    )
    for item in result.object_updates:
        print(f"object name={{item.object_name}} message={{item.message}}")
    for item in result.interactions:
        print(f"interaction sender={{item.sender}} message={{item.message}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _example_test(module_name: str, scenario_stem: str, fom_filename: str, display_name: str, object_class: str, interaction_class: str) -> str:
    return f'''from __future__ import annotations

from pathlib import Path

from hla2010.fom import parse_fom_xml
from {module_name}.scenarios import (
    make_{scenario_stem}_factory,
    {scenario_stem}_fom_path,
    run_{scenario_stem}_scenario,
)


def test_{scenario_stem}_fom_path_resolves_to_package_resource() -> None:
    path = Path({scenario_stem}_fom_path()).resolve()
    assert path.name == "{fom_filename}"
    assert "packages/hla2010-fom-{scenario_stem}/src/{module_name}/resources/foms" in str(path)


def test_{scenario_stem}_fom_declares_one_object_and_one_interaction() -> None:
    module = parse_fom_xml({scenario_stem}_fom_path())
    assert module.name == "{display_name} FOM Module"
    assert "HLAobjectRoot.{object_class}" in {{spec.full_name for spec in module.object_classes}}
    assert "HLAinteractionRoot.{interaction_class}" in {{spec.full_name for spec in module.interaction_classes}}


def test_{scenario_stem}_runs_against_python_rti() -> None:
    result = run_{scenario_stem}_scenario(
        make_{scenario_stem}_factory("python"),
        fom_modules=[{scenario_stem}_fom_path()],
    )
    assert result.backend_kinds == ("python/in-memory", "python/in-memory")
    assert len(result.object_updates) == 1
    assert result.object_updates[0].object_name == "Publisher-1"
    assert result.object_updates[0].message == "hello-object"
    assert len(result.interactions) == 1
    assert result.interactions[0].sender == "Publisher-1"
    assert result.interactions[0].message == "hello-interaction"
'''


def build_scaffold(name: str, *, output_root: Path) -> list[Path]:
    slug = _slugify(name)
    display_name = _camel_name(slug)
    dist_name = f"hla2010-fom-{slug}"
    module_name = f"hla2010_fom_{slug.replace('-', '_')}"
    scenario_stem = slug.replace("-", "_")
    object_class = f"{display_name}Object"
    interaction_class = f"{display_name}Announcement"
    fom_filename = f"{display_name}FOMmodule.xml"
    version = _repo_version()

    package_root = output_root / "packages" / dist_name
    example_path = output_root / "examples" / f"{scenario_stem}_demo.py"
    test_path = output_root / "tests" / "examples" / f"test_{scenario_stem}_demo.py"

    for path in (package_root, example_path, test_path):
        _assert_missing(path)

    file_map: dict[Path, str] = {
        package_root / "README.md": _package_readme(dist_name, module_name, scenario_stem, fom_filename, display_name),
        package_root / "docs" / "README.md": _package_docs_readme(dist_name, module_name, scenario_stem),
        package_root / "pyproject.toml": _pyproject(dist_name, module_name, version),
        package_root / "src" / module_name / "__init__.py": _package_init(scenario_stem),
        package_root / "src" / module_name / "resources" / "__init__.py": "",
        package_root / "src" / module_name / "resources" / "foms" / fom_filename: _fom_xml(display_name, object_class, interaction_class),
        package_root / "src" / module_name / "scenarios" / "__init__.py": _scenarios_init(scenario_stem),
        package_root / "src" / module_name / "scenarios" / f"{scenario_stem}.py": _scenario_module(module_name, scenario_stem, display_name, object_class, interaction_class),
        package_root / "src" / module_name / "scenarios" / f"{scenario_stem}_factory.py": _factory_module(module_name, scenario_stem, display_name, fom_filename),
        example_path: _example_script(module_name, scenario_stem, display_name),
        test_path: _example_test(module_name, scenario_stem, fom_filename, display_name, object_class, interaction_class),
    }

    written: list[Path] = []
    for path, text in file_map.items():
        _write(path, text)
        written.append(path)
    return written


def _relative(path: Path, start: Path) -> str:
    return path.relative_to(start).as_posix()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scaffold a package-owned FOM and starter federate example.")
    parser.add_argument("name", help="demo/package stem such as target-tracker or minimal-demo")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT,
        help="root directory that should receive packages/, examples/, and tests/ output",
    )
    args = parser.parse_args(argv)

    output_root = args.output_root.resolve()
    written = build_scaffold(args.name, output_root=output_root)

    print(f"Scaffolded FOM package for {args.name}")
    print(f"output_root: {output_root}")
    for path in written:
        print(f"- {_relative(path, output_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
