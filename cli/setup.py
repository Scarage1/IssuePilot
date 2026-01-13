"""
IssuePilot CLI Setup Configuration
"""
from setuptools import setup, find_packages

with open("../README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="issuepilot",
    version="1.0.0",
    author="IssuePilot Team",
    author_email="team@issuepilot.dev",
    description="AI-powered GitHub issue analysis assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Scarage1/IssuePilot",
    project_urls={
        "Bug Tracker": "https://github.com/Scarage1/IssuePilot/issues",
        "Documentation": "https://github.com/Scarage1/IssuePilot/tree/main/docs",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    py_modules=["issuepilot"],
    python_requires=">=3.9",
    install_requires=[
        "httpx>=0.25.0",
    ],
    entry_points={
        "console_scripts": [
            "issuepilot=issuepilot:main",
        ],
    },
    keywords="github, issues, ai, analysis, open-source, maintainer, triage",
)
