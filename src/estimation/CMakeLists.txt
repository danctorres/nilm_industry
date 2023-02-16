# CMakeLists files in this project can
# refer to the root source directory of the project as ${HELLO_SOURCE_DIR} and
# to the root binary directory of the project as ${HELLO_BINARY_DIR}.
cmake_minimum_required (VERSION 3.10)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

project (estimation)
add_executable(estimation main.cpp)
target_include_directories(estimation PUBLIC $(CMAKE_CURRENT_SOURCE_DIR)/include )