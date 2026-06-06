package hla.rti1516e;

import hla.rti1516e.exceptions.*;
import java.util.ArrayDeque;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Queue;
import java.util.Set;

/**
 * Tiny stateful RTIambassador shim for backend smoke tests.
 *
 * This is deliberately not a full HLA RTI.  It only implements the methods used
 * by hla2010.testing.scenarios.run_basic_federate_scenario so JPype/Py4J can be
 * exercised against real Java classes with the same package/method shape as a
 * 1516e RTI.
 */
public class RTIambassador {
    private interface Callback { void run() throws RTIexception; }

    private boolean connected = false;
    private FederateAmbassador federate;
    private String federationName;
    private String federateName;
    private String federateType;
    private FederateHandle federateHandle;
    private int nextHandle = 1;
    private long currentTime = 0L;
    private final Queue<Callback> callbacks = new ArrayDeque<>();
    private final Set<String> federations = new HashSet<>();
    private final TransportationTypeHandle transportationReliable = new TransportationTypeHandle(alloc());

    private final Map<String, ObjectClassHandle> objectClasses = new HashMap<>();
    private final Map<ObjectClassHandle, String> objectClassNames = new HashMap<>();
    private final Map<String, AttributeHandle> attributes = new HashMap<>();
    private final Map<String, String> attributeNames = new HashMap<>();

    private final Map<String, InteractionClassHandle> interactionClasses = new HashMap<>();
    private final Map<InteractionClassHandle, String> interactionClassNames = new HashMap<>();
    private final Map<String, ParameterHandle> parameters = new HashMap<>();
    private final Map<String, String> parameterNames = new HashMap<>();

    private final Map<ObjectInstanceHandle, ObjectClassHandle> objectClassByObject = new HashMap<>();
    private final Map<ObjectInstanceHandle, String> objectNamesByHandle = new HashMap<>();
    private final Map<String, ObjectInstanceHandle> objectHandlesByName = new HashMap<>();

    private final Set<ObjectClassHandle> publishedObjects = new HashSet<>();
    private final Set<ObjectClassHandle> subscribedObjects = new HashSet<>();
    private final Set<InteractionClassHandle> publishedInteractions = new HashSet<>();
    private final Set<InteractionClassHandle> subscribedInteractions = new HashSet<>();

    private final Map<String, DimensionHandle> dimensions = new HashMap<>();
    private final Map<DimensionHandle, String> dimensionNames = new HashMap<>();
    private final Map<RegionHandle, Set<DimensionHandle>> regions = new HashMap<>();

    private int alloc() { return nextHandle++; }

    private void requireConnected() throws NotConnected {
        if (!connected) { throw new NotConnected("RTI shim is not connected"); }
    }

    private void requireJoined() throws RTIexception {
        requireConnected();
        if (federateHandle == null) { throw new FederateNotExecutionMember("Federate has not joined a federation"); }
    }

    private static long timeValue(Object value) {
        if (value instanceof HLAinteger64Time) { return ((HLAinteger64Time) value).getValue(); }
        if (value instanceof Number) { return ((Number) value).longValue(); }
        return Long.parseLong(String.valueOf(value));
    }

    private String attributeKey(ObjectClassHandle whichClass, String name) {
        return whichClass.intValue() + ":" + name;
    }

    private String attributeReverseKey(ObjectClassHandle whichClass, AttributeHandle handle) {
        return whichClass.intValue() + ":" + handle.intValue();
    }

    private String parameterKey(InteractionClassHandle whichClass, String name) {
        return whichClass.intValue() + ":" + name;
    }

    private String parameterReverseKey(InteractionClassHandle whichClass, ParameterHandle handle) {
        return whichClass.intValue() + ":" + handle.intValue();
    }

    // Federation management ------------------------------------------------
    public void connect(FederateAmbassador federateReference, CallbackModel callbackModel) throws RTIexception {
        connect(federateReference, callbackModel, null);
    }

    public void connect(FederateAmbassador federateReference, CallbackModel callbackModel, String localSettingsDesignator) throws RTIexception {
        if (connected) { throw new AlreadyConnected("RTI shim is already connected"); }
        this.federate = federateReference;
        this.connected = true;
    }

