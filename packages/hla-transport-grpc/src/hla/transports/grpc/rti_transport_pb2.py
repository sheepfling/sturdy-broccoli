# -*- coding: utf-8 -*-
# Generated manually from rti_transport.proto because the local protoc binary is
# not usable in this workspace. The module shape matches generated protobuf code.
from __future__ import annotations

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import struct_pb2 as _struct_pb2  # noqa: F401 - loads dependency descriptor
from google.protobuf import symbol_database as _symbol_database

_sym_db = _symbol_database.Default()


def _build_file_descriptor() -> _descriptor.FileDescriptor:
    file_proto = _descriptor_pb2.FileDescriptorProto()
    file_proto.name = "rti_transport.proto"
    file_proto.package = "hla.rti1516e.backends.grpc_transport"
    file_proto.syntax = "proto3"
    file_proto.dependency.append("google/protobuf/struct.proto")

    transport_list = file_proto.message_type.add()
    transport_list.name = "TransportList"
    field = transport_list.field.add()
    field.name = "values"
    field.number = 1
    field.label = _descriptor.FieldDescriptor.LABEL_REPEATED
    field.type = _descriptor.FieldDescriptor.TYPE_MESSAGE
    field.type_name = ".hla.rti1516e.backends.grpc_transport.TransportValue"

    transport_struct = file_proto.message_type.add()
    transport_struct.name = "TransportStruct"
    fields_entry = transport_struct.nested_type.add()
    fields_entry.name = "FieldsEntry"
    fields_entry.options.map_entry = True
    key_field = fields_entry.field.add()
    key_field.name = "key"
    key_field.number = 1
    key_field.label = _descriptor.FieldDescriptor.LABEL_OPTIONAL
    key_field.type = _descriptor.FieldDescriptor.TYPE_STRING
    value_field = fields_entry.field.add()
    value_field.name = "value"
    value_field.number = 2
    value_field.label = _descriptor.FieldDescriptor.LABEL_OPTIONAL
    value_field.type = _descriptor.FieldDescriptor.TYPE_MESSAGE
    value_field.type_name = ".hla.rti1516e.backends.grpc_transport.TransportValue"
    field = transport_struct.field.add()
    field.name = "fields"
    field.number = 1
    field.label = _descriptor.FieldDescriptor.LABEL_REPEATED
    field.type = _descriptor.FieldDescriptor.TYPE_MESSAGE
    field.type_name = ".hla.rti1516e.backends.grpc_transport.TransportStruct.FieldsEntry"

    transport_value = file_proto.message_type.add()
    transport_value.name = "TransportValue"
    transport_value.oneof_decl.add().name = "kind"

    def add_oneof_field(name: str, number: int, field_type: int, type_name: str | None = None):
        entry = transport_value.field.add()
        entry.name = name
        entry.number = number
        entry.label = _descriptor.FieldDescriptor.LABEL_OPTIONAL
        setattr(entry, "type", field_type)
        entry.oneof_index = 0
        if type_name is not None:
            entry.type_name = type_name

    add_oneof_field("null_value", 1, _descriptor.FieldDescriptor.TYPE_ENUM, ".google.protobuf.NullValue")
    add_oneof_field("bool_value", 2, _descriptor.FieldDescriptor.TYPE_BOOL)
    add_oneof_field("int64_value", 3, _descriptor.FieldDescriptor.TYPE_INT64)
    add_oneof_field("double_value", 4, _descriptor.FieldDescriptor.TYPE_DOUBLE)
    add_oneof_field("string_value", 5, _descriptor.FieldDescriptor.TYPE_STRING)
    add_oneof_field("bytes_value", 6, _descriptor.FieldDescriptor.TYPE_BYTES)
    add_oneof_field("list_value", 7, _descriptor.FieldDescriptor.TYPE_MESSAGE, ".hla.rti1516e.backends.grpc_transport.TransportList")
    add_oneof_field("struct_value", 8, _descriptor.FieldDescriptor.TYPE_MESSAGE, ".hla.rti1516e.backends.grpc_transport.TransportStruct")

    transport_request = file_proto.message_type.add()
    transport_request.name = "TransportRequest"
    field = transport_request.field.add()
    field.name = "command"
    field.number = 1
    field.label = _descriptor.FieldDescriptor.LABEL_OPTIONAL
    field.type = _descriptor.FieldDescriptor.TYPE_STRING
    field = transport_request.field.add()
    field.name = "fields"
    field.number = 2
    field.label = _descriptor.FieldDescriptor.LABEL_REPEATED
    field.type = _descriptor.FieldDescriptor.TYPE_MESSAGE
    field.type_name = ".hla.rti1516e.backends.grpc_transport.TransportValue"
    field = transport_request.field.add()
    field.name = "metadata"
    field.number = 3
    field.label = _descriptor.FieldDescriptor.LABEL_OPTIONAL
    setattr(field, "type", _descriptor.FieldDescriptor.TYPE_MESSAGE)
    field.type_name = ".hla.rti1516e.backends.grpc_transport.TransportStruct"

    transport_error = file_proto.message_type.add()
    transport_error.name = "TransportError"
    field = transport_error.field.add()
    field.name = "code"
    field.number = 1
    field.label = _descriptor.FieldDescriptor.LABEL_OPTIONAL
    field.type = _descriptor.FieldDescriptor.TYPE_STRING
    field = transport_error.field.add()
    field.name = "message"
    field.number = 2
    field.label = _descriptor.FieldDescriptor.LABEL_OPTIONAL
    field.type = _descriptor.FieldDescriptor.TYPE_STRING
    field = transport_error.field.add()
    field.name = "metadata"
    field.number = 3
    field.label = _descriptor.FieldDescriptor.LABEL_OPTIONAL
    field.type = _descriptor.FieldDescriptor.TYPE_MESSAGE
    field.type_name = ".hla.rti1516e.backends.grpc_transport.TransportStruct"

    transport_response = file_proto.message_type.add()
    transport_response.name = "TransportResponse"
    field = transport_response.field.add()
    field.name = "fields"
    field.number = 1
    field.label = _descriptor.FieldDescriptor.LABEL_REPEATED
    field.type = _descriptor.FieldDescriptor.TYPE_MESSAGE
    field.type_name = ".hla.rti1516e.backends.grpc_transport.TransportValue"
    field = transport_response.field.add()
    field.name = "metadata"
    field.number = 2
    field.label = _descriptor.FieldDescriptor.LABEL_OPTIONAL
    field.type = _descriptor.FieldDescriptor.TYPE_MESSAGE
    field.type_name = ".hla.rti1516e.backends.grpc_transport.TransportStruct"
    field = transport_response.field.add()
    field.name = "error"
    field.number = 3
    field.label = _descriptor.FieldDescriptor.LABEL_OPTIONAL
    field.type = _descriptor.FieldDescriptor.TYPE_MESSAGE
    field.type_name = ".hla.rti1516e.backends.grpc_transport.TransportError"

    service = file_proto.service.add()
    service.name = "RTITransportService"
    method = service.method.add()
    method.name = "Request"
    method.input_type = ".hla.rti1516e.backends.grpc_transport.TransportRequest"
    method.output_type = ".hla.rti1516e.backends.grpc_transport.TransportResponse"

    return _descriptor_pool.Default().Add(file_proto)


