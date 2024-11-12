# src/scanners/sast_scanner.py
import logging
import ast
import os
from typing import Dict, Any, List
from datetime import datetime
from .base_scanner import BaseScanner

logger = logging.getLogger(__name__)

class SASTScanner(BaseScanner):
    def __init__(self):
        super().__init__(scan_type="sast")
        self.patterns = {
            'hardcoded_secrets': [
                'password',
                'secret',
                'key',
                'token',
                'api_key'
            ],
            'security_risks': [
                'eval(',
                'exec(',
                'os.system(',
                'subprocess.call(',
                'pickle.loads('
            ],
            'sql_injection': [
                'execute(',
                'executemany(',
                'raw_input('
            ]
        }

    async def scan(self, directory: str = '.') -> Dict[str, Any]:
        """Perform static analysis security testing"""
        try:
            scan_id = f"sast_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            findings = []

            # Scan Python files
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        file_findings = await self._scan_file(file_path)
                        findings.extend(file_findings)

            return {
                'scan_id': scan_id,
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'completed',
                'findings': findings,
                'total_findings': len(findings)
            }

        except Exception as e:
            error_msg = f"SAST scan failed: {str(e)}"
            logger.error(error_msg)
            return {
                'scan_id': scan_id if 'scan_id' in locals() else 'error',
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'failed',
                'error': error_msg
            }

    async def _scan_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Scan individual Python file"""
        findings = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse AST
            tree = ast.parse(content)
            visitor = SecurityVisitor(file_path, self.patterns)
            visitor.visit(tree)
            findings.extend(visitor.findings)

            # Check for pattern matches
            findings.extend(self._check_patterns(file_path, content))

        except Exception as e:
            logger.error(f"Error scanning file {file_path}: {str(e)}")

        return findings

    def _check_patterns(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Check for pattern matches in code"""
        findings = []
        
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if pattern.lower() in content.lower():
                    findings.append({
                        'file': file_path,
                        'type': category,
                        'severity': 'HIGH' if category in ['hardcoded_secrets', 'sql_injection'] else 'MEDIUM',
                        'finding': f'Potential {category} issue: {pattern} found',
                        'line_number': self._find_line_number(content, pattern)
                    })
        
        return findings

    def _find_line_number(self, content: str, pattern: str) -> int:
        """Find line number for pattern match"""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if pattern.lower() in line.lower():
                return i
        return 0

class SecurityVisitor(ast.NodeVisitor):
    """AST visitor for security checks"""
    def __init__(self, file_path: str, patterns: Dict[str, List[str]]):
        self.file_path = file_path
        self.patterns = patterns
        self.findings = []

    def visit_Call(self, node):
        """Visit function calls"""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in ['eval', 'exec']:
                self.findings.append({
                    'file': self.file_path,
                    'type': 'dangerous_function',
                    'severity': 'HIGH',
                    'finding': f'Dangerous function call: {func_name}',
                    'line_number': node.lineno
                })
        self.generic_visit(node)

    def visit_Assign(self, node):
        """Visit assignments"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id.lower()
                if any(pattern in var_name for pattern in self.patterns['hardcoded_secrets']):
                    self.findings.append({
                        'file': self.file_path,
                        'type': 'hardcoded_secret',
                        'severity': 'HIGH',
                        'finding': f'Potential hardcoded secret in variable: {target.id}',
                        'line_number': node.lineno
                    })
        self.generic_visit(node)