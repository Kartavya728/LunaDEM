cmake_minimum_required(VERSION 3.20)
project(lunadem_native LANGUAGES CXX)

find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(_native lunadem_native.cpp)
target_compile_features(_native PRIVATE cxx_std_17)
install(TARGETS _native LIBRARY DESTINATION lunadem RUNTIME DESTINATION lunadem ARCHIVE DESTINATION lunadem)
