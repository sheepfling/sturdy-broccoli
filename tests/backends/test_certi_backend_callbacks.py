from __future__ import annotations

from hla2010_rti_backend_common import RecordingFederateAmbassador
from hla2010_rti_certi import CERTIBackend
from hla2010.handles import AttributeHandle, AttributeHandleSet, FederateHandle, ObjectInstanceHandle


def test_certi_backend_dispatches_extended_ownership_callbacks():
    backend = CERTIBackend()
    fed = RecordingFederateAmbassador()
    backend.adapt_federate_ambassador(fed)

    backend._dispatch_helper_callback(  # type: ignore[attr-defined]
        ["REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION", "7", "31,32", "6f666665722d746167"]
    )
    backend._dispatch_helper_callback(  # type: ignore[attr-defined]
        ["ATTRIBUTE_OWNERSHIP_UNAVAILABLE", "7", "31,32"]
    )
    backend._dispatch_helper_callback(  # type: ignore[attr-defined]
        ["OWNERSHIP_ACQUIRED", "7", "31", "61637175697265642d746167"]
    )
    backend._dispatch_helper_callback(  # type: ignore[attr-defined]
        ["REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE", "7", "31,32", "72656c656173652d746167"]
    )
    backend._dispatch_helper_callback(  # type: ignore[attr-defined]
        ["REQUEST_DIVESTITURE_CONFIRMATION", "7", "31"]
    )
    backend._dispatch_helper_callback(  # type: ignore[attr-defined]
        ["CONFIRM_ATTRIBUTE_OWNERSHIP_ACQUISITION_CANCELLATION", "7", "32"]
    )
    backend._dispatch_helper_callback(  # type: ignore[attr-defined]
        ["ATTRIBUTE_IS_NOT_OWNED", "7", "31"]
    )
    backend._dispatch_helper_callback(  # type: ignore[attr-defined]
        ["INFORM_ATTRIBUTE_OWNERSHIP", "7", "31", "5"]
    )

    assumption = fed.last_callback("requestAttributeOwnershipAssumption")
    assert assumption is not None
    assert assumption.args == (ObjectInstanceHandle(7), AttributeHandleSet({AttributeHandle(31), AttributeHandle(32)}), b"offer-tag")

    unavailable = fed.last_callback("attributeOwnershipUnavailable")
    assert unavailable is not None
    assert unavailable.args[0] == ObjectInstanceHandle(7)
    assert unavailable.args[1] == AttributeHandleSet({AttributeHandle(31), AttributeHandle(32)})

    acquired = fed.last_callback("attributeOwnershipAcquisitionNotification")
    assert acquired is not None
    assert acquired.args == (ObjectInstanceHandle(7), AttributeHandleSet({AttributeHandle(31)}), b"acquired-tag")

    release = fed.last_callback("requestAttributeOwnershipRelease")
    assert release is not None
    assert release.args[0] == ObjectInstanceHandle(7)
    assert release.args[1] == AttributeHandleSet({AttributeHandle(31), AttributeHandle(32)})
    assert release.args[2] == b"release-tag"

    divest = fed.last_callback("requestDivestitureConfirmation")
    assert divest is not None
    assert divest.args == (ObjectInstanceHandle(7), AttributeHandleSet({AttributeHandle(31)}))

    cancelled = fed.last_callback("confirmAttributeOwnershipAcquisitionCancellation")
    assert cancelled is not None
    assert cancelled.args == (ObjectInstanceHandle(7), AttributeHandleSet({AttributeHandle(32)}))

    not_owned = fed.last_callback("attributeIsNotOwned")
    assert not_owned is not None
    assert not_owned.args == (ObjectInstanceHandle(7), AttributeHandle(31))

    informed = fed.last_callback("informAttributeOwnership")
    assert informed is not None
    assert informed.args == (ObjectInstanceHandle(7), AttributeHandle(31), FederateHandle(5))
