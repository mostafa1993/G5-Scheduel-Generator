"""
Setup script for the G5 Spaced Repetition Schedule Generator.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="g5",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python tool for generating spaced repetition learning schedules using the G5 method",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/g5",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "g5=g5.cli:main",
        ],
    },
)
