# scripts/verify_environment.py

import sys
from pathlib import Path
import pkg_resources
import subprocess
import os
from typing import List, Tuple

def check_python_version() -> Tuple[bool, str]:
    required_version = (3, 9)
    current_version = sys.version_info[:2]
    is_valid = current_version >= required_version
    message = f"Python Version: {'.'.join(map(str, current_version))} ({'✓' if is_valid else '✗'})"
    return is_valid, message

def check_dependencies() -> List[Tuple[bool, str]]:
    results = []
    
    # Check required files exist
    required_files = ['requirements.txt', 'requirements-dev.txt']
    for file in required_files:
        exists = os.path.exists(file)
        results.append((exists, f"File {file} exists: {'✓' if exists else '✗'}"))
    
    # Check installed packages
    try:
        with open('requirements.txt') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        for requirement in requirements:
            try:
                pkg_resources.require(requirement)
                results.append((True, f"Package {requirement}: ✓"))
            except pkg_resources.DistributionNotFound:
                results.append((False, f"Package {requirement}: ✗ (not installed)"))
            except pkg_resources.VersionConflict:
                results.append((False, f"Package {requirement}: ✗ (version conflict)"))
    except Exception as e:
        results.append((False, f"Error checking dependencies: {str(e)}"))
    
    return results

def check_azure_functions_tools() -> Tuple[bool, str]:
    try:
        result = subprocess.run(['func', '--version'], capture_output=True, text=True)
        is_valid = result.returncode == 0
        version = result.stdout.strip() if is_valid else 'Not found'
        return is_valid, f"Azure Functions Core Tools: {version} ({'✓' if is_valid else '✗'})"
    except FileNotFoundError:
        return False, "Azure Functions Core Tools: ✗ (not installed)"

def main():
    print("=== Environment Verification ===\n")
    
    # Check Python version
    python_valid, python_message = check_python_version()
    print(python_message)

    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.append(str(project_root))
    
    # Check Azure Functions Tools
    azure_valid, azure_message = check_azure_functions_tools()
    print(azure_message)
    
    # Check dependencies
    print("\nChecking dependencies...")
    dependency_results = check_dependencies()
    for is_valid, message in dependency_results:
        print(message)
    
    # Overall status
    all_valid = python_valid and azure_valid and all(result[0] for result in dependency_results)
    print(f"\nOverall Status: {'✓ Ready' if all_valid else '✗ Issues Found'}")
    
    return 0 if all_valid else 1

if __name__ == '__main__':
    sys.exit(main())