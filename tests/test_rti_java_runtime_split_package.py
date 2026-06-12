from __future__ import annotations

from hla2010_rti_java_common import (
    discover_java_home,
    discover_java_home as package_discover_java_home,
    discover_java_tool,
    discover_java_tool as package_discover_java_tool,
    ensure_java_home,
    ensure_java_home as package_ensure_java_home,
)


def test_split_java_common_package_exports_runtime_helpers():
    from hla2010_rti_java_common.java_runtime import (
        discover_java_home as discover_java_home_from_module,
    )
    from hla2010_rti_java_common.java_runtime import (
        discover_java_tool as discover_java_tool_from_module,
    )
    from hla2010_rti_java_common.java_runtime import (
        ensure_java_home as ensure_java_home_from_module,
    )

    assert discover_java_home_from_module is package_discover_java_home
    assert discover_java_tool_from_module is package_discover_java_tool
    assert ensure_java_home_from_module is package_ensure_java_home


def test_split_java_common_package_root_re_exports_runtime_helpers():
    assert discover_java_home is package_discover_java_home
    assert discover_java_tool is package_discover_java_tool
    assert ensure_java_home is package_ensure_java_home
