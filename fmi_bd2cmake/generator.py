"""CMakeLists.txt generator for FMI build descriptions."""

import platform
from typing import List
from .parser import BuildInfo


class CMakeGenerator:
    """Generates CMakeLists.txt content from FMI build information."""
    
    def generate(self, build_info: BuildInfo, fmi_headers_dir: str = None) -> str:
        """Generate CMakeLists.txt content from build information."""
        lines = []
        
        # CMake minimum version and project setup
        lines.append("cmake_minimum_required(VERSION 3.5)")
        lines.append("")
        
        # Use the first build configuration
        if not build_info.build_configurations:
            raise ValueError("No build configurations found")
        
        config = build_info.build_configurations[0]
        project_name = config.model_identifier or "fmi_model"
        
        lines.append(f"project({project_name})")
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
        arch = self._get_architecture()
        lines.append(f"    LIBRARY_OUTPUT_DIRECTORY binaries/{arch}")
        lines.append(f"    RUNTIME_OUTPUT_DIRECTORY binaries/{arch}")
        lines.append(")")
        lines.append("")
        
        # Add include directories
        include_dirs = set()
        include_dirs.add("sources")  # Always include sources directory
        
        # Add FMI headers directory if specified
        if fmi_headers_dir:
            include_dirs.add(fmi_headers_dir)
        
        # Add global include directories
        for inc_dir in config.include_directories:
            include_dirs.add(inc_dir)
        
        # Add include directories from source file sets
        for sfs in config.source_file_sets:
            for inc_dir in sfs.include_directories:
                include_dirs.add(inc_dir)
        
        if include_dirs:
            lines.append("# Include directories")
            lines.append(f"target_include_directories({project_name} PRIVATE")
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
        lines.append(f"    LIBRARY DESTINATION binaries/{arch}")
        lines.append(f"    RUNTIME DESTINATION binaries/{arch}")
        lines.append(")")
        
        # Create binaries directory
        lines.append("")
        lines.append("# Create binaries directory")
        lines.append(f"file(MAKE_DIRECTORY ${{CMAKE_BINARY_DIR}}/binaries/{arch})")
        
        return "\n".join(lines) + "\n"
    
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
    
    def _get_architecture(self) -> str:
        """Get the target architecture string for FMI."""
        machine = platform.machine().lower()
        system = platform.system().lower()
        
        # Map common architecture names to FMI conventions
        if machine in ["x86_64", "amd64"]:
            arch = "x86_64"
        elif machine in ["i386", "i686", "x86"]:
            arch = "x86"
        elif machine.startswith("arm"):
            arch = "arm"
        elif machine.startswith("aarch64"):
            arch = "aarch64"
        else:
            arch = machine
        
        # Add OS suffix
        if system == "windows":
            return f"{arch}-windows"
        elif system == "darwin":
            return f"{arch}-darwin"
        elif system == "linux":
            return f"{arch}-linux"
        else:
            return f"{arch}-{system}"