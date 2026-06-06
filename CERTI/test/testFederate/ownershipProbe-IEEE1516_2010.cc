#include <RTI/Enums.h>
#include <RTI/NullFederateAmbassador.h>
#include <RTI/RTI1516.h>

#include <chrono>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <memory>
#include <string>
#include <thread>
#include <unistd.h>

namespace {

std::string narrow(const std::wstring& value)
{
    return std::string(value.begin(), value.end());
}

std::wstring widen(const std::string& value)
{
    return std::wstring(value.begin(), value.end());
}

class OwnershipProbeAmbassador : public rti1516e::NullFederateAmbassador {
public:
    bool discovered_object_valid = false;
    rti1516e::ObjectInstanceHandle discovered_object;
    bool assumption_received = false;
    bool release_requested = false;
    bool unavailable_received = false;
    bool acquisition_confirmed = false;
    bool cancellation_confirmed = false;

    void discoverObjectInstance(rti1516e::ObjectInstanceHandle theObject,
                                rti1516e::ObjectClassHandle,
                                std::wstring const& theObjectInstanceName) throw(rti1516e::FederateInternalError) override
    {
        discovered_object = theObject;
        discovered_object_valid = true;
        std::cout << "[callback] discoverObjectInstance name=" << narrow(theObjectInstanceName) << std::endl;
    }

    void requestAttributeOwnershipAssumption(rti1516e::ObjectInstanceHandle,
                                             rti1516e::AttributeHandleSet const& offeredAttributes,
                                             rti1516e::VariableLengthData const&) throw(rti1516e::FederateInternalError) override
    {
        assumption_received = true;
        std::cout << "[callback] requestAttributeOwnershipAssumption attrs=" << offeredAttributes.size() << std::endl;
    }

    void requestAttributeOwnershipRelease(rti1516e::ObjectInstanceHandle,
                                          rti1516e::AttributeHandleSet const& candidateAttributes,
                                          rti1516e::VariableLengthData const&) throw(rti1516e::FederateInternalError) override
    {
        release_requested = true;
        std::cout << "[callback] requestAttributeOwnershipRelease attrs=" << candidateAttributes.size() << std::endl;
    }

    void attributeOwnershipUnavailable(rti1516e::ObjectInstanceHandle,
                                       rti1516e::AttributeHandleSet const& theAttributes) throw(rti1516e::FederateInternalError) override
    {
        unavailable_received = true;
        std::cout << "[callback] attributeOwnershipUnavailable attrs=" << theAttributes.size() << std::endl;
    }

    void attributeOwnershipAcquisitionNotification(rti1516e::ObjectInstanceHandle,
                                                   rti1516e::AttributeHandleSet const& securedAttributes,
                                                   rti1516e::VariableLengthData const&) throw(rti1516e::FederateInternalError) override
    {
        acquisition_confirmed = true;
        std::cout << "[callback] attributeOwnershipAcquisitionNotification attrs=" << securedAttributes.size() << std::endl;
    }

