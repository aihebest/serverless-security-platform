# src/reporting/report_storage.py

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import asyncio
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient
import os
import json

logger = logging.getLogger(__name__)

class ReportStorage:
    def __init__(self):
        # Initialize Blob Storage
        self.blob_service_client = BlobServiceClient.from_connection_string(
            os.getenv('STORAGE_CONNECTION_STRING')
        )
        self.container_client = self.blob_service_client.get_container_client(
            'security-reports'
        )

        # Initialize Cosmos DB
        cosmos_client = CosmosClient.from_connection_string(
            os.getenv('COSMOS_DB_CONNECTION_STRING')
        )
        self.database = cosmos_client.get_database_client(
            os.getenv('COSMOS_DB_DATABASE_NAME')
        )
        self.container = self.database.get_container_client('Reports')

    async def store_report(self, report: Dict[str, Any]) -> str:
        """Store report content and metadata"""
        try:
            report_id = report['report_id']
            
            # Store report content in Blob Storage
            blob_client = self.container_client.get_blob_client(f"{report_id}.html")
            await blob_client.upload_blob(
                report['content'],
                overwrite=True
            )
            
            # Store metadata in Cosmos DB
            metadata = {
                'id': report_id,
                'type': report['type'],
                'generated_at': report['generated_at'],
                'period': report['period'],
                'summary': report['summary'],
                'blob_url': blob_client.url
            }
            
            await self.container.create_item(body=metadata)
            
            return report_id
            
        except Exception as e:
            logger.error(f"Failed to store report: {str(e)}")
            raise

    async def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve report by ID"""
        try:
            # Get metadata from Cosmos DB
            query = f"SELECT * FROM c WHERE c.id = '{report_id}'"
            results = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            if not results:
                return None
                
            metadata = results[0]
            
            # Get content from Blob Storage
            blob_client = self.container_client.get_blob_client(f"{report_id}.html")
            content = await blob_client.download_blob()
            content_str = await content.content_as_text()
            
            return {
                **metadata,
                'content': content_str
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve report: {str(e)}")
            raise

    async def list_reports(
        self,
        report_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """List available reports"""
        try:
            if report_type:
                query = f"""
                    SELECT * FROM c
                    WHERE c.type = '{report_type}'
                    ORDER BY c.generated_at DESC
                    OFFSET 0 LIMIT {limit}
                """
            else:
                query = f"""
                    SELECT * FROM c
                    ORDER BY c.generated_at DESC
                    OFFSET 0 LIMIT {limit}
                """
                
            return list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
        except Exception as e:
            logger.error(f"Failed to list reports: {str(e)}")
            raise

    async def delete_report(self, report_id: str):
        """Delete a report"""
        try:
            # Delete from Blob Storage
            blob_client = self.container_client.get_blob_client(f"{report_id}.html")
            await blob_client.delete_blob()
            
            # Delete from Cosmos DB
            await self.container.delete_item(
                item=report_id,
                partition_key=report_id
            )
            
            logger.info(f"Deleted report: {report_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete report: {str(e)}")
            raise