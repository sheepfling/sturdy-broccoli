#include <pybind11/pybind11.h>

#include "shim_routes/shim_rti.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_hla_cpp_shim, m) {
  m.doc() = "HLA C++ shim pybind module";

  py::class_<shim_routes::ShimRtiKernel>(m, "ShimRtiKernel")
      .def(py::init<>())
      .def("name", &shim_routes::ShimRtiKernel::name);

  m.def("create_kernel", []() { return shim_routes::ShimRtiKernel{}; });
}
