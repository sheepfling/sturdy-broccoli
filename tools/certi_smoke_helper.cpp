#include <RTI/NullFederateAmbassador.h>
#include <RTI/RTI1516fedTime.h>
#include <RTI/RTIambassador.h>
#include <RTI/RTIambassadorFactory.h>
#include <RTI/VariableLengthData.h>

#include <cstdlib>
#include <cmath>
#include <deque>
#include <iostream>
#include <map>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

std::string percent_decode(const std::string& text)
{
    std::string result;
    result.reserve(text.size());
    for (std::size_t i = 0; i < text.size(); ++i) {
        if (text[i] == '%' && i + 2 < text.size()) {
            const auto hex = text.substr(i + 1, 2);
            char value = static_cast<char>(std::strtol(hex.c_str(), nullptr, 16));
            result.push_back(value);
            i += 2;
        } else {
            result.push_back(text[i]);
        }
    }
    return result;
}

std::string percent_encode(const std::string& text)
{
    static const char* hex = "0123456789ABCDEF";
    std::string result;
    for (unsigned char ch : text) {
        const bool safe =
            (ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') || (ch >= '0' && ch <= '9') || ch == '-' || ch == '_' ||
            ch == '.' || ch == '~';
        if (safe) {
            result.push_back(static_cast<char>(ch));
        } else {
            result.push_back('%');
            result.push_back(hex[(ch >> 4) & 0xF]);
            result.push_back(hex[ch & 0xF]);
        }
    }
    return result;
}

std::wstring widen_ascii(const std::string& text)
{
    return std::wstring(text.begin(), text.end());
}

std::string narrow_ascii(const std::wstring& text)
{
    return std::string(text.begin(), text.end());
}

rti1516e::OrderType parse_order_type_name(const std::string& text)
{
    if (text == "TIMESTAMP") {
        return rti1516e::TIMESTAMP;
    }
    if (text == "RECEIVE") {
        return rti1516e::RECEIVE;
    }
    throw std::runtime_error("Unknown order type " + text);
}

std::vector<std::string> split_tab(const std::string& line)
{
    std::vector<std::string> fields;
    std::size_t start = 0;
    while (true) {
        const auto pos = line.find('\t', start);
        if (pos == std::string::npos) {
            fields.push_back(line.substr(start));
            return fields;
        }
        fields.push_back(line.substr(start, pos - start));
        start = pos + 1;
    }
}

std::vector<std::string> split_char(const std::string& text, char separator)
{
    std::vector<std::string> fields;
    if (text.empty()) {
        return fields;
    }
    std::size_t start = 0;
    while (true) {
        const auto pos = text.find(separator, start);
        if (pos == std::string::npos) {
            fields.push_back(text.substr(start));
            return fields;
        }
        fields.push_back(text.substr(start, pos - start));
        start = pos + 1;
    }
}

std::string hex_encode_bytes(void const* data, std::size_t size)
{
    static const char* hex = "0123456789abcdef";
    auto const* bytes = static_cast<unsigned char const*>(data);
    std::string result;
    result.reserve(size * 2);
    for (std::size_t i = 0; i < size; ++i) {
        unsigned char value = bytes[i];
        result.push_back(hex[(value >> 4) & 0xF]);
        result.push_back(hex[value & 0xF]);
    }
    return result;
}

std::string hex_encode_string(const std::string& text)
{
    return hex_encode_bytes(text.data(), text.size());
}

std::string hex_encode_variable_length_data(rti1516e::VariableLengthData const& value)
{
    return hex_encode_bytes(value.data(), value.size());
}

std::string hex_decode_string(const std::string& hex)
{
    if (hex.size() % 2 != 0) {
        throw std::runtime_error("Odd-length hex payload");
    }
    std::string result;
    result.reserve(hex.size() / 2);
    for (std::size_t i = 0; i < hex.size(); i += 2) {
        char buffer[3] = {hex[i], hex[i + 1], '\0'};
        char value = static_cast<char>(std::strtol(buffer, nullptr, 16));
        result.push_back(value);
    }
    return result;
}

void ok()
{
    std::cout << "OK" << std::endl;
}

void ok(const std::string& value)
{
    std::cout << "OK\t" << percent_encode(value) << std::endl;
}

void ok(const std::vector<std::string>& values)
{
    std::cout << "OK";
    for (std::vector<std::string>::const_iterator it = values.begin(); it != values.end(); ++it) {
        std::cout << '\t' << percent_encode(*it);
    }
    std::cout << std::endl;
}

void error(const std::string& type, const std::wstring& message)
{
    std::cout << "ERR\t" << type << "\t" << percent_encode(std::string(message.begin(), message.end())) << std::endl;
}

#define HANDLE_RTI_EXCEPTION(name) \
    catch (const rti1516e::name& exc) { \
        error(#name, exc.what()); \
    }

template<typename HandleT>
class HandleRegistry {
public:
    int intern(HandleT const& handle)
    {
        typename std::map<HandleT, int>::const_iterator existing = handle_to_id_.find(handle);
        if (existing != handle_to_id_.end()) {
            return existing->second;
        }
        int id = next_id_++;
        handle_to_id_[handle] = id;
        id_to_handle_[id] = handle;
        return id;
    }

    HandleT resolve(int id) const
    {
        typename std::map<int, HandleT>::const_iterator it = id_to_handle_.find(id);
        if (it == id_to_handle_.end()) {
            throw std::runtime_error("Unknown handle id " + std::to_string(id));
        }
        return it->second;
    }

private:
    int next_id_ = 1;
    std::map<HandleT, int> handle_to_id_;
    std::map<int, HandleT> id_to_handle_;
};

struct PendingEvent {
    std::string kind;
    int primary_handle = 0;
    int secondary_handle = 0;
    int tertiary_handle = 0;
    std::string object_name;
    std::vector<std::pair<int, std::string> > values;
    std::vector<int> handles;
    std::string tag_hex;
    int order = 0;
    int received_order = 0;
    int transportation = 0;
    std::string time_type;
    std::string time_value;
};

class SmokeSession;

std::string logical_time_to_wire_string(rti1516e::LogicalTime const& logical_time, const std::string& logical_time_name);

class QueueingFederateAmbassador : public rti1516e::NullFederateAmbassador {
public:
    explicit QueueingFederateAmbassador(SmokeSession& session)
        : session_(session)
    {
    }

    virtual void discoverObjectInstance(
        rti1516e::ObjectInstanceHandle theObject,
        rti1516e::ObjectClassHandle theObjectClass,
        std::wstring const& theObjectInstanceName)
        throw (rti1516e::FederateInternalError);

    virtual void reflectAttributeValues(
        rti1516e::ObjectInstanceHandle theObject,
        rti1516e::AttributeHandleValueMap const& theAttributeValues,
        rti1516e::VariableLengthData const& theUserSuppliedTag,
        rti1516e::OrderType sentOrder,
        rti1516e::TransportationType theType,
        rti1516e::SupplementalReflectInfo theReflectInfo)
        throw (rti1516e::FederateInternalError);

    virtual void reflectAttributeValues(
        rti1516e::ObjectInstanceHandle theObject,
        rti1516e::AttributeHandleValueMap const& theAttributeValues,
        rti1516e::VariableLengthData const& theUserSuppliedTag,
        rti1516e::OrderType sentOrder,
        rti1516e::TransportationType theType,
        rti1516e::LogicalTime const& theTime,
        rti1516e::OrderType receivedOrder,
        rti1516e::SupplementalReflectInfo theReflectInfo)
        throw (rti1516e::FederateInternalError);

    virtual void reflectAttributeValues(
        rti1516e::ObjectInstanceHandle theObject,
        rti1516e::AttributeHandleValueMap const& theAttributeValues,
        rti1516e::VariableLengthData const& theUserSuppliedTag,
        rti1516e::OrderType sentOrder,
        rti1516e::TransportationType theType,
        rti1516e::LogicalTime const& theTime,
        rti1516e::OrderType receivedOrder,
        rti1516e::MessageRetractionHandle theHandle,
        rti1516e::SupplementalReflectInfo theReflectInfo)
        throw (rti1516e::FederateInternalError);

    virtual void receiveInteraction(
        rti1516e::InteractionClassHandle theInteraction,
        rti1516e::ParameterHandleValueMap const& theParameterValues,
        rti1516e::VariableLengthData const& theUserSuppliedTag,
        rti1516e::OrderType sentOrder,
        rti1516e::TransportationType theType,
        rti1516e::SupplementalReceiveInfo theReceiveInfo)
        throw (rti1516e::FederateInternalError);

    virtual void receiveInteraction(
        rti1516e::InteractionClassHandle theInteraction,
        rti1516e::ParameterHandleValueMap const& theParameterValues,
        rti1516e::VariableLengthData const& theUserSuppliedTag,
        rti1516e::OrderType sentOrder,
        rti1516e::TransportationType theType,
        rti1516e::LogicalTime const& theTime,
        rti1516e::OrderType receivedOrder,
        rti1516e::SupplementalReceiveInfo theReceiveInfo)
        throw (rti1516e::FederateInternalError);

    virtual void receiveInteraction(
        rti1516e::InteractionClassHandle theInteraction,
        rti1516e::ParameterHandleValueMap const& theParameterValues,
        rti1516e::VariableLengthData const& theUserSuppliedTag,
        rti1516e::OrderType sentOrder,
        rti1516e::TransportationType theType,
        rti1516e::LogicalTime const& theTime,
        rti1516e::OrderType receivedOrder,
        rti1516e::MessageRetractionHandle theHandle,
        rti1516e::SupplementalReceiveInfo theReceiveInfo)
        throw (rti1516e::FederateInternalError);

    virtual void timeRegulationEnabled(rti1516e::LogicalTime const& theFederateTime)
        throw (rti1516e::FederateInternalError);

    virtual void timeConstrainedEnabled(rti1516e::LogicalTime const& theFederateTime)
        throw (rti1516e::FederateInternalError);

    virtual void timeAdvanceGrant(rti1516e::LogicalTime const& theTime)
        throw (rti1516e::FederateInternalError);

    virtual void announceSynchronizationPoint(
        std::wstring const& synchronizationPointLabel,
        rti1516e::VariableLengthData const& theUserSuppliedTag)
        throw (rti1516e::FederateInternalError);

    virtual void federationSynchronized(
        std::wstring const& synchronizationPointLabel,
        rti1516e::FederateHandleSet const& failedToSyncSet)
        throw (rti1516e::FederateInternalError);

    virtual void attributeOwnershipAcquisitionNotification(
        rti1516e::ObjectInstanceHandle theObject,
        rti1516e::AttributeHandleSet const& securedAttributes,
        rti1516e::VariableLengthData const& theUserSuppliedTag)
        throw (rti1516e::FederateInternalError);

    virtual void requestAttributeOwnershipAssumption(
        rti1516e::ObjectInstanceHandle theObject,
        rti1516e::AttributeHandleSet const& offeredAttributes,
        rti1516e::VariableLengthData const& theUserSuppliedTag)
        throw (rti1516e::FederateInternalError);

    virtual void informAttributeOwnership(
        rti1516e::ObjectInstanceHandle theObject,
        rti1516e::AttributeHandle theAttribute,
        rti1516e::FederateHandle theOwner)
        throw (rti1516e::FederateInternalError);

    virtual void attributeIsNotOwned(
        rti1516e::ObjectInstanceHandle theObject,
        rti1516e::AttributeHandle theAttribute)
        throw (rti1516e::FederateInternalError);

    virtual void attributeOwnershipUnavailable(
        rti1516e::ObjectInstanceHandle theObject,
        rti1516e::AttributeHandleSet const& theAttributes)
        throw (rti1516e::FederateInternalError);

    virtual void requestAttributeOwnershipRelease(
        rti1516e::ObjectInstanceHandle theObject,
        rti1516e::AttributeHandleSet const& candidateAttributes,
        rti1516e::VariableLengthData const& theUserSuppliedTag)
        throw (rti1516e::FederateInternalError);

    virtual void requestDivestitureConfirmation(
        rti1516e::ObjectInstanceHandle theObject,
        rti1516e::AttributeHandleSet const& releasedAttributes)
        throw (rti1516e::FederateInternalError);

    virtual void confirmAttributeOwnershipAcquisitionCancellation(
        rti1516e::ObjectInstanceHandle theObject,
        rti1516e::AttributeHandleSet const& theAttributes)
        throw (rti1516e::FederateInternalError);

private:
    SmokeSession& session_;
};

class SmokeSession {
public:
    SmokeSession()
        : factory_(), rti_(factory_.createRTIambassador()), ambassador_(*this)
    {
    }

    int intern_federate_handle(rti1516e::FederateHandle handle)
    {
        return federate_handles_.intern(handle);
    }

    int intern_object_class_handle(rti1516e::ObjectClassHandle handle)
    {
        return object_class_handles_.intern(handle);
    }

    int intern_attribute_handle(rti1516e::AttributeHandle handle)
    {
        return attribute_handles_.intern(handle);
    }

    int intern_interaction_class_handle(rti1516e::InteractionClassHandle handle)
    {
        return interaction_class_handles_.intern(handle);
    }

    int intern_parameter_handle(rti1516e::ParameterHandle handle)
    {
        return parameter_handles_.intern(handle);
    }

    int intern_object_instance_handle(rti1516e::ObjectInstanceHandle handle)
    {
        return object_instance_handles_.intern(handle);
    }

    int intern_retraction_handle(rti1516e::MessageRetractionHandle handle)
    {
        return retraction_handles_.intern(handle);
    }

    rti1516e::FederateHandle resolve_federate_handle(int id) const
    {
        return federate_handles_.resolve(id);
    }

    rti1516e::ObjectClassHandle resolve_object_class_handle(int id) const
    {
        return object_class_handles_.resolve(id);
    }

    rti1516e::AttributeHandle resolve_attribute_handle(int id) const
    {
        return attribute_handles_.resolve(id);
    }

    rti1516e::InteractionClassHandle resolve_interaction_class_handle(int id) const
    {
        return interaction_class_handles_.resolve(id);
    }

    rti1516e::ParameterHandle resolve_parameter_handle(int id) const
    {
        return parameter_handles_.resolve(id);
    }

    rti1516e::ObjectInstanceHandle resolve_object_instance_handle(int id) const
    {
        return object_instance_handles_.resolve(id);
    }

    rti1516e::MessageRetractionHandle resolve_retraction_handle(int id) const
    {
        return retraction_handles_.resolve(id);
    }

    void enqueue_event(PendingEvent const& event)
    {
        pending_events_.push_back(event);
    }

    std::string logical_time_name() const
    {
        return logical_time_name_.empty() ? "HLAfloat64Time" : logical_time_name_;
    }

    void connect(const std::vector<std::string>& fields)
    {
        const std::string callback_model = fields.size() >= 2 ? percent_decode(fields[1]) : "HLA_EVOKED";
        const std::string local_settings = fields.size() >= 3 ? percent_decode(fields[2]) : "";
        rti_->connect(ambassador_, callback_model == "HLA_IMMEDIATE" ? rti1516e::HLA_IMMEDIATE : rti1516e::HLA_EVOKED, widen_ascii(local_settings));
        ok();
    }

    void create(const std::vector<std::string>& fields)
    {
        const std::wstring federation_name = widen_ascii(percent_decode(fields.at(1)));
        logical_time_name_ = fields.size() >= 3 ? percent_decode(fields.at(2)) : "";
        const std::wstring logical_time_name = widen_ascii(logical_time_name_);
        std::vector<std::wstring> fom_modules;
        for (std::size_t i = 3; i < fields.size(); ++i) {
            fom_modules.push_back(widen_ascii(percent_decode(fields[i])));
        }
        rti_->createFederationExecution(federation_name, fom_modules, logical_time_name);
        ok();
    }

    void destroy(const std::vector<std::string>& fields)
    {
        rti_->destroyFederationExecution(widen_ascii(percent_decode(fields.at(1))));
        ok();
    }

    void join(const std::vector<std::string>& fields)
    {
        const std::string federate_name = percent_decode(fields.at(1));
        const std::wstring federate_type = widen_ascii(percent_decode(fields.at(2)));
        const std::wstring federation_name = widen_ascii(percent_decode(fields.at(3)));
        std::vector<std::wstring> additional_foms;
        for (std::size_t i = 4; i < fields.size(); ++i) {
            additional_foms.push_back(widen_ascii(percent_decode(fields[i])));
        }
        rti1516e::FederateHandle handle =
            federate_name.empty() ? rti_->joinFederationExecution(federate_type, federation_name, additional_foms)
                                  : rti_->joinFederationExecution(widen_ascii(federate_name), federate_type, federation_name, additional_foms);
        ok(std::to_string(intern_federate_handle(handle)));
    }

    void resign(const std::vector<std::string>& fields)
    {
        const std::string action_name = percent_decode(fields.at(1));
        rti1516e::ResignAction action = rti1516e::NO_ACTION;
        if (action_name == "UNCONDITIONALLY_DIVEST_ATTRIBUTES") {
            action = rti1516e::UNCONDITIONALLY_DIVEST_ATTRIBUTES;
        } else if (action_name == "DELETE_OBJECTS") {
            action = rti1516e::DELETE_OBJECTS;
        } else if (action_name == "CANCEL_PENDING_OWNERSHIP_ACQUISITIONS") {
            action = rti1516e::CANCEL_PENDING_OWNERSHIP_ACQUISITIONS;
        } else if (action_name == "DELETE_OBJECTS_THEN_DIVEST") {
            action = rti1516e::DELETE_OBJECTS_THEN_DIVEST;
        } else if (action_name == "CANCEL_THEN_DELETE_THEN_DIVEST") {
            action = rti1516e::CANCEL_THEN_DELETE_THEN_DIVEST;
        }
        rti_->resignFederationExecution(action);
        ok();
    }

    void disconnect()
    {
        rti_->disconnect();
        ok();
    }

    void get_hla_version()
    {
        ok("IEEE 1516-2010");
    }

    void get_federate_handle(const std::vector<std::string>& fields)
    {
        rti1516e::FederateHandle handle = rti_->getFederateHandle(widen_ascii(percent_decode(fields.at(1))));
        ok(std::to_string(intern_federate_handle(handle)));
    }

    void get_federate_name(const std::vector<std::string>& fields)
    {
        ok(narrow_ascii(rti_->getFederateName(resolve_federate_handle(std::atoi(percent_decode(fields.at(1)).c_str())))));
    }

    void get_object_class_handle(const std::vector<std::string>& fields)
    {
        rti1516e::ObjectClassHandle handle = rti_->getObjectClassHandle(widen_ascii(percent_decode(fields.at(1))));
        ok(std::to_string(intern_object_class_handle(handle)));
    }

    void get_object_class_name(const std::vector<std::string>& fields)
    {
        ok(narrow_ascii(rti_->getObjectClassName(resolve_object_class_handle(std::atoi(percent_decode(fields.at(1)).c_str())))));
    }

    void get_attribute_handle(const std::vector<std::string>& fields)
    {
        rti1516e::AttributeHandle handle = rti_->getAttributeHandle(
            resolve_object_class_handle(std::atoi(percent_decode(fields.at(1)).c_str())),
            widen_ascii(percent_decode(fields.at(2))));
        ok(std::to_string(intern_attribute_handle(handle)));
    }

    void get_attribute_name(const std::vector<std::string>& fields)
    {
        ok(narrow_ascii(rti_->getAttributeName(
            resolve_object_class_handle(std::atoi(percent_decode(fields.at(1)).c_str())),
            resolve_attribute_handle(std::atoi(percent_decode(fields.at(2)).c_str())))));
    }

    void publish_object_class_attributes(const std::vector<std::string>& fields)
    {
        rti_->publishObjectClassAttributes(
            resolve_object_class_handle(std::atoi(percent_decode(fields.at(1)).c_str())),
            parse_attribute_handle_set(percent_decode(fields.at(2))));
        ok();
    }

    void subscribe_object_class_attributes(const std::vector<std::string>& fields)
    {
        rti_->subscribeObjectClassAttributes(
            resolve_object_class_handle(std::atoi(percent_decode(fields.at(1)).c_str())),
            parse_attribute_handle_set(percent_decode(fields.at(2))));
        ok();
    }

    void register_object_instance(const std::vector<std::string>& fields)
    {
        rti1516e::ObjectClassHandle object_class = resolve_object_class_handle(std::atoi(percent_decode(fields.at(1)).c_str()));
        rti1516e::ObjectInstanceHandle handle =
            (fields.size() >= 3 && !percent_decode(fields.at(2)).empty())
                ? rti_->registerObjectInstance(object_class, widen_ascii(percent_decode(fields.at(2))))
                : rti_->registerObjectInstance(object_class);
        ok(std::to_string(intern_object_instance_handle(handle)));
    }

    void get_object_instance_handle(const std::vector<std::string>& fields)
    {
        rti1516e::ObjectInstanceHandle handle = rti_->getObjectInstanceHandle(widen_ascii(percent_decode(fields.at(1))));
        ok(std::to_string(intern_object_instance_handle(handle)));
    }

    void get_object_instance_name(const std::vector<std::string>& fields)
    {
        ok(narrow_ascii(rti_->getObjectInstanceName(resolve_object_instance_handle(std::atoi(percent_decode(fields.at(1)).c_str())))));
    }

    void get_known_object_class_handle(const std::vector<std::string>& fields)
    {
        rti1516e::ObjectClassHandle handle = rti_->getKnownObjectClassHandle(resolve_object_instance_handle(std::atoi(percent_decode(fields.at(1)).c_str())));
        ok(std::to_string(intern_object_class_handle(handle)));
    }

    void update_attribute_values(const std::vector<std::string>& fields)
    {
        rti_->updateAttributeValues(
            resolve_object_instance_handle(std::atoi(percent_decode(fields.at(1)).c_str())),
            parse_attribute_value_map(percent_decode(fields.at(2))),
            make_variable_length_data(hex_decode_string(percent_decode(fields.at(3)))));
        ok();
    }

    void update_attribute_values_timestamp(const std::vector<std::string>& fields)
    {
        RTI1516fedTime timestamp(parse_logical_time_argument(fields));
        rti1516e::MessageRetractionHandle handle = rti_->updateAttributeValues(
            resolve_object_instance_handle(std::atoi(percent_decode(fields.at(1)).c_str())),
            parse_attribute_value_map(percent_decode(fields.at(2))),
            make_variable_length_data(hex_decode_string(percent_decode(fields.at(3)))),
            timestamp);
        ok(std::to_string(intern_retraction_handle(handle)));
    }

    void change_attribute_order_type(const std::vector<std::string>& fields)
    {
        rti_->changeAttributeOrderType(
            resolve_object_instance_handle(std::atoi(percent_decode(fields.at(1)).c_str())),
            parse_attribute_handle_set(percent_decode(fields.at(2))),
            parse_order_type_name(percent_decode(fields.at(3))));
        ok();
    }

    void get_interaction_class_handle(const std::vector<std::string>& fields)
    {
        rti1516e::InteractionClassHandle handle = rti_->getInteractionClassHandle(widen_ascii(percent_decode(fields.at(1))));
        ok(std::to_string(intern_interaction_class_handle(handle)));
    }

    void get_interaction_class_name(const std::vector<std::string>& fields)
    {
        ok(narrow_ascii(rti_->getInteractionClassName(resolve_interaction_class_handle(std::atoi(percent_decode(fields.at(1)).c_str())))));
    }

    void get_parameter_handle(const std::vector<std::string>& fields)
    {
        rti1516e::ParameterHandle handle = rti_->getParameterHandle(
            resolve_interaction_class_handle(std::atoi(percent_decode(fields.at(1)).c_str())),
            widen_ascii(percent_decode(fields.at(2))));
        ok(std::to_string(intern_parameter_handle(handle)));
    }

    void get_parameter_name(const std::vector<std::string>& fields)
    {
        ok(narrow_ascii(rti_->getParameterName(
            resolve_interaction_class_handle(std::atoi(percent_decode(fields.at(1)).c_str())),
            resolve_parameter_handle(std::atoi(percent_decode(fields.at(2)).c_str())))));
    }

    void publish_interaction_class(const std::vector<std::string>& fields)
    {
        rti_->publishInteractionClass(resolve_interaction_class_handle(std::atoi(percent_decode(fields.at(1)).c_str())));
        ok();
    }

    void subscribe_interaction_class(const std::vector<std::string>& fields)
    {
        rti_->subscribeInteractionClass(resolve_interaction_class_handle(std::atoi(percent_decode(fields.at(1)).c_str())));
        ok();
    }

    void send_interaction(const std::vector<std::string>& fields)
    {
        rti_->sendInteraction(
            resolve_interaction_class_handle(std::atoi(percent_decode(fields.at(1)).c_str())),
            parse_parameter_value_map(percent_decode(fields.at(2))),
            make_variable_length_data(hex_decode_string(percent_decode(fields.at(3)))));
        ok();
    }

    void send_interaction_timestamp(const std::vector<std::string>& fields)
    {
        RTI1516fedTime timestamp(parse_logical_time_argument(fields));
        rti1516e::MessageRetractionHandle handle = rti_->sendInteraction(
            resolve_interaction_class_handle(std::atoi(percent_decode(fields.at(1)).c_str())),
            parse_parameter_value_map(percent_decode(fields.at(2))),
            make_variable_length_data(hex_decode_string(percent_decode(fields.at(3)))),
            timestamp);
        ok(std::to_string(intern_retraction_handle(handle)));
    }

    void change_interaction_order_type(const std::vector<std::string>& fields)
    {
        rti_->changeInteractionOrderType(
            resolve_interaction_class_handle(std::atoi(percent_decode(fields.at(1)).c_str())),
            parse_order_type_name(percent_decode(fields.at(2))));
        ok();
    }

    void enable_time_regulation(const std::vector<std::string>& fields)
    {
        RTI1516fedTimeInterval lookahead(parse_logical_time_argument(fields));
        rti_->enableTimeRegulation(lookahead);
        ok();
    }

    void enable_time_constrained()
    {
        rti_->enableTimeConstrained();
        ok();
    }

    void register_federation_synchronization_point(const std::vector<std::string>& fields)
    {
        const std::wstring label = widen_ascii(percent_decode(fields.at(1)));
        const std::string tag = hex_decode_string(percent_decode(fields.at(2)));
        rti1516e::VariableLengthData user_tag = make_variable_length_data(tag);
        if (fields.size() >= 4 && !percent_decode(fields.at(3)).empty()) {
            rti_->registerFederationSynchronizationPoint(label, user_tag, parse_federate_handle_set(percent_decode(fields.at(3))));
        } else {
            rti_->registerFederationSynchronizationPoint(label, user_tag);
        }
        ok();
    }

    void synchronization_point_achieved(const std::vector<std::string>& fields)
    {
        const std::wstring label = widen_ascii(percent_decode(fields.at(1)));
        bool successful = true;
        if (fields.size() >= 3) {
            const std::string flag = percent_decode(fields.at(2));
            successful = !(flag == "0" || flag == "false" || flag == "False");
        }
        rti_->synchronizationPointAchieved(label, successful);
        ok();
    }

    void unconditional_attribute_ownership_divestiture(const std::vector<std::string>& fields)
    {
        rti_->unconditionalAttributeOwnershipDivestiture(
            resolve_object_instance_handle(std::atoi(percent_decode(fields.at(1)).c_str())),
            parse_attribute_handle_set(percent_decode(fields.at(2))));
        ok();
    }

    void negotiated_attribute_ownership_divestiture(const std::vector<std::string>& fields)
    {
        const std::string tag = hex_decode_string(percent_decode(fields.at(3)));
        rti_->negotiatedAttributeOwnershipDivestiture(
            resolve_object_instance_handle(std::atoi(percent_decode(fields.at(1)).c_str())),
            parse_attribute_handle_set(percent_decode(fields.at(2))),
            make_variable_length_data(tag));
        ok();
    }

    void confirm_divestiture(const std::vector<std::string>& fields)
    {
        const std::string tag = hex_decode_string(percent_decode(fields.at(3)));
        rti_->confirmDivestiture(
            resolve_object_instance_handle(std::atoi(percent_decode(fields.at(1)).c_str())),
            parse_attribute_handle_set(percent_decode(fields.at(2))),
            make_variable_length_data(tag));
        ok();
    }

    void attribute_ownership_acquisition(const std::vector<std::string>& fields)
    {
        const std::string tag = hex_decode_string(percent_decode(fields.at(3)));
        rti_->attributeOwnershipAcquisition(
            resolve_object_instance_handle(std::atoi(percent_decode(fields.at(1)).c_str())),
            parse_attribute_handle_set(percent_decode(fields.at(2))),
            make_variable_length_data(tag));
        ok();
    }

    void attribute_ownership_acquisition_if_available(const std::vector<std::string>& fields)
    {
        rti_->attributeOwnershipAcquisitionIfAvailable(
            resolve_object_instance_handle(std::atoi(percent_decode(fields.at(1)).c_str())),
            parse_attribute_handle_set(percent_decode(fields.at(2))));
        ok();
    }

    void attribute_ownership_release_denied(const std::vector<std::string>& fields)
    {
        rti_->attributeOwnershipReleaseDenied(
            resolve_object_instance_handle(std::atoi(percent_decode(fields.at(1)).c_str())),
            parse_attribute_handle_set(percent_decode(fields.at(2))));
        ok();
    }

    void attribute_ownership_divestiture_if_wanted(const std::vector<std::string>& fields)
    {
        rti1516e::AttributeHandleSet divested;
        rti_->attributeOwnershipDivestitureIfWanted(
            resolve_object_instance_handle(std::atoi(percent_decode(fields.at(1)).c_str())),
            parse_attribute_handle_set(percent_decode(fields.at(2))),
            divested);
        std::vector<int> handles;
        for (rti1516e::AttributeHandleSet::const_iterator it = divested.begin(); it != divested.end(); ++it) {
            handles.push_back(intern_attribute_handle(*it));
        }
        ok(encode_handle_list(handles));
    }

    void cancel_negotiated_attribute_ownership_divestiture(const std::vector<std::string>& fields)
    {
        rti_->cancelNegotiatedAttributeOwnershipDivestiture(
            resolve_object_instance_handle(std::atoi(percent_decode(fields.at(1)).c_str())),
            parse_attribute_handle_set(percent_decode(fields.at(2))));
        ok();
    }

    void cancel_attribute_ownership_acquisition(const std::vector<std::string>& fields)
    {
        rti_->cancelAttributeOwnershipAcquisition(
            resolve_object_instance_handle(std::atoi(percent_decode(fields.at(1)).c_str())),
            parse_attribute_handle_set(percent_decode(fields.at(2))));
        ok();
    }

    void query_attribute_ownership(const std::vector<std::string>& fields)
    {
        rti_->queryAttributeOwnership(
            resolve_object_instance_handle(std::atoi(percent_decode(fields.at(1)).c_str())),
            resolve_attribute_handle(std::atoi(percent_decode(fields.at(2)).c_str())));
        ok();
    }

    void is_attribute_owned_by_federate(const std::vector<std::string>& fields)
    {
        const bool owned = rti_->isAttributeOwnedByFederate(
            resolve_object_instance_handle(std::atoi(percent_decode(fields.at(1)).c_str())),
            resolve_attribute_handle(std::atoi(percent_decode(fields.at(2)).c_str())));
        ok(owned ? "1" : "0");
    }

    static double parse_logical_time_argument(const std::vector<std::string>& fields)
    {
        return std::atof(percent_decode(fields.back()).c_str());
    }

    void time_advance_request(const std::vector<std::string>& fields)
    {
        RTI1516fedTime timestamp(parse_logical_time_argument(fields));
        rti_->timeAdvanceRequest(timestamp);
        ok();
    }

    void time_advance_request_available(const std::vector<std::string>& fields)
    {
        RTI1516fedTime timestamp(parse_logical_time_argument(fields));
        rti_->timeAdvanceRequestAvailable(timestamp);
        ok();
    }

    void next_message_request(const std::vector<std::string>& fields)
    {
        RTI1516fedTime timestamp(parse_logical_time_argument(fields));
        rti_->nextMessageRequest(timestamp);
        ok();
    }

    void next_message_request_available(const std::vector<std::string>& fields)
    {
        RTI1516fedTime timestamp(parse_logical_time_argument(fields));
        rti_->nextMessageRequestAvailable(timestamp);
        ok();
    }

    void flush_queue_request(const std::vector<std::string>& fields)
    {
        RTI1516fedTime timestamp(parse_logical_time_argument(fields));
        rti_->flushQueueRequest(timestamp);
        ok();
    }

    void query_galt()
    {
        RTI1516fedTime timestamp(0.0);
        const bool valid = rti_->queryGALT(timestamp);
        std::ostringstream stream;
        stream << logical_time_to_wire_string(timestamp, logical_time_name());
        ok(std::vector<std::string>{valid ? "1" : "0", logical_time_name(), stream.str()});
    }

    void query_lits()
    {
        RTI1516fedTime timestamp(0.0);
        const bool valid = rti_->queryLITS(timestamp);
        std::ostringstream stream;
        stream << logical_time_to_wire_string(timestamp, logical_time_name());
        ok(std::vector<std::string>{valid ? "1" : "0", logical_time_name(), stream.str()});
    }

    void evoke(const std::vector<std::string>& fields)
    {
        bool evoked = rti_->evokeCallback(std::atof(percent_decode(fields.at(1)).c_str()));
        emit_callback_result(evoked);
    }

    void evoke_many(const std::vector<std::string>& fields)
    {
        bool evoked = rti_->evokeMultipleCallbacks(
            std::atof(percent_decode(fields.at(1)).c_str()),
            std::atof(percent_decode(fields.at(2)).c_str()));
        emit_callback_result(evoked);
    }

private:
    static rti1516e::VariableLengthData make_variable_length_data(const std::string& text)
    {
        return rti1516e::VariableLengthData(text.data(), text.size());
    }

    rti1516e::AttributeHandleSet parse_attribute_handle_set(const std::string& spec) const
    {
        rti1516e::AttributeHandleSet result;
        std::vector<std::string> parts = split_char(spec, ',');
        for (std::vector<std::string>::const_iterator it = parts.begin(); it != parts.end(); ++it) {
            if (!it->empty()) {
                result.insert(resolve_attribute_handle(std::atoi(it->c_str())));
            }
        }
        return result;
    }

    rti1516e::FederateHandleSet parse_federate_handle_set(const std::string& spec) const
    {
        rti1516e::FederateHandleSet result;
        std::vector<std::string> parts = split_char(spec, ',');
        for (std::vector<std::string>::const_iterator it = parts.begin(); it != parts.end(); ++it) {
            if (!it->empty()) {
                result.insert(resolve_federate_handle(std::atoi(it->c_str())));
            }
        }
        return result;
    }

    rti1516e::AttributeHandleValueMap parse_attribute_value_map(const std::string& spec) const
    {
        rti1516e::AttributeHandleValueMap result;
        std::vector<std::string> entries = split_char(spec, ',');
        for (std::vector<std::string>::const_iterator it = entries.begin(); it != entries.end(); ++it) {
            if (it->empty()) {
                continue;
            }
            std::size_t colon = it->find(':');
            if (colon == std::string::npos) {
                throw std::runtime_error("Invalid attribute value map entry");
            }
            int id = std::atoi(it->substr(0, colon).c_str());
            std::string bytes = hex_decode_string(it->substr(colon + 1));
            result[resolve_attribute_handle(id)] = make_variable_length_data(bytes);
        }
        return result;
    }

    rti1516e::ParameterHandleValueMap parse_parameter_value_map(const std::string& spec) const
    {
        rti1516e::ParameterHandleValueMap result;
        std::vector<std::string> entries = split_char(spec, ',');
        for (std::vector<std::string>::const_iterator it = entries.begin(); it != entries.end(); ++it) {
            if (it->empty()) {
                continue;
            }
            std::size_t colon = it->find(':');
            if (colon == std::string::npos) {
                throw std::runtime_error("Invalid parameter value map entry");
            }
            int id = std::atoi(it->substr(0, colon).c_str());
            std::string bytes = hex_decode_string(it->substr(colon + 1));
            result[resolve_parameter_handle(id)] = make_variable_length_data(bytes);
        }
        return result;
    }

    void emit_callback_result(bool evoked)
    {
        if (pending_events_.empty()) {
            ok(std::vector<std::string>(1, evoked ? "1" : "0"));
            return;
        }
        PendingEvent event = pending_events_.front();
        pending_events_.pop_front();
        std::vector<std::string> payload;
        payload.push_back("1");
        payload.push_back(event.kind);
        if (event.kind == "DISCOVER") {
            payload.push_back(std::to_string(event.primary_handle));
            payload.push_back(std::to_string(event.secondary_handle));
            payload.push_back(event.object_name);
        } else if (event.kind == "ANNOUNCE_SYNC_POINT") {
            payload.push_back(event.object_name);
            payload.push_back(event.tag_hex);
        } else if (event.kind == "FEDERATION_SYNCHRONIZED") {
            payload.push_back(event.object_name);
            payload.push_back(encode_handle_list(event.handles));
        } else if (event.kind == "OWNERSHIP_ACQUIRED") {
            payload.push_back(std::to_string(event.primary_handle));
            payload.push_back(encode_handle_list(event.handles));
            payload.push_back(event.tag_hex);
        } else if (event.kind == "REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION") {
            payload.push_back(std::to_string(event.primary_handle));
            payload.push_back(encode_handle_list(event.handles));
            payload.push_back(event.tag_hex);
        } else if (event.kind == "INFORM_ATTRIBUTE_OWNERSHIP") {
            payload.push_back(std::to_string(event.primary_handle));
            payload.push_back(std::to_string(event.secondary_handle));
            payload.push_back(std::to_string(event.tertiary_handle));
        } else if (event.kind == "ATTRIBUTE_IS_NOT_OWNED") {
            payload.push_back(std::to_string(event.primary_handle));
            payload.push_back(std::to_string(event.secondary_handle));
        } else if (
            event.kind == "ATTRIBUTE_OWNERSHIP_UNAVAILABLE" ||
            event.kind == "REQUEST_DIVESTITURE_CONFIRMATION" ||
            event.kind == "CONFIRM_ATTRIBUTE_OWNERSHIP_ACQUISITION_CANCELLATION") {
            payload.push_back(std::to_string(event.primary_handle));
            payload.push_back(encode_handle_list(event.handles));
        } else if (event.kind == "REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE") {
            payload.push_back(std::to_string(event.primary_handle));
            payload.push_back(encode_handle_list(event.handles));
            payload.push_back(event.tag_hex);
        } else if (event.kind == "TIME_REGULATION_ENABLED" || event.kind == "TIME_CONSTRAINED_ENABLED" || event.kind == "TIME_ADVANCE_GRANT") {
            payload.push_back(event.time_type);
            payload.push_back(event.time_value);
        } else if (event.kind == "REFLECT_TSO" || event.kind == "INTERACTION_TSO") {
            payload.push_back(std::to_string(event.primary_handle));
            payload.push_back(encode_value_pairs(event.values));
            payload.push_back(event.tag_hex);
            payload.push_back(std::to_string(event.order));
            payload.push_back(std::to_string(event.transportation));
            payload.push_back(event.time_type);
            payload.push_back(event.time_value);
            payload.push_back(std::to_string(event.received_order));
        } else {
            payload.push_back(std::to_string(event.primary_handle));
            payload.push_back(encode_value_pairs(event.values));
            payload.push_back(event.tag_hex);
            payload.push_back(std::to_string(event.order));
            payload.push_back(std::to_string(event.transportation));
        }
        ok(payload);
    }

    static std::string encode_value_pairs(const std::vector<std::pair<int, std::string> >& values)
    {
        std::ostringstream stream;
        for (std::size_t i = 0; i < values.size(); ++i) {
            if (i != 0) {
                stream << ',';
            }
            stream << values[i].first << ':' << values[i].second;
        }
        return stream.str();
    }

    static std::string encode_handle_list(const std::vector<int>& handles)
    {
        std::ostringstream stream;
        for (std::size_t i = 0; i < handles.size(); ++i) {
            if (i != 0) {
                stream << ',';
            }
            stream << handles[i];
        }
        return stream.str();
    }

    rti1516e::RTIambassadorFactory factory_;
    std::auto_ptr<rti1516e::RTIambassador> rti_;
    QueueingFederateAmbassador ambassador_;
    HandleRegistry<rti1516e::FederateHandle> federate_handles_;
    HandleRegistry<rti1516e::ObjectClassHandle> object_class_handles_;
    HandleRegistry<rti1516e::AttributeHandle> attribute_handles_;
    HandleRegistry<rti1516e::InteractionClassHandle> interaction_class_handles_;
    HandleRegistry<rti1516e::ParameterHandle> parameter_handles_;
    HandleRegistry<rti1516e::ObjectInstanceHandle> object_instance_handles_;
    HandleRegistry<rti1516e::MessageRetractionHandle> retraction_handles_;
    std::deque<PendingEvent> pending_events_;
    std::string logical_time_name_;
};

std::string logical_time_to_wire_string(rti1516e::LogicalTime const& logical_time, const std::string& logical_time_name)
{
    const std::string text = narrow_ascii(logical_time.toString());
    if (logical_time_name == "HLAinteger64Time") {
        const long long value = static_cast<long long>(std::llround(std::atof(text.c_str())));
        return std::to_string(value);
    }
    return text;
}

void QueueingFederateAmbassador::discoverObjectInstance(
    rti1516e::ObjectInstanceHandle theObject,
    rti1516e::ObjectClassHandle theObjectClass,
    std::wstring const& theObjectInstanceName)
    throw (rti1516e::FederateInternalError)
{
    PendingEvent event;
    event.kind = "DISCOVER";
    event.primary_handle = session_.intern_object_instance_handle(theObject);
    event.secondary_handle = session_.intern_object_class_handle(theObjectClass);
    event.object_name = narrow_ascii(theObjectInstanceName);
    session_.enqueue_event(event);
}

void QueueingFederateAmbassador::reflectAttributeValues(
    rti1516e::ObjectInstanceHandle theObject,
    rti1516e::AttributeHandleValueMap const& theAttributeValues,
    rti1516e::VariableLengthData const& theUserSuppliedTag,
    rti1516e::OrderType sentOrder,
    rti1516e::TransportationType theType,
    rti1516e::SupplementalReflectInfo)
    throw (rti1516e::FederateInternalError)
{
    PendingEvent event;
    event.kind = "REFLECT";
    event.primary_handle = session_.intern_object_instance_handle(theObject);
    for (rti1516e::AttributeHandleValueMap::const_iterator it = theAttributeValues.begin(); it != theAttributeValues.end(); ++it) {
        event.values.push_back(std::make_pair(session_.intern_attribute_handle(it->first), hex_encode_variable_length_data(it->second)));
    }
    event.tag_hex = hex_encode_variable_length_data(theUserSuppliedTag);
    event.order = static_cast<int>(sentOrder);
    event.transportation = static_cast<int>(theType);
    session_.enqueue_event(event);
}

void QueueingFederateAmbassador::reflectAttributeValues(
    rti1516e::ObjectInstanceHandle theObject,
    rti1516e::AttributeHandleValueMap const& theAttributeValues,
    rti1516e::VariableLengthData const& theUserSuppliedTag,
    rti1516e::OrderType,
    rti1516e::TransportationType theType,
    rti1516e::LogicalTime const& theTime,
    rti1516e::OrderType receivedOrder,
    rti1516e::SupplementalReflectInfo)
    throw (rti1516e::FederateInternalError)
{
    PendingEvent event;
    event.kind = "REFLECT_TSO";
    event.primary_handle = session_.intern_object_instance_handle(theObject);
    for (rti1516e::AttributeHandleValueMap::const_iterator it = theAttributeValues.begin(); it != theAttributeValues.end(); ++it) {
        event.values.push_back(std::make_pair(session_.intern_attribute_handle(it->first), hex_encode_variable_length_data(it->second)));
    }
    event.tag_hex = hex_encode_variable_length_data(theUserSuppliedTag);
    event.order = static_cast<int>(rti1516e::TIMESTAMP);
    event.received_order = static_cast<int>(receivedOrder);
    event.transportation = static_cast<int>(theType);
    event.time_type = session_.logical_time_name();
    event.time_value = logical_time_to_wire_string(theTime, event.time_type);
    session_.enqueue_event(event);
}

void QueueingFederateAmbassador::reflectAttributeValues(
    rti1516e::ObjectInstanceHandle theObject,
    rti1516e::AttributeHandleValueMap const& theAttributeValues,
    rti1516e::VariableLengthData const& theUserSuppliedTag,
    rti1516e::OrderType sentOrder,
    rti1516e::TransportationType theType,
    rti1516e::LogicalTime const& theTime,
    rti1516e::OrderType receivedOrder,
    rti1516e::MessageRetractionHandle,
    rti1516e::SupplementalReflectInfo theReflectInfo)
    throw (rti1516e::FederateInternalError)
{
    reflectAttributeValues(theObject, theAttributeValues, theUserSuppliedTag, sentOrder, theType, theTime, receivedOrder, theReflectInfo);
}

void QueueingFederateAmbassador::receiveInteraction(
    rti1516e::InteractionClassHandle theInteraction,
    rti1516e::ParameterHandleValueMap const& theParameterValues,
    rti1516e::VariableLengthData const& theUserSuppliedTag,
    rti1516e::OrderType sentOrder,
    rti1516e::TransportationType theType,
    rti1516e::SupplementalReceiveInfo)
    throw (rti1516e::FederateInternalError)
{
    PendingEvent event;
    event.kind = "INTERACTION";
    event.primary_handle = session_.intern_interaction_class_handle(theInteraction);
    for (rti1516e::ParameterHandleValueMap::const_iterator it = theParameterValues.begin(); it != theParameterValues.end(); ++it) {
        event.values.push_back(std::make_pair(session_.intern_parameter_handle(it->first), hex_encode_variable_length_data(it->second)));
    }
    event.tag_hex = hex_encode_variable_length_data(theUserSuppliedTag);
    event.order = static_cast<int>(sentOrder);
    event.transportation = static_cast<int>(theType);
    session_.enqueue_event(event);
}

void QueueingFederateAmbassador::receiveInteraction(
    rti1516e::InteractionClassHandle theInteraction,
    rti1516e::ParameterHandleValueMap const& theParameterValues,
    rti1516e::VariableLengthData const& theUserSuppliedTag,
    rti1516e::OrderType,
    rti1516e::TransportationType theType,
    rti1516e::LogicalTime const& theTime,
    rti1516e::OrderType receivedOrder,
    rti1516e::SupplementalReceiveInfo)
    throw (rti1516e::FederateInternalError)
{
    PendingEvent event;
    event.kind = "INTERACTION_TSO";
    event.primary_handle = session_.intern_interaction_class_handle(theInteraction);
    for (rti1516e::ParameterHandleValueMap::const_iterator it = theParameterValues.begin(); it != theParameterValues.end(); ++it) {
        event.values.push_back(std::make_pair(session_.intern_parameter_handle(it->first), hex_encode_variable_length_data(it->second)));
    }
    event.tag_hex = hex_encode_variable_length_data(theUserSuppliedTag);
    event.order = static_cast<int>(rti1516e::TIMESTAMP);
    event.received_order = static_cast<int>(receivedOrder);
    event.transportation = static_cast<int>(theType);
    event.time_type = session_.logical_time_name();
    event.time_value = logical_time_to_wire_string(theTime, event.time_type);
    session_.enqueue_event(event);
}

void QueueingFederateAmbassador::receiveInteraction(
    rti1516e::InteractionClassHandle theInteraction,
    rti1516e::ParameterHandleValueMap const& theParameterValues,
    rti1516e::VariableLengthData const& theUserSuppliedTag,
    rti1516e::OrderType sentOrder,
    rti1516e::TransportationType theType,
    rti1516e::LogicalTime const& theTime,
    rti1516e::OrderType receivedOrder,
    rti1516e::MessageRetractionHandle,
    rti1516e::SupplementalReceiveInfo theReceiveInfo)
    throw (rti1516e::FederateInternalError)
{
    receiveInteraction(theInteraction, theParameterValues, theUserSuppliedTag, sentOrder, theType, theTime, receivedOrder, theReceiveInfo);
}

void QueueingFederateAmbassador::timeRegulationEnabled(rti1516e::LogicalTime const& theFederateTime)
    throw (rti1516e::FederateInternalError)
{
    PendingEvent event;
    event.kind = "TIME_REGULATION_ENABLED";
    event.time_type = session_.logical_time_name();
    event.time_value = logical_time_to_wire_string(theFederateTime, event.time_type);
    session_.enqueue_event(event);
}

void QueueingFederateAmbassador::timeConstrainedEnabled(rti1516e::LogicalTime const& theFederateTime)
    throw (rti1516e::FederateInternalError)
{
    PendingEvent event;
    event.kind = "TIME_CONSTRAINED_ENABLED";
    event.time_type = session_.logical_time_name();
    event.time_value = logical_time_to_wire_string(theFederateTime, event.time_type);
    session_.enqueue_event(event);
}

void QueueingFederateAmbassador::timeAdvanceGrant(rti1516e::LogicalTime const& theTime)
    throw (rti1516e::FederateInternalError)
{
    PendingEvent event;
    event.kind = "TIME_ADVANCE_GRANT";
    event.time_type = session_.logical_time_name();
    event.time_value = logical_time_to_wire_string(theTime, event.time_type);
    session_.enqueue_event(event);
}

void QueueingFederateAmbassador::announceSynchronizationPoint(
    std::wstring const& synchronizationPointLabel,
    rti1516e::VariableLengthData const& theUserSuppliedTag)
    throw (rti1516e::FederateInternalError)
{
    PendingEvent event;
    event.kind = "ANNOUNCE_SYNC_POINT";
    event.object_name = narrow_ascii(synchronizationPointLabel);
    event.tag_hex = hex_encode_variable_length_data(theUserSuppliedTag);
    session_.enqueue_event(event);
}

void QueueingFederateAmbassador::federationSynchronized(
    std::wstring const& synchronizationPointLabel,
    rti1516e::FederateHandleSet const& failedToSyncSet)
    throw (rti1516e::FederateInternalError)
{
    PendingEvent event;
    event.kind = "FEDERATION_SYNCHRONIZED";
    event.object_name = narrow_ascii(synchronizationPointLabel);
    for (rti1516e::FederateHandleSet::const_iterator it = failedToSyncSet.begin(); it != failedToSyncSet.end(); ++it) {
        event.handles.push_back(session_.intern_federate_handle(*it));
    }
    session_.enqueue_event(event);
}

void QueueingFederateAmbassador::attributeOwnershipAcquisitionNotification(
    rti1516e::ObjectInstanceHandle theObject,
    rti1516e::AttributeHandleSet const& securedAttributes,
    rti1516e::VariableLengthData const& theUserSuppliedTag)
    throw (rti1516e::FederateInternalError)
{
    PendingEvent event;
    event.kind = "OWNERSHIP_ACQUIRED";
    event.primary_handle = session_.intern_object_instance_handle(theObject);
    for (rti1516e::AttributeHandleSet::const_iterator it = securedAttributes.begin(); it != securedAttributes.end(); ++it) {
        event.handles.push_back(session_.intern_attribute_handle(*it));
    }
    event.tag_hex = hex_encode_variable_length_data(theUserSuppliedTag);
    session_.enqueue_event(event);
}

void QueueingFederateAmbassador::requestAttributeOwnershipAssumption(
    rti1516e::ObjectInstanceHandle theObject,
    rti1516e::AttributeHandleSet const& offeredAttributes,
    rti1516e::VariableLengthData const& theUserSuppliedTag)
    throw (rti1516e::FederateInternalError)
{
    PendingEvent event;
    event.kind = "REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION";
    event.primary_handle = session_.intern_object_instance_handle(theObject);
    for (rti1516e::AttributeHandleSet::const_iterator it = offeredAttributes.begin(); it != offeredAttributes.end(); ++it) {
        event.handles.push_back(session_.intern_attribute_handle(*it));
    }
    event.tag_hex = hex_encode_variable_length_data(theUserSuppliedTag);
    session_.enqueue_event(event);
}

void QueueingFederateAmbassador::informAttributeOwnership(
    rti1516e::ObjectInstanceHandle theObject,
    rti1516e::AttributeHandle theAttribute,
    rti1516e::FederateHandle theOwner)
    throw (rti1516e::FederateInternalError)
{
    PendingEvent event;
    event.kind = "INFORM_ATTRIBUTE_OWNERSHIP";
    event.primary_handle = session_.intern_object_instance_handle(theObject);
    event.secondary_handle = session_.intern_attribute_handle(theAttribute);
    event.tertiary_handle = session_.intern_federate_handle(theOwner);
    session_.enqueue_event(event);
}

void QueueingFederateAmbassador::attributeIsNotOwned(
    rti1516e::ObjectInstanceHandle theObject,
    rti1516e::AttributeHandle theAttribute)
    throw (rti1516e::FederateInternalError)
{
    PendingEvent event;
    event.kind = "ATTRIBUTE_IS_NOT_OWNED";
    event.primary_handle = session_.intern_object_instance_handle(theObject);
    event.secondary_handle = session_.intern_attribute_handle(theAttribute);
    session_.enqueue_event(event);
}

void QueueingFederateAmbassador::attributeOwnershipUnavailable(
    rti1516e::ObjectInstanceHandle theObject,
    rti1516e::AttributeHandleSet const& theAttributes)
    throw (rti1516e::FederateInternalError)
{
    PendingEvent event;
    event.kind = "ATTRIBUTE_OWNERSHIP_UNAVAILABLE";
    event.primary_handle = session_.intern_object_instance_handle(theObject);
    for (rti1516e::AttributeHandleSet::const_iterator it = theAttributes.begin(); it != theAttributes.end(); ++it) {
        event.handles.push_back(session_.intern_attribute_handle(*it));
    }
    session_.enqueue_event(event);
}

void QueueingFederateAmbassador::requestAttributeOwnershipRelease(
    rti1516e::ObjectInstanceHandle theObject,
    rti1516e::AttributeHandleSet const& candidateAttributes,
    rti1516e::VariableLengthData const& theUserSuppliedTag)
    throw (rti1516e::FederateInternalError)
{
    PendingEvent event;
    event.kind = "REQUEST_ATTRIBUTE_OWNERSHIP_RELEASE";
    event.primary_handle = session_.intern_object_instance_handle(theObject);
    for (rti1516e::AttributeHandleSet::const_iterator it = candidateAttributes.begin(); it != candidateAttributes.end(); ++it) {
        event.handles.push_back(session_.intern_attribute_handle(*it));
    }
    event.tag_hex = hex_encode_variable_length_data(theUserSuppliedTag);
    session_.enqueue_event(event);
}

void QueueingFederateAmbassador::requestDivestitureConfirmation(
    rti1516e::ObjectInstanceHandle theObject,
    rti1516e::AttributeHandleSet const& releasedAttributes)
    throw (rti1516e::FederateInternalError)
{
    PendingEvent event;
    event.kind = "REQUEST_DIVESTITURE_CONFIRMATION";
    event.primary_handle = session_.intern_object_instance_handle(theObject);
    for (rti1516e::AttributeHandleSet::const_iterator it = releasedAttributes.begin(); it != releasedAttributes.end(); ++it) {
        event.handles.push_back(session_.intern_attribute_handle(*it));
    }
    session_.enqueue_event(event);
}

void QueueingFederateAmbassador::confirmAttributeOwnershipAcquisitionCancellation(
    rti1516e::ObjectInstanceHandle theObject,
    rti1516e::AttributeHandleSet const& theAttributes)
    throw (rti1516e::FederateInternalError)
{
    PendingEvent event;
    event.kind = "CONFIRM_ATTRIBUTE_OWNERSHIP_ACQUISITION_CANCELLATION";
    event.primary_handle = session_.intern_object_instance_handle(theObject);
    for (rti1516e::AttributeHandleSet::const_iterator it = theAttributes.begin(); it != theAttributes.end(); ++it) {
        event.handles.push_back(session_.intern_attribute_handle(*it));
    }
    session_.enqueue_event(event);
}

} // namespace

int main()
{
    SmokeSession session;
    std::string line;
    while (std::getline(std::cin, line)) {
        if (line.empty()) {
            continue;
        }
        const std::vector<std::string> fields = split_tab(line);
        const std::string& command = fields.front();
        try {
            if (command == "CONNECT") {
                session.connect(fields);
            } else if (command == "CREATE") {
                session.create(fields);
            } else if (command == "DESTROY") {
                session.destroy(fields);
            } else if (command == "JOIN") {
                session.join(fields);
            } else if (command == "RESIGN") {
                session.resign(fields);
            } else if (command == "DISCONNECT") {
                session.disconnect();
            } else if (command == "GET_HLA_VERSION") {
                session.get_hla_version();
            } else if (command == "GET_FEDERATE_HANDLE") {
                session.get_federate_handle(fields);
            } else if (command == "GET_FEDERATE_NAME") {
                session.get_federate_name(fields);
            } else if (command == "GET_OBJECT_CLASS_HANDLE") {
                session.get_object_class_handle(fields);
            } else if (command == "GET_OBJECT_CLASS_NAME") {
                session.get_object_class_name(fields);
            } else if (command == "GET_ATTRIBUTE_HANDLE") {
                session.get_attribute_handle(fields);
            } else if (command == "GET_ATTRIBUTE_NAME") {
                session.get_attribute_name(fields);
            } else if (command == "PUBLISH_OBJECT_CLASS_ATTRIBUTES") {
                session.publish_object_class_attributes(fields);
            } else if (command == "SUBSCRIBE_OBJECT_CLASS_ATTRIBUTES") {
                session.subscribe_object_class_attributes(fields);
            } else if (command == "REGISTER_OBJECT_INSTANCE") {
                session.register_object_instance(fields);
            } else if (command == "GET_OBJECT_INSTANCE_HANDLE") {
                session.get_object_instance_handle(fields);
            } else if (command == "GET_OBJECT_INSTANCE_NAME") {
                session.get_object_instance_name(fields);
            } else if (command == "GET_KNOWN_OBJECT_CLASS_HANDLE") {
                session.get_known_object_class_handle(fields);
            } else if (command == "UPDATE_ATTRIBUTE_VALUES") {
                session.update_attribute_values(fields);
            } else if (command == "UPDATE_ATTRIBUTE_VALUES_TIMESTAMP") {
                session.update_attribute_values_timestamp(fields);
            } else if (command == "CHANGE_ATTRIBUTE_ORDER_TYPE") {
                session.change_attribute_order_type(fields);
            } else if (command == "GET_INTERACTION_CLASS_HANDLE") {
                session.get_interaction_class_handle(fields);
            } else if (command == "GET_INTERACTION_CLASS_NAME") {
                session.get_interaction_class_name(fields);
            } else if (command == "GET_PARAMETER_HANDLE") {
                session.get_parameter_handle(fields);
            } else if (command == "GET_PARAMETER_NAME") {
                session.get_parameter_name(fields);
            } else if (command == "PUBLISH_INTERACTION_CLASS") {
                session.publish_interaction_class(fields);
            } else if (command == "SUBSCRIBE_INTERACTION_CLASS") {
                session.subscribe_interaction_class(fields);
            } else if (command == "SEND_INTERACTION") {
                session.send_interaction(fields);
            } else if (command == "SEND_INTERACTION_TIMESTAMP") {
                session.send_interaction_timestamp(fields);
            } else if (command == "CHANGE_INTERACTION_ORDER_TYPE") {
                session.change_interaction_order_type(fields);
            } else if (command == "ENABLE_TIME_REGULATION") {
                session.enable_time_regulation(fields);
            } else if (command == "ENABLE_TIME_CONSTRAINED") {
                session.enable_time_constrained();
            } else if (command == "REGISTER_FEDERATION_SYNCHRONIZATION_POINT") {
                session.register_federation_synchronization_point(fields);
            } else if (command == "SYNCHRONIZATION_POINT_ACHIEVED") {
                session.synchronization_point_achieved(fields);
            } else if (command == "UNCONDITIONAL_ATTRIBUTE_OWNERSHIP_DIVESTITURE") {
                session.unconditional_attribute_ownership_divestiture(fields);
            } else if (command == "NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE") {
                session.negotiated_attribute_ownership_divestiture(fields);
            } else if (command == "CONFIRM_DIVESTITURE") {
                session.confirm_divestiture(fields);
            } else if (command == "ATTRIBUTE_OWNERSHIP_ACQUISITION") {
                session.attribute_ownership_acquisition(fields);
            } else if (command == "ATTRIBUTE_OWNERSHIP_ACQUISITION_IF_AVAILABLE") {
                session.attribute_ownership_acquisition_if_available(fields);
            } else if (command == "ATTRIBUTE_OWNERSHIP_RELEASE_DENIED") {
                session.attribute_ownership_release_denied(fields);
            } else if (command == "ATTRIBUTE_OWNERSHIP_DIVESTITURE_IF_WANTED") {
                session.attribute_ownership_divestiture_if_wanted(fields);
            } else if (command == "CANCEL_NEGOTIATED_ATTRIBUTE_OWNERSHIP_DIVESTITURE") {
                session.cancel_negotiated_attribute_ownership_divestiture(fields);
            } else if (command == "CANCEL_ATTRIBUTE_OWNERSHIP_ACQUISITION") {
                session.cancel_attribute_ownership_acquisition(fields);
            } else if (command == "QUERY_ATTRIBUTE_OWNERSHIP") {
                session.query_attribute_ownership(fields);
            } else if (command == "IS_ATTRIBUTE_OWNED_BY_FEDERATE") {
                session.is_attribute_owned_by_federate(fields);
            } else if (command == "TIME_ADVANCE_REQUEST") {
                session.time_advance_request(fields);
            } else if (command == "TIME_ADVANCE_REQUEST_AVAILABLE") {
                session.time_advance_request_available(fields);
            } else if (command == "NEXT_MESSAGE_REQUEST") {
                session.next_message_request(fields);
            } else if (command == "NEXT_MESSAGE_REQUEST_AVAILABLE") {
                session.next_message_request_available(fields);
            } else if (command == "FLUSH_QUEUE_REQUEST") {
                session.flush_queue_request(fields);
            } else if (command == "QUERY_GALT") {
                session.query_galt();
            } else if (command == "QUERY_LITS") {
                session.query_lits();
            } else if (command == "EVOKE") {
                session.evoke(fields);
            } else if (command == "EVOKE_MANY") {
                session.evoke_many(fields);
            } else if (command == "CLOSE") {
                ok();
                return 0;
            } else {
                error("RTIinternalError", widen_ascii("Unknown helper command: " + command));
            }
        }
        HANDLE_RTI_EXCEPTION(ConnectionFailed)
        HANDLE_RTI_EXCEPTION(InvalidLocalSettingsDesignator)
        HANDLE_RTI_EXCEPTION(UnsupportedCallbackModel)
        HANDLE_RTI_EXCEPTION(AlreadyConnected)
        HANDLE_RTI_EXCEPTION(CallNotAllowedFromWithinCallback)
        HANDLE_RTI_EXCEPTION(CouldNotCreateLogicalTimeFactory)
        HANDLE_RTI_EXCEPTION(InconsistentFDD)
        HANDLE_RTI_EXCEPTION(ErrorReadingFDD)
        HANDLE_RTI_EXCEPTION(CouldNotOpenFDD)
        HANDLE_RTI_EXCEPTION(FederationExecutionAlreadyExists)
        HANDLE_RTI_EXCEPTION(NotConnected)
        HANDLE_RTI_EXCEPTION(FederatesCurrentlyJoined)
        HANDLE_RTI_EXCEPTION(FederationExecutionDoesNotExist)
        HANDLE_RTI_EXCEPTION(SaveInProgress)
        HANDLE_RTI_EXCEPTION(RestoreInProgress)
        HANDLE_RTI_EXCEPTION(FederateAlreadyExecutionMember)
        HANDLE_RTI_EXCEPTION(FederateNameAlreadyInUse)
        HANDLE_RTI_EXCEPTION(InvalidResignAction)
        HANDLE_RTI_EXCEPTION(OwnershipAcquisitionPending)
        HANDLE_RTI_EXCEPTION(FederateOwnsAttributes)
        HANDLE_RTI_EXCEPTION(FederateNotExecutionMember)
        HANDLE_RTI_EXCEPTION(NameNotFound)
        HANDLE_RTI_EXCEPTION(ObjectInstanceNotKnown)
        HANDLE_RTI_EXCEPTION(InvalidObjectClassHandle)
        HANDLE_RTI_EXCEPTION(InvalidAttributeHandle)
        HANDLE_RTI_EXCEPTION(AttributeNotDefined)
        HANDLE_RTI_EXCEPTION(InvalidInteractionClassHandle)
        HANDLE_RTI_EXCEPTION(InvalidParameterHandle)
        HANDLE_RTI_EXCEPTION(InteractionParameterNotDefined)
        HANDLE_RTI_EXCEPTION(InvalidFederateHandle)
        HANDLE_RTI_EXCEPTION(FederateHandleNotKnown)
        HANDLE_RTI_EXCEPTION(ObjectClassNotPublished)
        HANDLE_RTI_EXCEPTION(ObjectClassNotDefined)
        HANDLE_RTI_EXCEPTION(InteractionClassNotPublished)
        HANDLE_RTI_EXCEPTION(InteractionClassNotDefined)
        HANDLE_RTI_EXCEPTION(ObjectInstanceNameInUse)
        HANDLE_RTI_EXCEPTION(ObjectInstanceNameNotReserved)
        HANDLE_RTI_EXCEPTION(ObjectInstanceNameInUse)
        HANDLE_RTI_EXCEPTION(InvalidLogicalTime)
        HANDLE_RTI_EXCEPTION(InvalidLookahead)
        HANDLE_RTI_EXCEPTION(TimeRegulationAlreadyEnabled)
        HANDLE_RTI_EXCEPTION(TimeConstrainedAlreadyEnabled)
        HANDLE_RTI_EXCEPTION(RequestForTimeRegulationPending)
        HANDLE_RTI_EXCEPTION(RequestForTimeConstrainedPending)
        HANDLE_RTI_EXCEPTION(InTimeAdvancingState)
        HANDLE_RTI_EXCEPTION(FederateUnableToUseTime)
        HANDLE_RTI_EXCEPTION(SynchronizationPointLabelNotAnnounced)
        HANDLE_RTI_EXCEPTION(AttributeNotOwned)
        HANDLE_RTI_EXCEPTION(AttributeAlreadyBeingAcquired)
        HANDLE_RTI_EXCEPTION(AttributeAlreadyOwned)
        HANDLE_RTI_EXCEPTION(AttributeAcquisitionWasNotRequested)
        HANDLE_RTI_EXCEPTION(AttributeAlreadyBeingDivested)
        HANDLE_RTI_EXCEPTION(AttributeDivestitureWasNotRequested)
        HANDLE_RTI_EXCEPTION(RTIinternalError)
        catch (const std::exception& exc) {
            error("RTIinternalError", widen_ascii(exc.what()));
        }
    }
    return 0;
}
