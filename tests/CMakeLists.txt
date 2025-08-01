cmake_minimum_required(VERSION 3.20)
set(CMAKE_OSX_DEPLOYMENT_TARGET "10.15" CACHE STRING "Minimum OS X deployment version")

project(CASMcode_composition_tests VERSION 2.2.0 LANGUAGES CXX)


# set CMAKE_INSTALL_X variables
include(GNUInstallDirs)

# specify the C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# try to use ccache
find_program(CCACHE_PROGRAM ccache)
if(CCACHE_PROGRAM)
    set(CMAKE_CXX_COMPILER_LAUNCHER "${CCACHE_PROGRAM}")
endif()

### googletest ###
include(FetchContent)

FetchContent_Declare(
  googletest
  GIT_REPOSITORY https://github.com/google/googletest.git
  GIT_TAG        v1.13.0
)
FetchContent_MakeAvailable(googletest)
message(STATUS "googletest_SOURCE_DIR: ${googletest_SOURCE_DIR}")

# compile Google Test as an object library
add_library(gtest_all OBJECT "${googletest_SOURCE_DIR}/googletest/src/gtest-all.cc")
set_property(TARGET gtest_all PROPERTY INCLUDE_DIRECTORIES
  "${googletest_SOURCE_DIR}/googletest/include"
  "${googletest_SOURCE_DIR}/googletest")
set_property(TARGET gtest_all PROPERTY POSITION_INDEPENDENT_CODE ON)
target_compile_options(gtest_all
  PUBLIC
    "-DGTEST_HAS_PTHREAD=0"
    "-DGTEST_LINKED_AS_SHARED_LIBRARY=1"
)

### ZLIB ###
# Should find ZLIB::ZLIB
find_package(ZLIB)


### CASM ###

# Find CASM
if(NOT DEFINED CASM_PREFIX)
  message(STATUS "CASM_PREFIX not defined")
  # try to find Python
  find_package (Python COMPONENTS Interpreter Development)
  if(DEFINED Python_EXECUTABLE)
    # if Python found, obtain CASM_PREFIX from the libcasm.casmglobal
    message(STATUS "found Python_EXECUTABLE: ${Python_EXECUTABLE}")
    message(STATUS "checking for libcasm-global")
    execute_process(
      COMMAND pip show libcasm-global
      RESULT_VARIABLE EXIT_CODE
      OUTPUT_QUIET
    )
    if (${EXIT_CODE} EQUAL 0)
      message(STATUS "found libcasm-global")
      execute_process(COMMAND ${Python_EXECUTABLE} -m libcasm.casmglobal --prefix
                      OUTPUT_VARIABLE CASM_PREFIX_RAW)
      string(STRIP ${CASM_PREFIX_RAW} CASM_PREFIX)
      message(STATUS "CASM_PREFIX: ${CASM_PREFIX}")
    else()
      message(STATUS "did not find libcasm-global")
    endif()
  endif()
endif()
if(DEFINED CASM_PREFIX)
  set(CASMcode_global_ROOT ${CASM_PREFIX}/share/CASMcode_global/cmake)
  set(CASMcode_composition_ROOT ${CASM_PREFIX}/share/CASMcode_composition/cmake)
endif()

find_package(CASMcode_global)
if(NOT CASMcode_global_FOUND)
  message(FATAL_ERROR "CMake failed to find CASMcode_global")
endif()
# if successful, we have CASM::casm_global

find_package(CASMcode_composition)
if(NOT CASMcode_composition_FOUND)
  message(FATAL_ERROR "CMake failed to find CASMcode_composition")
endif()
# if successful, we have CASM::casm_composition


### libcasm_testing ###
set(
  libcasm_testing_SOURCES
  ${PROJECT_SOURCE_DIR}/unit/autotools.cc
)
add_library(casm_testing SHARED ${libcasm_testing_SOURCES})
target_include_directories(casm_testing
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/unit>
    $<BUILD_INTERFACE:${googletest_SOURCE_DIR}/googletest/include>
)
target_link_libraries(casm_testing
  gtest_all
  CASM::casm_global
  CASM::casm_composition
)
target_compile_options(casm_testing
  PUBLIC
    "-DABS_SRCDIR=\"${CMAKE_SOURCE_DIR}\""
    "-DABS_TOP_BUILDDIR=\"${CMAKE_BINARY_DIR}\""
)

enable_testing()

################################################################
# casm_unit_composition
add_executable(casm_unit_composition
  ${PROJECT_SOURCE_DIR}/unit/gtest_main_run_all.cpp
  ${PROJECT_SOURCE_DIR}/unit/composition/make_subsystem_end_members_test.cpp
  ${PROJECT_SOURCE_DIR}/unit/composition/make_chemical_subsystem_test.cpp
  ${PROJECT_SOURCE_DIR}/unit/composition/CompositionConverter_test.cpp
  ${PROJECT_SOURCE_DIR}/unit/composition/CompositionCalculator_test.cpp
  ${PROJECT_SOURCE_DIR}/unit/composition/make_end_members_test.cpp
  ${PROJECT_SOURCE_DIR}/unit/composition/make_standard_origin_and_end_members_test.cpp
)
target_link_libraries(casm_unit_composition
  gtest_all
  CASM::casm_global
  CASM::casm_composition
  casm_testing
  ZLIB::ZLIB
)
target_include_directories(casm_unit_composition
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/unit>
)

add_test(NAME casm_unit_composition COMMAND casm_unit_composition)
