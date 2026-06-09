from __future__ import annotations


def test_split_runtime_common_package_exports_process_helpers():
    from hla2010.real_rti_process import RuntimeProcess as OldRuntimeProcess
    from hla2010.real_rti_process import reserve_tcp_port as old_reserve_tcp_port
    from hla2010_rti_runtime_common import RuntimeProcess, reserve_tcp_port

    assert OldRuntimeProcess is RuntimeProcess
    assert old_reserve_tcp_port is reserve_tcp_port


def test_vendor_runtime_packages_import_shared_process_helpers_from_new_package():
    from hla2010_rti_runtime_common import RuntimeProcess
    from hla2010_rti_certi.real_rti_certi import RuntimeProcess as CertiRuntimeProcess
    from hla2010_rti_pitch_common.real_rti_pitch import RuntimeProcess as PitchRuntimeProcess

    assert CertiRuntimeProcess is RuntimeProcess
    assert PitchRuntimeProcess is RuntimeProcess
