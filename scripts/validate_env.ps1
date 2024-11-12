# scripts/validate_env.ps1

$ErrorActionPreference = "Stop"

Write-Host "Validating development environment..." -ForegroundColor Green

$tools = @(
    @{Name = "python"; Command = "--version"},
    @{Name = "pip"; Command = "--version"},
    @{Name = "pytest"; Command = "--version"},
    @{Name = "bandit"; Command = "--version"},
    @{Name = "safety"; Command = "--version"}
)

$success = $true

try {
    # Activate virtual environment if not already activated
    if (-not $env:VIRTUAL_ENV) {
        & ".\.venv\Scripts\Activate.ps1"
    }

    foreach ($tool in $tools) {
        try {
            $output = (& python -m $tool.Name $tool.Command 2>&1).ToString()
            Write-Host "✓ $($tool.Name) is available: $output" -ForegroundColor Green
        }
        catch {
            Write-Host "✗ $($tool.Name) is not available" -ForegroundColor Red
            $success = $false
        }
    }

    # Check directories
    $directories = @(
        "src/dashboard/static/css",
        "src/dashboard/static/js",
        "src/scanners",
        "tests/test_scanners",
        "tests/test_integration"
    )

    foreach ($dir in $directories) {
        if (Test-Path $dir) {
            Write-Host "✓ Directory exists: $dir" -ForegroundColor Green
        }
        else {
            Write-Host "✗ Missing directory: $dir" -ForegroundColor Red
            $success = $false
        }
    }

    if ($success) {
        Write-Host "`nEnvironment validation successful!" -ForegroundColor Green
    }
    else {
        throw "Environment validation failed. Please run setup_dev.ps1 to fix issues."
    }
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}