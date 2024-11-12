# scripts/setup_dev.ps1
$ErrorActionPreference = "Stop"

# Define Python path
$pythonPath = "C:\Users\admin\AppData\Local\Programs\Python\Python39\python.exe"

Write-Host "Setting up development environment..." -ForegroundColor Green

# Create project structure (keep existing directory creation code)
# ...

# Update setup.py with fixed versions
$setupPyContent = @'
from setuptools import setup, find_packages

setup(
    name="serverless-security-platform",
    version="0.1.0",
    description="A serverless security scanning platform",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "azure-functions==1.12.0",
        "azure-functions-worker==1.1.8",
        "azure-core>=1.32.0",  # Updated to be compatible
        "aiohttp==3.8.1",
        "python-dateutil==2.8.2",
        "packaging>=21.3"  # Updated to be compatible
    ],
    python_requires=">=3.9",
)
'@
Set-Content -Path "setup.py" -Value $setupPyContent

# Create virtual environment
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    & $pythonPath -m venv .venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

# Clean install approach
Write-Host "Installing dependencies in order..." -ForegroundColor Yellow

# 1. Core setup tools
Write-Host "Installing core tools..." -ForegroundColor Yellow
& python -m pip install --upgrade pip setuptools wheel

# 2. Install packaging first
Write-Host "Installing packaging..." -ForegroundColor Yellow
& python -m pip install "packaging>=21.3"

# 3. Install core Azure packages
Write-Host "Installing Azure core packages..." -ForegroundColor Yellow
$corePackages = @(
    "azure-core>=1.32.0",
    "azure-functions==1.12.0",
    "azure-functions-worker==1.1.8",
    "aiohttp==3.8.1",
    "python-dateutil==2.8.2"
)

foreach ($package in $corePackages) {
    Write-Host "Installing $package..." -ForegroundColor Yellow
    & python -m pip install $package --no-deps
}

# 4. Install project in editable mode
Write-Host "Installing project in editable mode..." -ForegroundColor Yellow
& python -m pip install -e . --no-deps

# 5. Install development tools with fixed versions
$devPackages = @(
    "pytest==7.4.3",
    "pytest-asyncio==0.21.1",
    "pytest-cov==4.1.0",
    "pytest-mock==3.12.0",
    "black~=23.10.1",  # Using compatible version
    "flake8==6.1.0",
    "mypy==1.6.1",
    "bandit==1.7.5",
    "safety~=2.3.5",   # Using compatible version
    "azure-storage-blob>=12.17.0",
    "azure-identity>=1.13.0"
)

foreach ($package in $devPackages) {
    Write-Host "Installing $package..." -ForegroundColor Yellow
    & python -m pip install $package
}

# 6. Install remaining dependencies
Write-Host "Resolving remaining dependencies..." -ForegroundColor Yellow
& python -m pip install --no-deps -r requirements.txt
& python -m pip install -r requirements.txt

Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "Python project structure created and dependencies installed." -ForegroundColor Green
Write-Host "`nTo activate the virtual environment in new terminals, run:" -ForegroundColor Cyan
Write-Host "    .\activate.ps1" -ForegroundColor Yellow