    public void disconnect() throws RTIexception {
        if (federateHandle != null) { throw new FederateIsExecutionMember("Resign before disconnecting"); }
        connected = false;
        federate = null;
    }

    public void createFederationExecution(String name) throws RTIexception { createFederationExecution(name, (Object) null); }
    public void createFederationExecution(String name, Object ignored) throws RTIexception {
        requireConnected();
        if (federations.contains(name)) { throw new FederationExecutionAlreadyExists(name); }
        federations.add(name);
    }
    public void createFederationExecution(String name, Object[] ignored) throws RTIexception { createFederationExecution(name, (Object) ignored); }
    public void createFederationExecution(String name, java.util.List<?> ignored) throws RTIexception { createFederationExecution(name, (Object) ignored); }
    public void createFederationExecution(String name, java.net.URL[] ignored) throws RTIexception { createFederationExecution(name, (Object) ignored); }

    public void destroyFederationExecution(String name) throws RTIexception {
        requireConnected();
        if (federateHandle != null && name.equals(federationName)) { throw new FederatesCurrentlyJoined(name); }
        if (!federations.contains(name)) { throw new FederationExecutionDoesNotExist(name); }
        federations.remove(name);
    }

    public FederateHandle joinFederationExecution(String federateType, String federationExecutionName) throws RTIexception {
        return joinFederationExecution("federate-" + nextHandle, federateType, federationExecutionName);
    }
    public FederateHandle joinFederationExecution(String federateName, String federateType, String federationExecutionName) throws RTIexception {
        requireConnected();
        if (federateHandle != null) { throw new FederateAlreadyExecutionMember("Already joined"); }
        if (!federations.contains(federationExecutionName)) { throw new FederationExecutionDoesNotExist(federationExecutionName); }
        this.federateName = federateName;
        this.federateType = federateType;
        this.federationName = federationExecutionName;
        this.federateHandle = new FederateHandle(alloc());
        return federateHandle;
    }
    public FederateHandle joinFederationExecution(String federateName, String federateType, String federationExecutionName, Object ignored) throws RTIexception {
        return joinFederationExecution(federateName, federateType, federationExecutionName);
    }

    public void resignFederationExecution(ResignAction resignAction) throws RTIexception {
        requireJoined();
        federateHandle = null;
        federateName = null;
        federateType = null;
        federationName = null;
    }

    // Declaration management ------------------------------------------------
    public void publishObjectClassAttributes(ObjectClassHandle theClass, Set<AttributeHandle> attributeList) throws RTIexception {
        requireJoined();
        publishedObjects.add(theClass);
    }
    public void subscribeObjectClassAttributes(ObjectClassHandle theClass, Set<AttributeHandle> attributeList) throws RTIexception {
        requireJoined();
        subscribedObjects.add(theClass);
    }
    public void subscribeObjectClassAttributes(ObjectClassHandle theClass, Set<AttributeHandle> attributeList, String updateRateDesignator) throws RTIexception {
        subscribeObjectClassAttributes(theClass, attributeList);
    }
    public void publishInteractionClass(InteractionClassHandle theInteraction) throws RTIexception {
        requireJoined();
        publishedInteractions.add(theInteraction);
    }
    public void subscribeInteractionClass(InteractionClassHandle theClass) throws RTIexception {
        requireJoined();
        subscribedInteractions.add(theClass);
    }

    // Object management -----------------------------------------------------
    public ObjectInstanceHandle registerObjectInstance(ObjectClassHandle theClass) throws RTIexception {
        return registerObjectInstance(theClass, "Object-" + nextHandle);
    }
    public ObjectInstanceHandle registerObjectInstance(ObjectClassHandle theClass, String theObjectName) throws RTIexception {
        requireJoined();
        if (objectHandlesByName.containsKey(theObjectName)) { throw new ObjectInstanceNameInUse(theObjectName); }
        ObjectInstanceHandle handle = new ObjectInstanceHandle(alloc());
        objectHandlesByName.put(theObjectName, handle);
        objectNamesByHandle.put(handle, theObjectName);
        objectClassByObject.put(handle, theClass);
        callbacks.add(() -> federate.discoverObjectInstance(handle, theClass, theObjectName));
        return handle;
    }

