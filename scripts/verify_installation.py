# scripts/verify_installation.py

import sys
import importlib

def check_import(module_name):
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✓ {module_name} (version: {version})")
        return True
    except ImportError as e:
        print(f"✗ {module_name} (error: {str(e)})")
        return False

def main():
    modules_to_check = [
        'azure.functions',
        'aiohttp',
        'pytest',
        'black',
        'flake8',
        'mypy',
        'bandit',
        'safety',
        'python-jose'
    ]

    print("Checking installed packages:")
    results = [check_import(module) for module in modules_to_check]
    
    if all(results):
        print("\nAll required packages are installed correctly!")
        return 0
    else:
        print("\nSome packages are missing or incorrectly installed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())