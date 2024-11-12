# Check if Python is accessible
$pythonPath = "C:\Users\admin\AppData\Local\Programs\Python\Python39"
$pythonScripts = "C:\Users\admin\AppData\Local\Programs\Python\Python39\Scripts"

# Add Python to Path if not already there
if ($env:Path -notlike "*$pythonPath*") {
    $env:Path = "$env:Path;$pythonPath;$pythonScripts"
}

# Remove existing venv if it exists
if (Test-Path ".venv") {
    Write-Host "Removing existing virtual environment..."
    Remove-Item -Recurse -Force .venv
}

# Create new virtual environment
Write-Host "Creating new virtual environment..."
& "$pythonPath\python.exe" -m venv .venv

# Activate virtual environment
Write-Host "Activating virtual environment..."
. .\.venv\Scripts\Activate.ps1

# Upgrade pip and install basic tools
Write-Host "Upgrading pip and installing basic tools..."
python -m pip install --upgrade pip setuptools wheel

# Install requirements
Write-Host "Installing base requirements..."
pip install -r requirements/base.txt

Write-Host "Installing development requirements..."
pip install -r requirements/dev.txt

Write-Host "Environment setup complete!"
Write-Host "To activate the virtual environment, use:"
Write-Host "    .venv\Scripts\Activate.ps1"