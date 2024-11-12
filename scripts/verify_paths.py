# scripts/verify_paths.py

import os
from pathlib import Path

def verify_project_structure():
    project_root = Path(__file__).parent.parent
    
    required_paths = {
        "function_app.py": project_root / "function_app.py",
        "local.settings.json": project_root / "local.settings.json",
        "styles.css": project_root / "src" / "dashboard" / "static" / "css" / "styles.css",
        "dashboard.js": project_root / "src" / "dashboard" / "static" / "js" / "dashboard.js"
    }
    
    print("Verifying project structure...")
    all_exist = True
    
    for name, path in required_paths.items():
        exists = path.exists()
        status = "✓" if exists else "✗"
        print(f"{status} {name}: {path}")
        if not exists:
            all_exist = False
    
    return all_exist

if __name__ == "__main__":
    success = verify_project_structure()
    print(f"\nAll files {'exist' if success else 'do not exist'}")
    exit(0 if success else 1)