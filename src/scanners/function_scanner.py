# src/scanners/function_scanner.py
from typing import Dict, Any, List
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.mgmt.web import WebSiteManagementClient
from .base_scanner import BaseScanner

class FunctionScanner(BaseScanner):
    def __init__(self):
        super().__init__()
        self.credential = DefaultAzureCredential()
        
    async def scan(self) -> Dict[str, Any]:
        """Scan Azure Functions for security issues"""
        try:
            functions = await self._get_deployed_functions()
            scan_results = await self._scan_functions(functions)
            
            return {
                "scan_type": "function",
                "timestamp": datetime.utcnow().isoformat(),
                "functions_scanned": len(functions),
                "findings": scan_results
            }
        except Exception as e:
            return {
                "scan_type": "function",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "error",
                "error": str(e)
            }
    
    async def _get_deployed_functions(self) -> List[Dict[str, Any]]:
        """Get list of deployed Azure Functions"""
        client = WebSiteManagementClient(
            self.credential,
            self.config['subscription_id']
        )
        
        functions = []
        for function_app in client.web_apps.list():
            if function_app.kind == 'functionapp':
                functions.append({
                    "name": function_app.name,
                    "location": function_app.location,
                    "resource_group": function_app.resource_group,
                    "settings": await self._get_function_settings(client, function_app)
                })
        return functions
    
    async def _scan_functions(self, functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Scan each function for security issues"""
        findings = []
        for function in functions:
            security_issues = await self._check_function_security(function)
            if security_issues:
                findings.append({
                    "function_name": function['name'],
                    "issues": security_issues
                })
        return findings
    
    async def _check_function_security(self, function: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check individual function for security issues"""
        issues = []
        settings = function.get('settings', {})
        
        # Check authentication
        if not settings.get('authenticationEnabled'):
            issues.append({
                "severity": "HIGH",
                "category": "Authentication",
                "description": "Function authentication is not enabled"
            })
            
        # Check HTTPS
        if not settings.get('httpsOnly'):
            issues.append({
                "severity": "HIGH",
                "category": "Transport Security",
                "description": "HTTPS-only mode is not enabled"
            })
            
        # Check runtime version
        if settings.get('runtime_version', '').startswith('~2'):
            issues.append({
                "severity": "MEDIUM",
                "category": "Runtime",
                "description": "Using outdated runtime version"
            })
            
        return issues