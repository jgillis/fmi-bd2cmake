cmake_minimum_required(VERSION 3.5)

project(model_DANA_modified_extraction_76122067_49_ds)

set(CMAKE_C_STANDARD 99)

# Create shared library
add_library(model_DANA_modified_extraction_76122067_49_ds SHARED
    sources/model_DANA_modified_extraction_76122067_49_ds.c
)

# Set target properties
set_target_properties(model_DANA_modified_extraction_76122067_49_ds PROPERTIES
    OUTPUT_NAME model_DANA_modified_extraction_76122067_49_ds
    LIBRARY_OUTPUT_DIRECTORY binaries/x86_64-linux
    RUNTIME_OUTPUT_DIRECTORY binaries/x86_64-linux
)

# Include directories
target_include_directories(model_DANA_modified_extraction_76122067_49_ds PRIVATE
    sources
)

# Install rules
install(TARGETS model_DANA_modified_extraction_76122067_49_ds
    LIBRARY DESTINATION binaries/x86_64-linux
    RUNTIME DESTINATION binaries/x86_64-linux
)

# Create binaries directory
file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/binaries/x86_64-linux)
