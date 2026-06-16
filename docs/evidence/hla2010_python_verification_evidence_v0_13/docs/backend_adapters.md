# Backend adapter design notes

The Python HLA surface now has three layers:

1. **Spec-shaped API**: `hla.rti1516e.raw_api` and `hla.rti1516e.api` expose the IEEE-derived
   `RTIambassador` and `FederateAmbassador` method names.
2. **Backend-neutral façade**: `hla.rti1516e.backends.base.DelegatingRTIAmbassador`
   provides a concrete ambassador and forwards every RTI service to an
   `RTIBackend`.
3. **Runtime backends**: JPype, Py4J, pure Python, C++, or network adapters only
   need to implement `RTIBackend.invoke(Invocation)` and callback adaptation.

## Invocation boundary

`Invocation.method_name` is always the original HLA lowerCamelCase service name,
for example `joinFederationExecution` or `updateAttributeValues`.  Snake-case
calls such as `join_federation_execution` are resolved by the Pythonic API layer
before they reach the backend.

The invocation also carries API metadata for all source overloads.  Java adapters
use that metadata to order keyword arguments into positional Java arguments.

## Java callback boundary

When the application calls:

```python
rti.connect(MyFederate(), CallbackModel.HLA_EVOKED)
```

`DelegatingRTIAmbassador` asks the backend to adapt the Python
`FederateAmbassador`:

- JPype returns a `JProxy("hla.rti1516e.FederateAmbassador", inst=dispatcher)`.
- Py4J returns a Python callback object with `Java.implements = ["hla.rti1516e.FederateAmbassador"]`.

Both paths use `PythonFederateAmbassadorDispatcher`, which converts callback
arguments back to Python values and invokes the user's callback method.

## Handle strategy

Java RTIs return implementation-specific opaque handle objects.  The Python
public API keeps typed handles such as `FederateHandle` and `ObjectClassHandle`.
`NativeHandleRegistry` bridges the two worlds:

- Java handle returned by backend -> typed Python surrogate handle.
- Same Python surrogate handle passed later -> original Java handle object.

The surrogate integer is adapter-local.  It is not intended to be a portable HLA
wire encoding; for actual handle encoding, call the RTI `encode*Handle` service
on the same backend.

## Extension points

Vendor-specific adapters can specialize any of these:

- `JavaBridge.call` for nonstandard method dispatch.
- `JavaBridge.create_federate_proxy` for custom callback-server setup.
- `JavaValueConverter.to_backend` and `from_backend` for factory-created HLA
  `AttributeHandleSet`, `ParameterHandleValueMap`, logical-time objects, and
  byte arrays.
- `JavaRTIBackend.invoke` for RTIs that need a service-specific shim.

## Current limitations

The JPype and Py4J modules are scaffolds that load optional dependencies only
when used.  They should be tested against each target RTI vendor because the HLA
Java API leaves implementation details such as factory classes, logical-time
classes, and concrete set/map classes to the RTI implementation.