    public void updateAttributeValues(ObjectInstanceHandle theObject, Map<AttributeHandle, byte[]> theAttributes, byte[] userSuppliedTag) throws RTIexception {
        updateAttributeValues(theObject, theAttributes, userSuppliedTag, null);
    }
    public void updateAttributeValues(ObjectInstanceHandle theObject, Map<AttributeHandle, byte[]> theAttributes, byte[] userSuppliedTag, Object time) throws RTIexception {
        requireJoined();
        if (!objectClassByObject.containsKey(theObject)) { throw new ObjectInstanceNotKnown(String.valueOf(theObject)); }
        ObjectClassHandle theClass = objectClassByObject.get(theObject);
        if (subscribedObjects.contains(theClass)) {
            callbacks.add(() -> federate.reflectAttributeValues(theObject, theAttributes, userSuppliedTag, OrderType.RECEIVE, transportationReliable, new Object()));
        }
    }

    public void sendInteraction(InteractionClassHandle interactionClass, Map<ParameterHandle, byte[]> parameters, byte[] userSuppliedTag) throws RTIexception {
        sendInteraction(interactionClass, parameters, userSuppliedTag, null);
    }
    public void sendInteraction(InteractionClassHandle interactionClass, Map<ParameterHandle, byte[]> parameters, byte[] userSuppliedTag, Object time) throws RTIexception {
        requireJoined();
        if (subscribedInteractions.contains(interactionClass)) {
            callbacks.add(() -> federate.receiveInteraction(interactionClass, parameters, userSuppliedTag, OrderType.RECEIVE, transportationReliable, new Object()));
        }
    }

    // Time management -------------------------------------------------------
    public void enableTimeRegulation(LogicalTimeInterval lookahead) throws RTIexception {
        requireJoined();
        callbacks.add(() -> federate.timeRegulationEnabled(new HLAinteger64Time(currentTime)));
    }
    public void enableTimeConstrained() throws RTIexception {
        requireJoined();
        callbacks.add(() -> federate.timeConstrainedEnabled(new HLAinteger64Time(currentTime)));
    }
    public void timeAdvanceRequest(LogicalTime theTime) throws RTIexception {
        requireJoined();
        currentTime = timeValue(theTime);
        callbacks.add(() -> federate.timeAdvanceGrant(new HLAinteger64Time(currentTime)));
    }
    public LogicalTime queryLogicalTime() throws RTIexception {
        requireJoined();
        return new HLAinteger64Time(currentTime);
    }
    public boolean evokeCallback(double approximateMinimumTimeInSeconds) throws RTIexception {
        if (callbacks.isEmpty()) { return false; }
        callbacks.remove().run();
        return !callbacks.isEmpty();
    }
    public boolean evokeMultipleCallbacks(double approximateMinimumTimeInSeconds, double approximateMaximumTimeInSeconds) throws RTIexception {
        while (!callbacks.isEmpty()) { callbacks.remove().run(); }
        return false;
    }
    public void enableAsynchronousDelivery() throws RTIexception { requireJoined(); }
    public void disableAsynchronousDelivery() throws RTIexception { requireJoined(); }

    // Data distribution management -----------------------------------------
    public RegionHandle createRegion(Set<DimensionHandle> dimensions) throws RTIexception {
        requireJoined();
        RegionHandle region = new RegionHandle(alloc());
        regions.put(region, new HashSet<>(dimensions));
        return region;
    }
    public void commitRegionModifications(Set<RegionHandle> regionsToCommit) throws RTIexception {
        requireJoined();
        for (RegionHandle region : regionsToCommit) {
            if (!regions.containsKey(region)) { throw new RTIinternalError("Unknown region " + region); }
        }
    }
    public void deleteRegion(RegionHandle theRegion) throws RTIexception {
        requireJoined();
        regions.remove(theRegion);
    }

    // Support services ------------------------------------------------------
    public FederateHandle getFederateHandle(String theName) throws RTIexception {
        requireJoined();
        if (theName.equals(federateName) && federateHandle != null) { return federateHandle; }
        throw new NameNotFound(theName);
    }
    public String getFederateName(FederateHandle theHandle) throws RTIexception {
        requireJoined();
        if (theHandle.equals(federateHandle)) { return federateName; }
        throw new FederateHandleNotKnown(String.valueOf(theHandle));
    }

