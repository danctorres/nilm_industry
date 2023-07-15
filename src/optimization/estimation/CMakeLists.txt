cmake_minimum_required (VERSION 3.10)

project (estimation)

file(GLOB_RECURSE HEADERS
        "handle_data/*.h"
        "optimization_interface/*.h"
        "pso/*.h"
        "simulated_annealing/*.h"
        "ant_colony/*.h"
        "genetic_algorithm/*.h"
        "gradient_descent/*.h"
        "newton/*.h"
        "problem_formulation/*.h"
)

file(GLOB_RECURSE SOURCES
        # "main_IMDELD.cpp"
        "main_HIPE.cpp"
        "handle_data/*.cpp"
        "optimization_interface/*.cpp"
        "pso/*.cpp"
        "simulated_annealing/*.cpp"
        "ant_colony/*.cpp"
        "genetic_algorithm/*.cpp"
        "gradient_descent/*.cpp"
        "newton/*.cpp"
        "problem_formulation/*.cpp"
)

# Define the executable target
add_executable(estimation ${SOURCES} ${HEADERS})

# Set the Clang++ compiler path
# set(CMAKE_CXX_COMPILER "/usr/bin/clang")

find_package(OpenMP REQUIRED)
#find_package(OpenMP REQUIRED)
#include_directories(${OpenCL_INCLUDE_DIRS})

set_target_properties(estimation PROPERTIES
    CXX_STANDARD 20
    CXX_STANDARD_REQUIRED YES
)

# Include directories for the target
target_include_directories(estimation PUBLIC
        handle_data
        optimization_interface
        pso
        simulated_annealing
        ant_colony
        genetic_algorithm
        gradient_descent
        newton
        problem_formulation
)

#target_link_libraries(estimation ${OpenCL_LIBRARIES})
target_link_libraries(estimation PRIVATE OpenMP::OpenMP_CXX)

