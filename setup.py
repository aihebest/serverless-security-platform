# setup.py

from setuptools import setup, find_packages
import os

def read_requirements(filename):
    with open(filename) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='serverless-security-platform',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements('requirements.txt'),
    extras_require={
        'dev': read_requirements('test_requirements.txt'),
    },
    entry_points={
        'console_scripts': [
            'security-platform=src.cli:main',
        ],
    },
    python_requires='>=3.9',
    author='Your Name',
    author_email='your.email@example.com',
    description='Serverless Security Platform',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
    ],
)