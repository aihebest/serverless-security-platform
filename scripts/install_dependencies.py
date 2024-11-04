# scripts/install_dependencies.py

import subprocess
import sys
import os
from pathlib import Path

class DependencyInstaller:
    def __init__(self):
        self.python_path = Path(sys.executable)
        self.venv_path = Path(".venv")
        self.pip_path = self.venv_path / "Scripts" / "pip.exe"

    def run_command(self, command):
        """Run a command and handle errors."""
        print(f"Running command: {' '.join(command)}")
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                shell=True  # Added for Windows compatibility
            )
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {' '.join(command)}")
            print(f"Error output: {e.stderr if hasattr(e, 'stderr') else str(e)}")
            return False

    def install_dependencies(self):
        """Install dependencies in the correct order."""
        try:
            # Use the full path to pip
            pip_cmd = str(self.pip_path)
            
            commands = [
                # Upgrade pip and core tools
                f'"{pip_cmd}" install --upgrade pip',
                f'"{pip_cmd}" install --upgrade setuptools wheel',
                
                # Uninstall potentially conflicting packages
                f'"{pip_cmd}" uninstall -y packaging black pytest safety',
                
                # Install core dependencies with specific versions
                f'"{pip_cmd}" install packaging==21.3',
                f'"{pip_cmd}" install python-dateutil==2.8.2',
                f'"{pip_cmd}" install attrs==21.4.0',
                
                # Install Azure dependencies
                f'"{pip_cmd}" install azure-functions==1.12.0',
                f'"{pip_cmd}" install azure-functions-worker==1.1.8',
                
                # Install remaining requirements
                f'"{pip_cmd}" install -r requirements.txt',
                f'"{pip_cmd}" install -r requirements-dev.txt'
            ]

            for command in commands:
                if not self.run_command(command):
                    return False
            return True

        except Exception as e:
            print(f"Error during installation: {e}")
            return False

def main():
    installer = DependencyInstaller()
    if installer.install_dependencies():
        print("\nDependencies installed successfully!")
        return 0
    else:
        print("\nDependency installation failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())