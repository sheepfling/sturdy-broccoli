#include "hla_x/shim_rti.hpp"

namespace hla_x {
namespace {
static_assert(sizeof(ShimRtiKernel) >= 1, "Shim kernel must be a real type");
}  // namespace
}  // namespace hla_x
