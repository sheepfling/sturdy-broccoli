#include "shim_routes/shim_rti.hpp"

namespace shim_routes {
namespace {
static_assert(sizeof(ShimRtiKernel) >= 1, "Shim kernel must be a real type");
}  // namespace
}  // namespace shim_routes