DESCRIPTOR = _build_file_descriptor()


def _register_message(message: object) -> None:
    _sym_db.RegisterMessage(message)  # type: ignore[reportArgumentType]


TransportList = _reflection.GeneratedProtocolMessageType(
    "TransportList",
    (_message.Message,),
    {
        "DESCRIPTOR": DESCRIPTOR.message_types_by_name["TransportList"],
        "__module__": __name__,
    },
)
_register_message(TransportList())

TransportStruct = _reflection.GeneratedProtocolMessageType(
    "TransportStruct",
    (_message.Message,),
    {
        "DESCRIPTOR": DESCRIPTOR.message_types_by_name["TransportStruct"],
        "__module__": __name__,
    },
)
_register_message(TransportStruct())

TransportValue = _reflection.GeneratedProtocolMessageType(
    "TransportValue",
    (_message.Message,),
    {
        "DESCRIPTOR": DESCRIPTOR.message_types_by_name["TransportValue"],
        "__module__": __name__,
    },
)
_register_message(TransportValue())

TransportRequest = _reflection.GeneratedProtocolMessageType(
    "TransportRequest",
    (_message.Message,),
    {
        "DESCRIPTOR": DESCRIPTOR.message_types_by_name["TransportRequest"],
        "__module__": __name__,
    },
)
_register_message(TransportRequest())

TransportError = _reflection.GeneratedProtocolMessageType(
    "TransportError",
    (_message.Message,),
    {
        "DESCRIPTOR": DESCRIPTOR.message_types_by_name["TransportError"],
        "__module__": __name__,
    },
)
_register_message(TransportError())

TransportResponse = _reflection.GeneratedProtocolMessageType(
    "TransportResponse",
    (_message.Message,),
    {
        "DESCRIPTOR": DESCRIPTOR.message_types_by_name["TransportResponse"],
        "__module__": __name__,
    },
)
_register_message(TransportResponse())


__all__ = [
    "DESCRIPTOR",
    "TransportList",
    "TransportStruct",
    "TransportValue",
    "TransportRequest",
    "TransportError",
    "TransportResponse",
]
