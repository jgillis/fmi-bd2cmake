cmake_minimum_required(VERSION 3.5)

project(advanced_model)

set(CMAKE_C_STANDARD 99)

# Create shared library
add_library(advanced_model SHARED
    sources/main.c
    sources/utils.c
)

# Set target properties
set_target_properties(advanced_model PROPERTIES
    OUTPUT_NAME advanced_model
    LIBRARY_OUTPUT_DIRECTORY binaries/x86_64-linux
    RUNTIME_OUTPUT_DIRECTORY binaries/x86_64-linux
)

# Include directories
target_include_directories(advanced_model PRIVATE
    ../../common/include
    ../include
    sources
)

# Preprocessor definitions
target_compile_definitions(advanced_model PRIVATE
    DEBUG
    FMI_VERSION=2
    PLATFORM_LINUX
)

# Link libraries
target_link_libraries(advanced_model PRIVATE
    m
)

# Install rules
install(TARGETS advanced_model
    LIBRARY DESTINATION binaries/x86_64-linux
    RUNTIME DESTINATION binaries/x86_64-linux
)

# Create binaries directory
file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/binaries/x86_64-linux)
