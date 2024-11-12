from setuptools import setup, find_packages
import os

# Simple version management
VERSION = "0.1.0"

# Read requirements files
def read_requirements(filename):
    with open(filename) as f:
        return [line.strip() for line in f 
                if line.strip() and not line.startswith('#')]

setup(
    name='serverless-security-platform',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.9',
    install_requires=read_requirements('requirements.txt'),
    extras_require={
        'dev': read_requirements('test_requirements.txt'),
    },
)