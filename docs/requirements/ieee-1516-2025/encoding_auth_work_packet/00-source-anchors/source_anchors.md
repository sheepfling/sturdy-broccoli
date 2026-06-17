# Source anchors from uploaded HLA API/XML artifacts

These anchors ground the work packet in the uploaded artifacts. They are not exhaustive; they identify the surfaces the agent should use as compatibility boundaries.

## Encoding factory is paired with the RTI factory

2010 Java API:

```text
/mnt/data/hla_extract/nested/IEEE1516-2010_Java/java/src/hla/rti1516e/RtiFactory.java:15-23
public interface RtiFactory {
   RTIambassador getRtiAmbassador() throws RTIinternalError;

   EncoderFactory getEncoderFactory()
      throws RTIinternalError;

   String rtiName();
   String rtiVersion();
}
```

2025 Java API:

```text
/mnt/data/hla_extract/nested/hla-4-java-api-20250514/src/hla/rti1516_2025/RtiFactory.java:15-23
public interface RtiFactory {
   RTIambassador getRtiAmbassador() throws RTIinternalError;

   EncoderFactory getEncoderFactory()
      throws RTIinternalError;

   String rtiName();
   String rtiVersion();
}
```

## HLA DataElement contract

```text
/mnt/data/hla_extract/nested/hla-4-cpp-api-20250210/RTI/encoding/DataElement.h:22-63
DataElement exposes clone, encode, encodeInto, decode, decodeFrom, getEncodedLength, and getOctetBoundary.
```

## Built-in encoding helpers

```text
/mnt/data/hla_extract/nested/hla-4-cpp-api-20250210/RTI/encoding/BasicDataElements.h:146-170
HLAASCIIchar, HLAASCIIstring, HLAboolean, HLAbyte, HLAfloat32BE/LE,
HLAfloat64BE/LE, HLAinteger16BE/LE, HLAinteger32BE/LE, HLAinteger64BE/LE,
HLAunsignedInteger16BE/LE, HLAunsignedInteger32BE/LE, HLAunsignedInteger64BE/LE,
HLAoctet, HLAoctetPairBE/LE, HLAunicodeChar, HLAunicodeString.
```

```text
/mnt/data/hla_extract/nested/hla-4-java-api-20250514/src/hla/rti1516_2025/encoding/EncoderFactory.java:19-134
EncoderFactory creates primitives plus HLAvariantRecord, HLAextendableVariantRecord,
HLAfixedRecord, HLAfixedArray, HLAopaqueData, and HLAvariableArray.
```

## OMT/FOM datatype surfaces

```text
/mnt/data/hla_extract/nested/hla4xml-submission-ready-2025-06-04/IEEE1516-OMT-2025.xsd:2492-2545
dataTypes contains basicDataRepresentations, simpleDataTypes, referenceDataTypes,
enumeratedDataTypes, arrayDataTypes, fixedRecordDataTypes, and variantRecordDataTypes.
```

```text
/mnt/data/hla_extract/nested/hla4xml-submission-ready-2025-06-04/IEEE1516-OMT-2025.xsd:2559-2586
basicData has name, size, interpretation, endian, and encoding.
```

```text
/mnt/data/hla_extract/nested/hla4xml-submission-ready-2025-06-04/IEEE1516-OMT-2025.xsd:2688-2713
fixedRecordData has name, encoding, semantics, and ordered field entries.
```

```text
/mnt/data/hla_extract/nested/hla4xml-submission-ready-2025-06-04/IEEE1516-OMT-2025.xsd:2780-2823
variantRecordData has discriminant, discriminant dataType, alternatives, encoding, and semantics.
```

```text
/mnt/data/hla_extract/nested/hla4xml-submission-ready-2025-06-04/IEEE1516-OMT-2025.xsd:2843-2873
arrayData has element dataType, cardinality, encoding, and semantics.
```

```text
/mnt/data/hla_extract/nested/hla4xml-submission-ready-2025-06-04/IEEE1516-OMT-2025.xsd:3048-3073
standard composite encoding names include HLAfixedRecord, HLAvariantRecord,
HLAextendableVariantRecord, HLAfixedArray, and HLAvariableArray, with non-empty custom strings allowed by union types.
```

## 2025 credential-connect surface

```text
/mnt/data/hla_extract/nested/hla-4-java-api-20250514/src/hla/rti1516_2025/RTIambassador.java:71-95
connect has overloads accepting Credentials and can throw Unauthorized and InvalidCredentials.
```

FedPro proto:

```text
/mnt/data/hla_extract/nested/hla-4-api-fedpro-20250210/datatypes.proto:45-48
message Credentials { string type = 1; bytes data = 2; }
```

```text
/mnt/data/hla_extract/nested/hla-4-api-fedpro-20250210/RTIambassador.proto:1406-1417
ConnectWithCredentialsRequest and ConnectWithConfigurationAndCredentialsRequest carry Credentials.
```

## 2025 authorizer surface

```text
/mnt/data/hla_extract/nested/hla-4-cpp-api-20250210/RTI/auth/Credentials.h:17-45
Credentials carries a type and VariableLengthData. Predefined credential types include HLAplainTextPassword and HLAnoCredentials; user-defined authorizer libraries can support new types.
```

```text
/mnt/data/hla_extract/nested/hla-4-cpp-api-20250210/RTI/auth/AuthorizationResult.h:16-24
AuthorizationResult codes: AUTHORIZED, UNAUTHORIZED, INVALID_CREDENTIALS, AUTHORIZATION_ERROR.
```

```text
/mnt/data/hla_extract/nested/hla-4-cpp-api-20250210/RTI/auth/Authorizer.h:24-46
Authorizer authorizes RTI operation, federation operation, and federate operation.
```

```text
/mnt/data/hla_extract/nested/hla-4-cpp-api-20250210/RTI/libauth/AuthorizerFactoryFactory.h:19-34
The authorizer library may provide custom authorizers, selected by name from runtime initialization data.
```
