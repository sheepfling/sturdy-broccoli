cmake_minimum_required(VERSION 3.16)
project(hla_cpp_shim LANGUAGES CXX)

add_library(hla_cpp_shim_kernel STATIC
  src/shim_rti.cpp
)

target_include_directories(hla_cpp_shim_kernel PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_compile_features(hla_cpp_shim_kernel PUBLIC cxx_std_14)

find_package(pybind11 CONFIG QUIET)
if(pybind11_FOUND)
  pybind11_add_module(_hla_cpp_shim MODULE
    src/pybind_module.cpp
  )
  target_include_directories(_hla_cpp_shim PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
  )
  target_link_libraries(_hla_cpp_shim PRIVATE hla_cpp_shim_kernel)
  target_compile_features(_hla_cpp_shim PRIVATE cxx_std_14)
else()
  message(STATUS "pybind11 not found; building only the native shim kernel")
endif()
