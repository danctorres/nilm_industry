cmake_minimum_required (VERSION 3.10)

project (estimation)

file(GLOB_RECURSE HEADERS
        "${CMAKE_SOURCE_DIR}/main.h"
        "${CMAKE_SOURCE_DIR}/read_data/*.h"
        "${CMAKE_SOURCE_DIR}/optimization_interface/*.h"
        "${CMAKE_SOURCE_DIR}/pso/PSO_Particle.h"
)

file(GLOB_RECURSE SOURCES
        "${CMAKE_SOURCE_DIR}/main.cpp"
        "${CMAKE_SOURCE_DIR}/read_data/*.cpp"
        "${CMAKE_SOURCE_DIR}/optimization_interface/*.cpp"
        "${CMAKE_SOURCE_DIR}/pso/PSO_Particle.h"
)

# Define the executable target
add_executable(estimation ${SOURCES} ${HEADERS})

# Set the Clang++ compiler path
# set(CMAKE_CXX_COMPILER "/usr/bin/clang")

set_target_properties(estimation PROPERTIES
    CXX_STANDARD 20
    CXX_STANDARD_REQUIRED YES
)

# Include directories for the target
target_include_directories(estimation PUBLIC
        ${CMAKE_SOURCE_DIR}/read_data
        ${CMAKE_SOURCE_DIR}/optimization_interface
        ${CMAKE_SOURCE_DIR}/pso
)
