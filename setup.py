from setuptools import setup, find_packages

setup(
    name="serverless-security-platform",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "azure-functions",
        "azure-storage-blob",
        "azure-keyvault-secrets",
        "azure-identity",
        "aiohttp",
        "fastapi",
        "pydantic",
        "python-jose[cryptography]",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
            "pytest-cov",
            "pytest-mock",
            "bandit",
            "safety",
        ]
    }
)