cmake_minimum_required(VERSION 3.20)
project(nilm_optimization LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()
if(NOT MSVC)
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(OpenMP)

foreach(exe estimate validate tests)
  add_executable(${exe} ${exe}.cpp)
  if(OpenMP_CXX_FOUND)
    target_link_libraries(${exe} PRIVATE OpenMP::OpenMP_CXX)
  endif()
endforeach()

enable_testing()
add_test(NAME tests COMMAND tests)
