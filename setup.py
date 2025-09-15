#!/usr/bin/env python3
"""Setup script for fmi-bd2cmake package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fmi-bd2cmake",
    version="0.1.0",
    author="FMI Build Tools",
    description="CMakeLists.txt generator that reads buildDescription.xml in FMI source",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "fmi-bd2cmake=fmi_bd2cmake.cli:main",
        ],
    },
    install_requires=[
        # Only standard library dependencies as requested
    ],
)