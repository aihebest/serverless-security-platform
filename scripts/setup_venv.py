# scripts/setup_venv.py

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return its success status."""
    print(f"Running: {' '.join(cmd)}")
    try:
        process = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        print(process.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Error output: {e.stderr}")
        return False

def setup_environment():
    """Set up the virtual environment and install dependencies."""
    try:
        # Get paths
        project_root = Path.cwd()
        venv_path = project_root / ".venv"
        python_path = Path(sys.executable)
        
        # Clean up existing environment
        if venv_path.exists():
            print("Removing existing virtual environment...")
            shutil.rmtree(venv_path, ignore_errors=True)
        
        # Create virtual environment
        print("Creating virtual environment...")
        if not run_command([sys.executable, "-m", "venv", str(venv_path)]):
            raise Exception("Failed to create virtual environment")

        # Get the path to the virtual environment Python and pip
        if os.name == 'nt':  # Windows
            venv_python = venv_path / "Scripts" / "python.exe"
            venv_pip = venv_path / "Scripts" / "pip.exe"
        else:  # Unix
            venv_python = venv_path / "bin" / "python"
            venv_pip = venv_path / "bin" / "pip"

        # Basic setup commands
        commands = [
            [str(venv_pip), "install", "--upgrade", "pip"],
            [str(venv_pip), "install", "wheel"],
            [str(venv_pip), "install", "setuptools"],
            # Install core dependencies first
            [str(venv_pip), "install", "packaging==21.3"],
            [str(venv_pip), "install", "attrs==21.4.0"],
            [str(venv_pip), "install", "async-timeout==4.0.0"],
            # Install main requirements
            [str(venv_pip), "install", "-r", "requirements.txt"],
            # Install dev requirements
            [str(venv_pip), "install", "-r", "requirements-dev.txt"]
        ]

        # Run all commands
        for cmd in commands:
            if not run_command(cmd):
                raise Exception(f"Failed to execute: {' '.join(cmd)}")

        print("\nEnvironment setup completed successfully!")
        return True

    except Exception as e:
        print(f"\nError during setup: {e}")
        return False

if __name__ == "__main__":
    sys.exit(0 if setup_environment() else 1)