#pragma once

namespace shim_routes {

class ShimRtiKernel {
public:
  ShimRtiKernel() = default;
  virtual ~ShimRtiKernel() = default;

  const char *name() const noexcept { return "hla_cpp_shim_kernel"; }
};

}  // namespace shim_routes
