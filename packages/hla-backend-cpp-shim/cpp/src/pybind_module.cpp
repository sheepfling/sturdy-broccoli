#include <pybind11/pybind11.h>

#include "hla_x/shim_rti.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_hla_cpp_shim, m) {
  m.doc() = "HLA C++ shim pybind module";

  py::class_<hla_x::ShimRtiKernel>(m, "ShimRtiKernel")
      .def(py::init<>())
      .def("name", &hla_x::ShimRtiKernel::name);

  m.def("create_kernel", []() { return hla_x::ShimRtiKernel{}; });
}
