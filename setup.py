import sys
from setuptools import find_packages, setup

setup(
    name="slurmpy",
    version="0.1.0",
    author="Sterling Baldwin",
    author_email="baldwin32@llnl.gov",
    description="Python wrapper around slurm console command",
    packages=find_packages(exclude=["*.test", "*.test.*", "test.*", "test", "*_template.py"]))