    public ObjectClassHandle getObjectClassHandle(String theName) throws RTIexception {
        requireJoined();
        ObjectClassHandle handle = objectClasses.get(theName);
        if (handle == null) {
            handle = new ObjectClassHandle(alloc());
            objectClasses.put(theName, handle);
            objectClassNames.put(handle, theName);
        }
        return handle;
    }
    public String getObjectClassName(ObjectClassHandle theHandle) throws RTIexception {
        requireJoined();
        String name = objectClassNames.get(theHandle);
        if (name == null) { throw new InvalidObjectClassHandle(String.valueOf(theHandle)); }
        return name;
    }
    public ObjectClassHandle getKnownObjectClassHandle(ObjectInstanceHandle theObject) throws RTIexception {
        requireJoined();
        ObjectClassHandle handle = objectClassByObject.get(theObject);
        if (handle == null) { throw new ObjectInstanceNotKnown(String.valueOf(theObject)); }
        return handle;
    }

    public AttributeHandle getAttributeHandle(ObjectClassHandle whichClass, String theName) throws RTIexception {
        requireJoined();
        String key = attributeKey(whichClass, theName);
        AttributeHandle handle = attributes.get(key);
        if (handle == null) {
            handle = new AttributeHandle(alloc());
            attributes.put(key, handle);
            attributeNames.put(attributeReverseKey(whichClass, handle), theName);
        }
        return handle;
    }
    public String getAttributeName(ObjectClassHandle whichClass, AttributeHandle theHandle) throws RTIexception {
        requireJoined();
        String name = attributeNames.get(attributeReverseKey(whichClass, theHandle));
        if (name == null) { throw new AttributeNotDefined(String.valueOf(theHandle)); }
        return name;
    }

    public InteractionClassHandle getInteractionClassHandle(String theName) throws RTIexception {
        requireJoined();
        InteractionClassHandle handle = interactionClasses.get(theName);
        if (handle == null) {
            handle = new InteractionClassHandle(alloc());
            interactionClasses.put(theName, handle);
            interactionClassNames.put(handle, theName);
        }
        return handle;
    }
    public String getInteractionClassName(InteractionClassHandle theHandle) throws RTIexception {
        requireJoined();
        String name = interactionClassNames.get(theHandle);
        if (name == null) { throw new InvalidInteractionClassHandle(String.valueOf(theHandle)); }
        return name;
    }

    public ParameterHandle getParameterHandle(InteractionClassHandle whichClass, String theName) throws RTIexception {
        requireJoined();
        String key = parameterKey(whichClass, theName);
        ParameterHandle handle = parameters.get(key);
        if (handle == null) {
            handle = new ParameterHandle(alloc());
            parameters.put(key, handle);
            parameterNames.put(parameterReverseKey(whichClass, handle), theName);
        }
        return handle;
    }
    public String getParameterName(InteractionClassHandle whichClass, ParameterHandle theHandle) throws RTIexception {
        requireJoined();
        String name = parameterNames.get(parameterReverseKey(whichClass, theHandle));
        if (name == null) { throw new InteractionParameterNotDefined(String.valueOf(theHandle)); }
        return name;
    }

    public ObjectInstanceHandle getObjectInstanceHandle(String theName) throws RTIexception {
        requireJoined();
        ObjectInstanceHandle handle = objectHandlesByName.get(theName);
        if (handle == null) { throw new ObjectInstanceNotKnown(theName); }
        return handle;
    }
    public String getObjectInstanceName(ObjectInstanceHandle theHandle) throws RTIexception {
        requireJoined();
        String name = objectNamesByHandle.get(theHandle);
        if (name == null) { throw new ObjectInstanceNotKnown(String.valueOf(theHandle)); }
        return name;
    }

    public DimensionHandle getDimensionHandle(String theName) throws RTIexception {
        requireJoined();
        DimensionHandle handle = dimensions.get(theName);
        if (handle == null) {
            handle = new DimensionHandle(alloc());
            dimensions.put(theName, handle);
            dimensionNames.put(handle, theName);
        }
        return handle;
    }
    public String getDimensionName(DimensionHandle theHandle) throws RTIexception {
        requireJoined();
        String name = dimensionNames.get(theHandle);
        if (name == null) { throw new RTIinternalError("Unknown dimension " + theHandle); }
        return name;
    }

    public String getHLAversion() { return "HLA 1516-2010 Java shim"; }
}
