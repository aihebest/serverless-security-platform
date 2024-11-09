# src/storage/findings_storage.py

from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp
import json
import asyncio
from ..scanners.base_scanner import SecurityFinding

class FindingsStorage:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.storage_type = config.get('storage_type', 'azure_blob')
        self.connection_string = config.get('storage_connection_string')
        self.container_name = config.get('container_name', 'security-findings')

    async def store_finding(self, finding: SecurityFinding) -> None:
        """Store a security finding."""
        if self.storage_type == 'azure_blob':
            await self._store_in_blob(finding)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")

    async def get_findings(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        severity: Optional[str] = None
    ) -> List[SecurityFinding]:
        """Retrieve findings with optional filters."""
        if self.storage_type == 'azure_blob':
            return await self._get_from_blob(start_time, end_time, severity)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")

    async def _store_in_blob(self, finding: SecurityFinding) -> None:
        """Store finding in Azure Blob Storage."""
        from azure.storage.blob.aio import BlobServiceClient
        
        try:
            blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
            container_client = blob_service_client.get_container_client(
                self.container_name
            )
            
            # Create a blob name based on timestamp and finding ID
            blob_name = f"{finding.timestamp.strftime('%Y/%m/%d')}/{finding.finding_id}.json"
            
            # Convert finding to JSON
            finding_json = json.dumps(finding.to_dict())
            
            # Upload to blob storage
            blob_client = container_client.get_blob_client(blob_name)
            await blob_client.upload_blob(finding_json, overwrite=True)
            
        except Exception as e:
            raise Exception(f"Failed to store finding in blob storage: {str(e)}")

    async def _get_from_blob(
        self,
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        severity: Optional[str]
    ) -> List[SecurityFinding]:
        """Retrieve findings from Azure Blob Storage."""
        from azure.storage.blob.aio import BlobServiceClient
        
        findings = []
        try:
            blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
            container_client = blob_service_client.get_container_client(
                self.container_name
            )
            
            # List all blobs in the container
            async for blob in container_client.list_blobs():
                # Apply time filter if specified
                blob_time = datetime.strptime(
                    blob.name.split('/')[0:3],
                    '%Y/%m/%d'
                )
                
                if (start_time and blob_time < start_time) or \
                   (end_time and blob_time > end_time):
                    continue
                
                # Download and parse finding
                blob_client = container_client.get_blob_client(blob.name)
                data = await blob_client.download_blob()
                content = await data.content_as_text()
                finding_dict = json.loads(content)
                
                # Apply severity filter if specified
                if severity and finding_dict['severity'] != severity:
                    continue
                
                findings.append(SecurityFinding.from_dict(finding_dict))
                
            return findings
            
        except Exception as e:
            raise Exception(f"Failed to retrieve findings from blob storage: {str(e)}")