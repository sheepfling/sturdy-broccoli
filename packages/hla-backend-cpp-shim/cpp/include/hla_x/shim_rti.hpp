#pragma once

namespace hla_x {

class ShimRtiKernel {
public:
  ShimRtiKernel() = default;
  virtual ~ShimRtiKernel() = default;

  const char *name() const noexcept { return "hla_cpp_shim_kernel"; }
};

}  // namespace hla_x
