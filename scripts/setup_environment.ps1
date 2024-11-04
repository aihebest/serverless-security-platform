# scripts/setup_environment.ps1

# Ensure we're running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Please run this script as Administrator"
    exit
}

# Set execution policy for this process only
$prevExecutionPolicy = Get-ExecutionPolicy
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

try {
    # Define paths
    $pythonPath = "C:\Users\admin\AppData\Local\Programs\Python\Python39\python.exe"
    $projectPath = $PWD
    $venvPath = Join-Path $projectPath ".venv"
    $tempPath = [System.IO.Path]::GetTempPath()

    # Clean up temp directory
    Write-Host "Cleaning up temp directory..."
    Get-ChildItem -Path $tempPath -Filter "pip-*" | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue

    # Remove existing virtual environment
    Write-Host "Removing existing virtual environment (if any)..."
    if (Test-Path $venvPath) {
        deactivate
        Remove-Item -Recurse -Force $venvPath -ErrorAction SilentlyContinue
    }

    # Create new virtual environment
    Write-Host "Creating virtual environment..."
    & $pythonPath -m venv $venvPath --clear

    # Activate virtual environment
    Write-Host "Activating virtual environment..."
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    . $activateScript

    # Fix permissions on virtual environment
    $venvScripts = Join-Path $venvPath "Scripts"
    $acl = Get-Acl $venvScripts
    $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    $rule = New-Object System.Security.AccessControl.FileSystemAccessRule($currentUser, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow")
    $acl.SetAccessRule($rule)
    Set-Acl $venvScripts $acl

    # Install packages in order
    Write-Host "Installing packages..."
    $pipCmd = Join-Path $venvScripts "pip.exe"

    # Basic packages first
    $commands = @(
        "install --upgrade pip",
        "install wheel",
        "install setuptools",
        "install packaging==21.3",
        "install attrs==21.4.0",
        "install async-timeout==4.0.0",
        "install aiohttp==3.9.1",
        "install azure-functions==1.12.0",
        "install azure-functions-worker==1.1.8",
        "install -r requirements.txt",
        "install -r requirements-dev.txt"
    )

    foreach ($cmd in $commands) {
        Write-Host "Running: $pipCmd $cmd"
        $process = Start-Process -FilePath $pipCmd -ArgumentList $cmd.Split() -NoNewWindow -Wait -PassThru
        if ($process.ExitCode -ne 0) {
            Write-Error "Failed to execute: pip $cmd"
            exit 1
        }
    }

    Write-Host "Environment setup completed successfully!" -ForegroundColor Green

} catch {
    Write-Error "An error occurred: $_"
    exit 1
} finally {
    # Restore previous execution policy
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy $prevExecutionPolicy -Force
}