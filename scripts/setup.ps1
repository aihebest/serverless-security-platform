# scripts/setup.ps1

$ErrorActionPreference = "Stop"

try {
    # Get absolute paths
    $projectRoot = $PWD
    $pythonPath = "C:\Users\admin\AppData\Local\Programs\Python\Python39\python.exe"
    $venvPath = Join-Path $projectRoot ".venv"

    # Remove existing virtual environment
    Write-Host "Removing existing virtual environment..."
    if (Test-Path $venvPath) {
        Remove-Item -Recurse -Force $venvPath -ErrorAction SilentlyContinue
    }

    # Create virtual environment
    Write-Host "Creating virtual environment..."
    & $pythonPath -m venv $venvPath
    if ($LASTEXITCODE -ne 0) { throw "Failed to create virtual environment" }

    # Get virtual environment paths
    $venvPython = Join-Path $venvPath "Scripts\python.exe"

    Write-Host "Installing dependencies..."
    
    # Install core dependencies first
    $corePackages = @(
        "wheel==0.38.4",
        "setuptools==65.5.1",
        "packaging==21.3",
        "pyparsing==3.0.9"
    )

    foreach ($package in $corePackages) {
        Write-Host "Installing $package..."
        & $venvPython -m pip install --no-cache-dir $package
        if ($LASTEXITCODE -ne 0) { throw "Failed to install $package" }
    }

    # Install main requirements
    Write-Host "Installing main requirements..."
    & $venvPython -m pip install --no-cache-dir -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw "Failed to install requirements.txt" }

    # Install dev requirements
    Write-Host "Installing dev requirements..."
    & $venvPython -m pip install --no-cache-dir -r requirements-dev.txt
    if ($LASTEXITCODE -ne 0) { throw "Failed to install requirements-dev.txt" }

    Write-Host "`nSetup completed successfully!" -ForegroundColor Green
    Write-Host "To activate the virtual environment, run: .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow

} catch {
    Write-Error $_.Exception.Message
    exit 1
}