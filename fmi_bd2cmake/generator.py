"""CMakeLists.txt generator for FMI build descriptions."""

from typing import List
from .parser import BuildInfo


class CMakeGenerator:
    """Generates CMakeLists.txt content from FMI build information."""
    
    def generate(self, build_info: BuildInfo) -> str:
        """Generate CMakeLists.txt content from build information."""
        lines = []
        
        # CMake minimum version and project setup
        lines.append("cmake_minimum_required(VERSION 3.5)")
        lines.append("")

        lines.append("""set(CMAKE_SHARED_LIBRARY_PREFIX "")""")
        lines.append("")
        
        # Use the first build configuration
        if not build_info.build_configurations:
            raise ValueError("No build configurations found")
        
        config = build_info.build_configurations[0]
        project_name = config.model_identifier or "fmi_model"
        
        lines.append(f"project({project_name})")
        lines.append("")

        # Architecture detection (after project() call)
        lines.extend(self._generate_architecture_detection())
        lines.append("")
        
        # Set language standards based on source file set languages
        c_standard, cxx_standard = self._get_language_standards(config)
        if c_standard:
            lines.append(f"set(CMAKE_C_STANDARD {c_standard})")
        if cxx_standard:
            lines.append(f"set(CMAKE_CXX_STANDARD {cxx_standard})")
        if c_standard or cxx_standard:
            lines.append("")
        
        # Collect all source files
        source_files = []
        for sfs in config.source_file_sets:
            for sf in sfs.source_files:
                # Prepend sources/ to the file path as per FMI convention
                source_files.append(f"sources/{sf.name}")
        
        if not source_files:
            raise ValueError("No source files found in build configuration")
        
        # Create shared library
        lines.append("# Create shared library")
        lines.append(f"add_library({project_name} SHARED")
        for sf in source_files:
            lines.append(f"    {sf}")
        lines.append(")")
        lines.append("")
        
        # Set target properties
        lines.append("# Set target properties")
        lines.append(f"set_target_properties({project_name} PROPERTIES")
        lines.append(f"    OUTPUT_NAME {project_name}")
        
        # Set the output directory based on platform
        lines.append(f"    LIBRARY_OUTPUT_DIRECTORY binaries/${{FMI_PLATFORM}}")
        lines.append(f"    RUNTIME_OUTPUT_DIRECTORY binaries/${{FMI_PLATFORM}}")
        lines.append(")")
        lines.append("")
        
        # Add include directories
        include_dirs = set()
        include_dirs.add("sources")  # Always include sources directory
        
        # Add global include directories
        for inc_dir in config.include_directories:
            include_dirs.add(inc_dir)
        
        # Add include directories from source file sets
        for sfs in config.source_file_sets:
            for inc_dir in sfs.include_directories:
                include_dirs.add(inc_dir)
        
        # Add FMI headers directory finding logic
        fmi_headers_section = self._generate_fmi_headers_section()
        if fmi_headers_section:
            lines.extend(fmi_headers_section)
            lines.append("")
        
        if include_dirs:
            lines.append("# Include directories")
            lines.append(f"target_include_directories({project_name} PRIVATE")
            # Add FMI headers if found
            lines.append("    $<$<BOOL:${FMI_HEADERS_DIR}>:${FMI_HEADERS_DIR}>")
            for inc_dir in sorted(include_dirs):
                lines.append(f"    {inc_dir}")
            lines.append(")")
            lines.append("")
        
        # Add preprocessor definitions
        definitions = set()
        
        # Add global definitions
        for definition in config.preprocessor_definitions:
            definitions.add(definition)
        
        # Add definitions from source file sets
        for sfs in config.source_file_sets:
            for definition in sfs.preprocessor_definitions:
                definitions.add(definition)
        
        if definitions:
            lines.append("# Preprocessor definitions")
            lines.append(f"target_compile_definitions({project_name} PRIVATE")
            for definition in sorted(definitions):
                lines.append(f"    {definition}")
            lines.append(")")
            lines.append("")
        
        # Add compiler options from source file sets
        compiler_options = set()
        for sfs in config.source_file_sets:
            if sfs.compiler_options:
                # Split compiler options and add them
                options = sfs.compiler_options.split()
                for option in options:
                    compiler_options.add(option)
        
        if compiler_options:
            lines.append("# Compiler options")
            lines.append(f"target_compile_options({project_name} PRIVATE")
            for option in sorted(compiler_options):
                lines.append(f"    {option}")
            lines.append(")")
            lines.append("")
        
        # Link libraries
        if config.libraries:
            lines.append("# Link libraries")
            lines.append(f"target_link_libraries({project_name} PRIVATE")
            for library in config.libraries:
                lines.append(f"    {library}")
            lines.append(")")
            lines.append("")
        
        # Install rules
        lines.append("# Install rules")
        lines.append(f"install(TARGETS {project_name}")
        lines.append(f"    LIBRARY DESTINATION binaries/${{FMI_PLATFORM}}")
        lines.append(f"    RUNTIME DESTINATION binaries/${{FMI_PLATFORM}}")
        lines.append(")")
        
        # Create binaries directory
        lines.append("")
        lines.append("# Create binaries directory")
        lines.append(f"file(MAKE_DIRECTORY ${{CMAKE_BINARY_DIR}}/binaries/${{FMI_PLATFORM}})")
        
        return "\n".join(lines) + "\n"
    
    def _generate_architecture_detection(self) -> List[str]:
        """Generate CMake code for architecture detection (inspired by Reference-FMUs)."""
        lines = []
        
        lines.append("# Architecture detection")
        lines.append("set(FMI_ARCHITECTURE \"\" CACHE STRING \"FMI Architecture\")")
        lines.append("set_property(CACHE FMI_ARCHITECTURE PROPERTY STRINGS \"\" \"aarch64\" \"x86\" \"x86_64\")")
        lines.append("")
        lines.append("if (NOT FMI_ARCHITECTURE)")
        lines.append("  # Try CMAKE_SYSTEM_PROCESSOR first, then CMAKE_HOST_SYSTEM_PROCESSOR as fallback")
        lines.append("  set(PROCESSOR \"${CMAKE_SYSTEM_PROCESSOR}\")")
        lines.append("  if (NOT PROCESSOR)")
        lines.append("    set(PROCESSOR \"${CMAKE_HOST_SYSTEM_PROCESSOR}\")")
        lines.append("  endif()")
        lines.append("  ")
        lines.append("  if (PROCESSOR MATCHES \"AMD64|x86_64\")")
        lines.append("    set(FMI_ARCHITECTURE \"x86_64\")")
        lines.append("  elseif (PROCESSOR MATCHES \"i386|i686|x86\")")
        lines.append("    set(FMI_ARCHITECTURE \"x86\")")
        lines.append("  elseif (PROCESSOR MATCHES \"aarch64|arm64\")")
        lines.append("    set(FMI_ARCHITECTURE \"aarch64\")")
        lines.append("  elseif (PROCESSOR MATCHES \"arm\")")
        lines.append("    set(FMI_ARCHITECTURE \"arm\")")
        lines.append("  else ()")
        lines.append("    # Default to x86_64 if processor is unknown or empty")
        lines.append("    message(STATUS \"Unknown or empty system processor '${PROCESSOR}', defaulting to x86_64\")")
        lines.append("    set(FMI_ARCHITECTURE \"x86_64\")")
        lines.append("  endif ()")
        lines.append("endif ()")
        lines.append("")
        lines.append("# Platform detection")
        lines.append("if (WIN32)")
        lines.append("  set(FMI_PLATFORM \"${FMI_ARCHITECTURE}-windows\")")
        lines.append("elseif (APPLE)")
        lines.append("  set(FMI_PLATFORM \"${FMI_ARCHITECTURE}-darwin\")")
        lines.append("else ()")
        lines.append("  set(FMI_PLATFORM \"${FMI_ARCHITECTURE}-linux\")")
        lines.append("endif ()")
        lines.append("")
        lines.append("message(STATUS \"FMI Platform: ${FMI_PLATFORM}\")")
        
        return lines
    
    def _generate_fmi_headers_section(self) -> List[str]:
        """Generate CMake code to find FMI headers directory."""
        lines = []
        
        lines.append("# Find FMI headers directory")
        lines.append("# Can be set via -DFMI_HEADERS_DIR=/path or FMI_HEADERS_DIR environment variable")
        lines.append("if(NOT FMI_HEADERS_DIR)")
        lines.append("    # Try environment variable first")
        lines.append("    set(FMI_HEADERS_DIR $ENV{FMI_HEADERS_DIR})")
        lines.append("endif()")
        lines.append("")
        lines.append("# Try to find fmi2Functions.h if FMI_HEADERS_DIR is not set")
        lines.append("if(NOT FMI_HEADERS_DIR)")
        lines.append("    find_path(FMI_HEADERS_DIR")
        lines.append("        NAMES fmi2Functions.h")
        lines.append("        PATHS")
        lines.append("            /usr/include/fmi2")
        lines.append("            /usr/local/include/fmi2") 
        lines.append("            /opt/local/include/fmi2")
        lines.append("            ${CMAKE_SOURCE_DIR}/../fmi-headers")
        lines.append("            ${CMAKE_SOURCE_DIR}/fmi-headers")
        lines.append("        DOC \"FMI headers directory containing fmi2Functions.h\"")
        lines.append("    )")
        lines.append("endif()")
        lines.append("")
        lines.append("if(FMI_HEADERS_DIR)")
        lines.append("    message(STATUS \"Using FMI headers from: ${FMI_HEADERS_DIR}\")")
        lines.append("else()")
        lines.append("    message(STATUS \"FMI headers not found - you may need to set FMI_HEADERS_DIR\")")
        lines.append("endif()")
        
        return lines
    
    def _get_language_standards(self, config) -> tuple:
        """Determine C and C++ standards from source file set languages."""
        c_standard = None
        cxx_standard = None
        
        for sfs in config.source_file_sets:
            lang = sfs.language.upper()
            
            # Handle C standards
            if lang in ["C99", "C89", "C90", "C11", "C17"]:
                lang_map = {
                    "C89": "90",
                    "C90": "90", 
                    "C99": "99",
                    "C11": "11",
                    "C17": "17"
                }
                if not c_standard:  # Use first found standard
                    c_standard = lang_map.get(lang, "99")
            
            # Handle C++ standards
            elif lang in ["C++", "CPP", "C++98", "C++03", "C++11", "C++14", "C++17", "C++20"]:
                cxx_map = {
                    "C++": "11",    # Default C++ to C++11
                    "CPP": "11",    # Default CPP to C++11
                    "C++98": "98",
                    "C++03": "03",
                    "C++11": "11",
                    "C++14": "14",
                    "C++17": "17",
                    "C++20": "20"
                }
                if not cxx_standard:  # Use first found standard
                    cxx_standard = cxx_map.get(lang, "11")
        
        # Set defaults if we have source files but no explicit standards
        if not c_standard and not cxx_standard:
            # Check if we have any source files to determine default
            has_c_files = any(sf.name.endswith(('.c', '.h')) for sfs in config.source_file_sets for sf in sfs.source_files)
            has_cpp_files = any(sf.name.endswith(('.cpp', '.cxx', '.cc', '.hpp', '.hxx')) for sfs in config.source_file_sets for sf in sfs.source_files)
            
            if has_cpp_files:
                cxx_standard = "11"  # Default to C++11
            elif has_c_files:
                c_standard = "99"   # Default to C99
        
        return c_standard, cxx_standard
