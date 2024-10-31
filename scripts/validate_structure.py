import os
import json  # Add this import at the top
from typing import Dict, List

class ProjectStructureValidator:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.required_structure = {
            'src': ['scanners', 'monitors', 'incident-response', 'dashboard'],
            'infrastructure': ['terraform', 'bicep'],
            'tests': [],
            'docs': [],
            '.github/workflows': []
        }

    def validate_structure(self) -> Dict:
        """Validate project directory structure"""
        missing_dirs = []
        existing_dirs = []

        for main_dir, subdirs in self.required_structure.items():
            main_path = os.path.join(self.root_dir, main_dir)
            
            if not os.path.exists(main_path):
                missing_dirs.append(main_dir)
            else:
                existing_dirs.append(main_dir)
                for subdir in subdirs:
                    subdir_path = os.path.join(main_path, subdir)
                    if not os.path.exists(subdir_path):
                        missing_dirs.append(f"{main_dir}/{subdir}")

        results = {
            'valid': len(missing_dirs) == 0,
            'existing_directories': existing_dirs,
            'missing_directories': missing_dirs
        }
        
        return results

if __name__ == "__main__":
    validator = ProjectStructureValidator(os.getcwd())
    results = validator.validate_structure()
    print(json.dumps(results, indent=2))