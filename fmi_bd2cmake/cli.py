#!/usr/bin/env python3
"""Command line interface for fmi-bd2cmake."""

import os
import sys
import argparse
from pathlib import Path

from .parser import BuildDescriptionParser
from .generator import CMakeGenerator


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Generate CMakeLists.txt from FMI buildDescription.xml"
    )
    parser.add_argument(
        "--input", "-i",
        default="sources/buildDescription.xml",
        help="Path to buildDescription.xml file (default: sources/buildDescription.xml)"
    )
    parser.add_argument(
        "--output", "-o",
        default="CMakeLists.txt",
        help="Output CMakeLists.txt file path (default: CMakeLists.txt)"
    )

    
    args = parser.parse_args()
    
    # Check if input file exists
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        print(f"Current directory: {os.getcwd()}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Parse the build description
        parser_obj = BuildDescriptionParser()
        build_info = parser_obj.parse(input_path)
        
        # Generate CMakeLists.txt
        generator = CMakeGenerator()
        cmake_content = generator.generate(build_info)
        
        # Write output file
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cmake_content)
        
        print(f"Successfully generated {args.output}")
        print("Suggested workflow: ")
        print(" $ cmake -B build -DFMI_HEADERS_DIR=/path/to/fmi/headers .")
        print(" $ cmake --build build --parallel 8")
        print(" $ cmake --install build")

        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