    void confirmAttributeOwnershipAcquisitionCancellation(rti1516e::ObjectInstanceHandle,
                                                          rti1516e::AttributeHandleSet const& theAttributes) throw(rti1516e::FederateInternalError) override
    {
        cancellation_confirmed = true;
        std::cout << "[callback] confirmAttributeOwnershipAcquisitionCancellation attrs=" << theAttributes.size()
                  << std::endl;
    }
};

void pump_callbacks(rti1516e::RTIambassador& ambassador, int loops = 25, double min_seconds = 0.01, double max_seconds = 0.05)
{
    for (int i = 0; i < loops; ++i) {
        ambassador.evokeMultipleCallbacks(min_seconds, max_seconds);
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
}

template <typename Predicate>
bool pump_until(rti1516e::RTIambassador& ambassador, Predicate&& predicate, int loops = 120, double min_seconds = 0.01,
                double max_seconds = 0.05)
{
    for (int i = 0; i < loops; ++i) {
        if (predicate()) {
            return true;
        }
        ambassador.evokeMultipleCallbacks(min_seconds, max_seconds);
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
    return predicate();
}

std::string getenv_or_empty(const char* name)
{
    const char* value = std::getenv(name);
    return value ? std::string(value) : std::string();
}

void write_marker(const std::string& path, const std::string& value)
{
    if (path.empty()) {
        return;
    }
    std::ofstream out(path);
    out << value << std::endl;
}

bool wait_for_marker(const std::string& path, int loops = 200)
{
    if (path.empty()) {
        return true;
    }
    for (int i = 0; i < loops; ++i) {
        if (access(path.c_str(), F_OK) == 0) {
            return true;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
    return false;
}

int usage(const char* program)
{
    std::cerr << "usage: " << program
              << " <owner|acquirer> <federation-name> <fom-path> <object-name> [deny|confirm|ifwanted]" << std::endl;
    return 2;
}

} // namespace

int main(int argc, char** argv)
{
    if (argc < 5) {
        return usage(argv[0]);
    }

    const std::string role = argv[1];
    const std::wstring federation_name = widen(argv[2]);
    const std::wstring fom_path = widen(argv[3]);
    const std::wstring object_name = widen(argv[4]);
    const std::string owner_action = argc >= 6 ? argv[5] : "deny";
    const std::string owner_registered_marker = getenv_or_empty("CERTI_PROBE_OWNER_REGISTERED_MARKER");
    const std::string owner_divesting_marker = getenv_or_empty("CERTI_PROBE_OWNER_DIVESTING_MARKER");
    const std::string acquirer_discovered_marker = getenv_or_empty("CERTI_PROBE_ACQUIRER_DISCOVERED_MARKER");
    const std::string acquirer_requested_marker = getenv_or_empty("CERTI_PROBE_ACQUIRER_REQUESTED_MARKER");

    OwnershipProbeAmbassador fed_amb;
    std::unique_ptr<rti1516e::RTIambassadorFactory> factory(new rti1516e::RTIambassadorFactory());
    std::unique_ptr<rti1516e::RTIambassador> ambassador = factory->createRTIambassador();

    try {
        ambassador->connect(fed_amb, rti1516e::HLA_EVOKED);
        std::cout << "[step] connect" << std::endl;

        if (role == "owner") {
            try {
                std::cout << "[step] createFederationExecution begin" << std::endl;
                ambassador->createFederationExecution(federation_name, fom_path);
                std::cout << "[step] createFederationExecution ok" << std::endl;
            } catch (rti1516e::FederationExecutionAlreadyExists&) {
                std::cout << "[step] createFederationExecution already exists" << std::endl;
            }
        }

        std::cout << "[step] joinFederationExecution begin role=" << role << std::endl;
        ambassador->joinFederationExecution(widen(role), widen(role), federation_name, std::vector<std::wstring>{});
        std::cout << "[step] joinFederationExecution role=" << role << std::endl;

        const auto object_class = ambassador->getObjectClassHandle(L"Employee");
        const auto attribute = ambassador->getAttributeHandle(object_class, L"PayRate");
        rti1516e::AttributeHandleSet attributes;
        attributes.insert(attribute);

        ambassador->publishObjectClassAttributes(object_class, attributes);
        std::cout << "[step] publishObjectClassAttributes" << std::endl;

        if (role == "owner") {
            const auto object = ambassador->registerObjectInstance(object_class, object_name);
            std::cout << "[step] registerObjectInstance name=" << narrow(object_name) << std::endl;
            write_marker(owner_registered_marker, "registered");
            if (!wait_for_marker(acquirer_discovered_marker)) {
                std::cerr << "[error] acquirer did not discover object before release-request setup" << std::endl;
                return 4;
            }

            std::cout << "[step] owner ready for release-request acquisition path" << std::endl;
            write_marker(owner_divesting_marker, "ready");
            if (!wait_for_marker(acquirer_requested_marker)) {
                std::cerr << "[error] acquirer did not request ownership before owner action" << std::endl;
                return 5;
            }
            if (!pump_until(*ambassador, [&fed_amb]() { return fed_amb.release_requested || fed_amb.assumption_received; }, 160)) {
                std::cout << "[warn] owner saw no ownership callback before timeout" << std::endl;
            }
            if (fed_amb.assumption_received && !fed_amb.release_requested) {
                std::cerr << "[error] owner received requestAttributeOwnershipAssumption instead of release request"
                          << std::endl;
                return 8;
            }

            if (fed_amb.release_requested) {
                std::cout << "[step] owner observed release request; action=" << owner_action << std::endl;
                rti1516e::VariableLengthData tag("probe-release", 13);
                if (owner_action == "confirm") {
                    ambassador->confirmDivestiture(object, attributes, tag);
                    std::cout << "[step] confirmDivestiture returned" << std::endl;
                } else if (owner_action == "ifwanted") {
                    rti1516e::AttributeHandleSet divested;
                    ambassador->attributeOwnershipDivestitureIfWanted(object, attributes, divested);
                    std::cout << "[step] attributeOwnershipDivestitureIfWanted returned attrs=" << divested.size()
                              << std::endl;
                } else {
                    ambassador->attributeOwnershipReleaseDenied(object, attributes);
                    std::cout << "[step] attributeOwnershipReleaseDenied returned" << std::endl;
                }
            }
        } else if (role == "acquirer") {
            if (!wait_for_marker(owner_registered_marker)) {
                std::cerr << "[error] owner did not register object before acquisition flow" << std::endl;
                return 6;
            }
            ambassador->subscribeObjectClassAttributes(object_class, attributes);
            std::cout << "[step] subscribeObjectClassAttributes" << std::endl;
            if (!pump_until(*ambassador, [&fed_amb]() { return fed_amb.discovered_object_valid; }, 160)) {
                std::cerr << "[error] no object discovery before acquisition attempt" << std::endl;
                return 3;
            }
            write_marker(acquirer_discovered_marker, "discovered");
            if (!wait_for_marker(owner_divesting_marker)) {
                std::cerr << "[error] owner did not enter ready state before acquisition" << std::endl;
                return 7;
            }

            rti1516e::VariableLengthData tag("probe-acquire", 13);
            ambassador->attributeOwnershipAcquisition(fed_amb.discovered_object, attributes, tag);
            std::cout << "[step] attributeOwnershipAcquisition returned" << std::endl;
            write_marker(acquirer_requested_marker, "requested");
            if (!pump_until(*ambassador,
                            [&fed_amb]() {
                                return fed_amb.acquisition_confirmed || fed_amb.unavailable_received
                                       || fed_amb.cancellation_confirmed;
                            },
                            160)) {
                std::cout << "[warn] acquirer saw no terminal ownership callback before timeout" << std::endl;
            }
        } else {
            return usage(argv[0]);
        }

        pump_callbacks(*ambassador, 20);
        ambassador->resignFederationExecution(rti1516e::NO_ACTION);
        std::cout << "[step] resignFederationExecution" << std::endl;

        if (role == "owner") {
            try {
                ambassador->destroyFederationExecution(federation_name);
                std::cout << "[step] destroyFederationExecution" << std::endl;
            } catch (rti1516e::Exception& exc) {
                std::cout << "[warn] destroyFederationExecution: " << narrow(exc.what()) << std::endl;
            }
        }

        ambassador->disconnect();
        std::cout << "[step] disconnect" << std::endl;
        return 0;
    } catch (rti1516e::Exception& exc) {
        std::cerr << "[exception] " << narrow(exc.what()) << std::endl;
        return 1;
    }
}
