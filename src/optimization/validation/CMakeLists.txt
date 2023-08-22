cmake_minimum_required (VERSION 3.10)

project (validation)

file(GLOB_RECURSE HEADERS
        "estimations/*.h"
        "../estimation/polynomial_function/*.h"
        "handle_data/*.h"
        "../estimation/handle_data/*.h"
        "../estimation/error/*.h"
        )

file(GLOB_RECURSE SOURCES
        "main_IMDELD.cpp"
        #"main_HIPE.cpp"
        "estimations/*.cpp"
        "../estimation/polynomial_function/*.cpp"
        "handle_data/*.cpp"
        "../estimation/handle_data/*.cpp"
        "../estimation/error/*.cpp"
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
        handle_data
        estimations
        ../estimation/polynomial_function
        ../estimation/handle_data/
        )

#target_link_libraries(estimation ${OpenCL_LIBRARIES})

