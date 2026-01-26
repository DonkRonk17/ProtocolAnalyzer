#!/usr/bin/env python3
"""Setup script for ProtocolAnalyzer."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="protocolanalyzer",
    version="1.0.0",
    author="ATLAS (Team Brain)",
    author_email="metaphyllc@example.com",
    description="Compare protocol options and recommend simplest solution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DonkRonk17/ProtocolAnalyzer",
    py_modules=["protocolanalyzer"],
    python_requires=">=3.7",
    install_requires=[],  # Zero dependencies!
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "mypy>=0.990",
        ],
    },
    entry_points={
        "console_scripts": [
            "protocolanalyzer=protocolanalyzer:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: System :: Networking",
    ],
    keywords="protocol analysis websocket socket.io http grpc graphql architecture",
    project_urls={
        "Bug Reports": "https://github.com/DonkRonk17/ProtocolAnalyzer/issues",
        "Source": "https://github.com/DonkRonk17/ProtocolAnalyzer",
        "Documentation": "https://github.com/DonkRonk17/ProtocolAnalyzer#readme",
    },
)
