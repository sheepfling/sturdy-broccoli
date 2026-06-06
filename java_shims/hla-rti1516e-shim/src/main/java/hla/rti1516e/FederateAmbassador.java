package hla.rti1516e;
import hla.rti1516e.exceptions.FederateInternalError;
import java.util.Map;
public interface FederateAmbassador {
    default void discoverObjectInstance(ObjectInstanceHandle theObject, ObjectClassHandle theObjectClass, String objectName) throws FederateInternalError { }
    default void discoverObjectInstance(ObjectInstanceHandle theObject, ObjectClassHandle theObjectClass, String objectName, FederateHandle producingFederate) throws FederateInternalError { }
    default void reflectAttributeValues(ObjectInstanceHandle theObject, Map<AttributeHandle, byte[]> theAttributes, byte[] userSuppliedTag, OrderType sentOrdering, TransportationTypeHandle theTransport, Object reflectInfo) throws FederateInternalError { }
    default void receiveInteraction(InteractionClassHandle interactionClass, Map<ParameterHandle, byte[]> theParameters, byte[] userSuppliedTag, OrderType sentOrdering, TransportationTypeHandle theTransport, Object receiveInfo) throws FederateInternalError { }
    default void timeRegulationEnabled(LogicalTime time) throws FederateInternalError { }
    default void timeConstrainedEnabled(LogicalTime time) throws FederateInternalError { }
    default void timeAdvanceGrant(LogicalTime theTime) throws FederateInternalError { }
}
