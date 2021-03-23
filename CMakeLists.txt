# Basic parameters; check that these match your project / environment
cmake_minimum_required(VERSION 3.9)

project(LMC++)
add_executable(LMC++ LMC++.cpp)

# Setup release packages
set(CPACK_GENERATOR "ZIP" "TGZ")
include(CPack)
