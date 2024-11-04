# scripts/run_tests.ps1

$ErrorActionPreference = "Stop"

Write-Host "Running tests..." -ForegroundColor Green

try {
    # Activate virtual environment if not already activated
    if (-not $env:VIRTUAL_ENV) {
        & ".\.venv\Scripts\Activate.ps1"
    }

    # Run pytest with coverage
    Write-Host "Running pytest with coverage..." -ForegroundColor Yellow
    & python -m pytest tests/ -v --cov=src --cov-report=xml --cov-report=term-missing

    # Run security checks
    Write-Host "`nRunning security checks..." -ForegroundColor Yellow
    & python -m bandit -r src/ -f json -o security-report.json
    & python -m safety check

    Write-Host "`nTest suite complete!" -ForegroundColor Green
}
catch {
    Write-Host "Error running tests: $_" -ForegroundColor Red
    exit 1
}