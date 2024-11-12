# src/scanners/config_scanner.py
from typing import Dict, Any, List
import logging
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from .base_scanner import BaseScanner, SecurityFinding

logger = logging.getLogger(__name__)

class ConfigScanner(BaseScanner):
    def __init__(self):
        super().__init__(scan_type="configuration")
        self.credential = DefaultAzureCredential()
        self.subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        self.resource_client = ResourceManagementClient(
            self.credential, 
            self.subscription_id
        )

    async def scan(self) -> Dict[str, Any]:
        """Scan Azure resources for security misconfigurations"""
        try:
            resources = list(self.resource_client.resources.list())
            for resource in resources:
                await self._check_resource_config(resource)
            
            return self.get_scan_results()
            
        except Exception as e:
            logger.error(f"Configuration scan failed: {str(e)}")
            raise

    async def _check_resource_config(self, resource):
        """Check individual resource configuration"""
        # Check encryption
        if encryption_issues := await self._check_encryption(resource):
            self.add_finding(SecurityFinding(
                finding_id=f"CONFIG-ENC-{resource.name}",
                severity="HIGH",
                title="Encryption Configuration Issue",
                description=encryption_issues,
                resource_id=resource.id,
                finding_type="encryption_misconfiguration"
            ))

        # Check network security
        if network_issues := await self._check_network_security(resource):
            self.add_finding(SecurityFinding(
                finding_id=f"CONFIG-NET-{resource.name}",
                severity="HIGH",
                title="Network Security Issue",
                description=network_issues,
                resource_id=resource.id,
                finding_type="network_misconfiguration"
            ))

        # Check access control
        if access_issues := await self._check_access_control(resource):
            self.add_finding(SecurityFinding(
                finding_id=f"CONFIG-IAM-{resource.name}",
                severity="MEDIUM",
                title="Access Control Issue",
                description=access_issues,
                resource_id=resource.id,
                finding_type="access_misconfiguration"
            ))

    async def _check_encryption(self, resource) -> str:
        """Check resource encryption settings"""
        # Implementation specific to resource type
        if resource.type == 'Microsoft.Storage/storageAccounts':
            return await self._check_storage_encryption(resource)
        elif resource.type == 'Microsoft.DocumentDB/databaseAccounts':
            return await self._check_cosmos_encryption(resource)
        return None

    async def _check_network_security(self, resource) -> str:
        """Check network security settings"""
        # Implementation specific to resource type
        if resource.type == 'Microsoft.Web/sites':
            return await self._check_function_network_security(resource)
        return None

    async def _check_access_control(self, resource) -> str:
        """Check access control settings"""
        # Implementation specific to resource type
        try:
            assignments = list(self.resource_client.role_assignments.list_for_resource(
                resource_group_name=resource.resource_group,
                resource_name=resource.name,
                resource_type=resource.type
            ))
            # Check for overly permissive roles
            return self._analyze_role_assignments(assignments)
        except Exception as e:
            logger.error(f"Error checking access control for {resource.name}: {str(e)}")
            return None