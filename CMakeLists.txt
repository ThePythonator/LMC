# Basic parameters; check that these match your project / environment
cmake_minimum_required(VERSION 3.9)

set(PROJECT_DISTRIBS LICENSE README.md)

project(LMC++)
add_executable(LMC++ LMC++.cpp)

install(FILES ${PROJECT_DISTRIBS} DESTINATION .)
install(TARGETS LMC++ DESTINATION bin)

# Setup release packages
set(CPACK_INCLUDE_TOPLEVEL_DIRECTORY OFF)
set(CPACK_GENERATOR "ZIP" "TGZ")
include(CPack)