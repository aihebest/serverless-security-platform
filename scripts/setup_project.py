# scripts/setup_project.py

import os
import sys
import subprocess
import platform
from pathlib import Path

def create_directory_structure():
    """Create the project directory structure."""
    directories = [
        "src/dashboard/static/css",
        "src/dashboard/static/js",
        "src/scanners",
        "src/monitors",
        "tests/test_scanners",
        "tests/test_integration",
        "scripts",
    ]
    
    project_root = Path(__file__).parent.parent
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        init_file = dir_path / "__init__.py"
        if not init_file.exists():
            init_file.touch()

def setup_virtual_environment():
    """Create and activate virtual environment."""
    try:
        venv_path = Path(".venv")
        if not venv_path.exists():
            subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
            print("Virtual environment created successfully")

        # Get the correct pip path based on OS
        if platform.system() == "Windows":
            pip_path = str(venv_path / "Scripts" / "python.exe")
            pip_command = [pip_path, "-m", "pip"]
        else:
            pip_path = str(venv_path / "bin" / "python")
            pip_command = [pip_path, "-m", "pip"]

        # Upgrade pip first
        subprocess.run([*pip_command, "install", "--upgrade", "pip"], check=True)
        
        # Install dependencies one by one to better handle errors
        print("Installing dependencies...")
        
        # Install core dependencies first
        subprocess.run([*pip_command, "install", "wheel"], check=True)
        subprocess.run([*pip_command, "install", "setuptools"], check=True)
        
        # Install from requirements files
        subprocess.run([*pip_command, "install", "-r", "requirements.txt"], check=True)
        subprocess.run([*pip_command, "install", "-r", "requirements-dev.txt"], check=True)
        
        print("Dependencies installed successfully")
        
        # Create activation scripts for Windows
        if platform.system() == "Windows":
            activate_script = """
@echo off
set "VIRTUAL_ENV=%~dp0\\.venv"
if defined _OLD_VIRTUAL_PROMPT (
    set "PROMPT=%_OLD_VIRTUAL_PROMPT%"
) else (
    set "_OLD_VIRTUAL_PROMPT=%PROMPT%"
)
set "PROMPT=(.venv) %PROMPT%"
if not defined VIRTUAL_ENV_DISABLE_PROMPT (
    set "VIRTUAL_ENV_DISABLE_PROMPT="
)
set "_OLD_VIRTUAL_PATH=%PATH%"
set "PATH=%VIRTUAL_ENV%\\Scripts;%PATH%"
            """
            
            activate_path = Path("scripts") / "activate.bat"
            with open(activate_path, "w") as f:
                f.write(activate_script)
            
            print("\nTo activate the virtual environment, run:")
            print("scripts\\activate.bat")
        else:
            print("\nTo activate the virtual environment, run:")
            print("source .venv/bin/activate")

    except subprocess.CalledProcessError as e:
        print(f"Error setting up virtual environment: {e}")
        sys.exit(1)

def main():
    try:
        print("Setting up project structure...")
        create_directory_structure()
        
        print("\nSetting up virtual environment...")
        setup_virtual_environment()
        
        print("\nProject setup completed successfully!")
        
    except Exception as e:
        print(f"Error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()