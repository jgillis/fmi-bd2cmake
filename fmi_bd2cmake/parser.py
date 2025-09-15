"""Parser for FMI buildDescription.xml files."""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from pathlib import Path


class BuildConfiguration:
    """Represents a single build configuration."""
    
    def __init__(self):
        self.description = ""
        self.model_identifier = ""
        self.source_file_sets = []
        self.libraries = []
        self.include_directories = []
        self.preprocessor_definitions = []


class SourceFileSet:
    """Represents a set of source files with the same language/compiler settings."""
    
    def __init__(self):
        self.language = ""
        self.compiler = ""
        self.compiler_options = ""
        self.source_files = []
        self.include_directories = []
        self.preprocessor_definitions = []


class SourceFile:
    """Represents a single source file."""
    
    def __init__(self, name: str):
        self.name = name


class BuildInfo:
    """Container for all build information parsed from buildDescription.xml."""
    
    def __init__(self):
        self.fmi_version = ""
        self.build_configurations = []


class BuildDescriptionParser:
    """Parser for FMI buildDescription.xml files."""
    
    def parse(self, xml_path: Path) -> BuildInfo:
        """Parse a buildDescription.xml file and return build information."""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML in {xml_path}: {e}")
        except Exception as e:
            raise ValueError(f"Error reading {xml_path}: {e}")
        
        build_info = BuildInfo()
        
        # Parse FMI version
        build_info.fmi_version = root.get("fmiVersion", "")
        
        # Parse build configurations
        for config_elem in root.findall("BuildConfiguration"):
            config = self._parse_build_configuration(config_elem)
            build_info.build_configurations.append(config)
        
        if not build_info.build_configurations:
            raise ValueError("No BuildConfiguration found in buildDescription.xml")
        
        return build_info
    
    def _parse_build_configuration(self, config_elem) -> BuildConfiguration:
        """Parse a BuildConfiguration element."""
        config = BuildConfiguration()
        config.description = config_elem.get("description", "")
        config.model_identifier = config_elem.get("modelIdentifier", "")
        
        # Parse source file sets
        for sfs_elem in config_elem.findall("SourceFileSet"):
            source_file_set = self._parse_source_file_set(sfs_elem)
            config.source_file_sets.append(source_file_set)
        
        # Parse libraries
        for lib_elem in config_elem.findall("Library"):
            library_name = lib_elem.get("name", "")
            if library_name:
                config.libraries.append(library_name)
        
        # Parse include directories
        for inc_elem in config_elem.findall("IncludeDirectory"):
            inc_dir = inc_elem.get("name", "")
            if inc_dir:
                config.include_directories.append(inc_dir)
        
        # Parse preprocessor definitions
        for def_elem in config_elem.findall("PreprocessorDefinition"):
            definition = def_elem.get("name", "")
            value = def_elem.get("value", "")
            if definition:
                if value:
                    config.preprocessor_definitions.append(f"{definition}={value}")
                else:
                    config.preprocessor_definitions.append(definition)
        
        return config
    
    def _parse_source_file_set(self, sfs_elem) -> SourceFileSet:
        """Parse a SourceFileSet element."""
        sfs = SourceFileSet()
        sfs.language = sfs_elem.get("language", "")
        sfs.compiler = sfs_elem.get("compiler", "")
        sfs.compiler_options = sfs_elem.get("compilerOptions", "")
        
        # Parse source files
        for sf_elem in sfs_elem.findall("SourceFile"):
            file_name = sf_elem.get("name", "")
            if file_name:
                source_file = SourceFile(file_name)
                sfs.source_files.append(source_file)
        
        # Parse include directories for this source file set
        for inc_elem in sfs_elem.findall("IncludeDirectory"):
            inc_dir = inc_elem.get("name", "")
            if inc_dir:
                sfs.include_directories.append(inc_dir)
        
        # Parse preprocessor definitions for this source file set
        for def_elem in sfs_elem.findall("PreprocessorDefinition"):
            definition = def_elem.get("name", "")
            value = def_elem.get("value", "")
            if definition:
                if value:
                    sfs.preprocessor_definitions.append(f"{definition}={value}")
                else:
                    sfs.preprocessor_definitions.append(definition)
        
        return sfs