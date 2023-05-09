cmake_minimum_required (VERSION 3.10)

project (validation)

file(GLOB_RECURSE HEADERS
        "main.h"
        "error/*.h"
        "estimations/*.h"
        "polynomial_function/*.h"
        "read_data/*.h"
        "../estimation/read_data/*.h"
        )

file(GLOB_RECURSE SOURCES
        "main.cpp"
        "error/*.cpp"
        "estimations/*.cpp"
        "polynomial_function/*.cpp"
        "read_data/*.cpp"
        "../estimation/read_data/*.cpp"
        )

# Define the executable target
add_executable(validation ${SOURCES} ${HEADERS})

# Set the Clang++ compiler path
# set(CMAKE_CXX_COMPILER "/usr/bin/clang")

#find_package(OpenMP REQUIRED)
#include_directories(${OpenCL_INCLUDE_DIRS})

set_target_properties(validation PROPERTIES
        CXX_STANDARD 20
        CXX_STANDARD_REQUIRED YES
        )

# Include directories for the target
target_include_directories(validation PUBLIC
        read_data
        error
        estimations
        polynomial_function
        ../estimation/read_data/
        )

#target_link_libraries(estimation ${OpenCL_LIBRARIES})

