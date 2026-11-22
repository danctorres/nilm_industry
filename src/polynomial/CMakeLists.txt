cmake_minimum_required(VERSION 3.20...3.31)
project(nilm_polynomial LANGUAGES CXX)

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

include(FetchContent)
FetchContent_Declare(doctest
  URL https://github.com/doctest/doctest/archive/refs/tags/v2.5.3.tar.gz
  URL_HASH SHA256=174ebc4e769928959614789c5b4e9c3d0a0f81a62bb608756b127bfebfb21331)
FetchContent_MakeAvailable(doctest)
include(${DOCTEST_CMAKE_HELPER})

foreach(exe estimate validate tests)
  add_executable(${exe} ${exe}.cpp)
endforeach()

if(OpenMP_CXX_FOUND)
  target_link_libraries(estimate PRIVATE OpenMP::OpenMP_CXX)
endif()

target_link_libraries(tests PRIVATE doctest::doctest_with_main)

enable_testing()
doctest_discover_tests(tests)

# estimate, then validate on its coefficients, on a tiny set: both must exit 0
set(td ${CMAKE_CURRENT_SOURCE_DIR}/testdata)
add_test(NAME end_to_end_estimate
         COMMAND estimate ${td}/aggregate.csv ${td}/states.csv coef.csv --cycles 1 --iters 20 --seed 1)
add_test(NAME end_to_end_validate COMMAND validate ${td}/aggregate.csv ${td}/states.csv coef.csv estimates.csv)
set_tests_properties(end_to_end_estimate PROPERTIES FIXTURES_SETUP coef)
set_tests_properties(end_to_end_validate PROPERTIES FIXTURES_REQUIRED coef)
