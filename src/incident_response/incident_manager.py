from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging
from azure.cosmos import CosmosClient
import os

logger = logging.getLogger(__name__)

class IncidentStatus:
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    MITIGATING = "MITIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class IncidentPriority:
    P1 = "P1"  # Critical
    P2 = "P2"  # High
    P3 = "P3"  # Medium
    P4 = "P4"  # Low

class IncidentManager:
    def __init__(self):
        # Initialize Cosmos DB client
        cosmos_client = CosmosClient.from_connection_string(
            os.getenv('COSMOS_DB_CONNECTION_STRING')
        )
        self.database = cosmos_client.get_database_client(
            os.getenv('COSMOS_DB_DATABASE_NAME')
        )
        self.container = self.database.get_container_client('SecurityIncidents')

    async def create_incident(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new security incident"""
        try:
            incident_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()
            
            incident = {
                'id': incident_id,
                'status': IncidentStatus.OPEN,
                'priority': incident_data['severity'],
                'title': incident_data['title'],
                'description': incident_data['description'],
                'created_at': timestamp,
                'updated_at': timestamp,
                'assigned_to': None,
                'timeline': [{
                    'timestamp': timestamp,
                    'status': IncidentStatus.OPEN,
                    'message': 'Incident created'
                }]
            }
            
            await self.container.create_item(body=incident)
            logger.info(f"Created incident: {incident_id}")
            
            # Trigger notifications based on severity
            if incident_data['severity'] in ['P1', 'P2']:
                await self.notify_security_team(incident)
            
            return incident
            
        except Exception as e:
            logger.error(f"Failed to create incident: {str(e)}")
            raise

    async def update_incident(
        self,
        incident_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update an existing incident"""
        try:
            current = await self.get_incident(incident_id)
            if not current:
                return None
                
            # Update fields
            current.update(updates)
            current['updated_at'] = datetime.utcnow().isoformat()
            
            # Add timeline entry
            current['timeline'].append({
                'timestamp': current['updated_at'],
                'status': updates.get('status', current['status']),
                'message': updates.get('message', 'Incident updated')
            })
            
            await self.container.upsert_item(body=current)
            logger.info(f"Updated incident: {incident_id}")
            
            return current
            
        except Exception as e:
            logger.error(f"Failed to update incident: {str(e)}")
            raise

    async def get_active_incidents(self) -> List[Dict[str, Any]]:
        """Get all active incidents"""
        try:
            query = """
                SELECT * FROM c 
                WHERE c.status IN ('OPEN', 'INVESTIGATING', 'MITIGATING')
                ORDER BY c.created_at DESC
            """
            
            return list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
        except Exception as e:
            logger.error(f"Failed to get active incidents: {str(e)}")
            raise

    async def notify_security_team(self, incident: Dict[str, Any]):
        """Notify security team of critical incidents"""
        try:
            # Here you could integrate with your notification system
            # (Email, Slack, Teams, etc.)
            logger.warning(
                f"SECURITY ALERT: {incident['priority']} incident created: "
                f"{incident['title']}"
            )
            
        except Exception as e:
            logger.error(f"Failed to notify security team: {str(e)}")

    async def get_incident_metrics(self) -> Dict[str, Any]:
        """Get incident metrics"""
        try:
            query = """
                SELECT 
                    COUNT(1) as total_incidents,
                    ARRAY_LENGTH(ARRAY(SELECT VALUE r FROM r IN root WHERE r.status = 'OPEN')) as open_incidents,
                    ARRAY_LENGTH(ARRAY(SELECT VALUE r FROM r IN root WHERE r.priority = 'P1')) as p1_incidents
                FROM root
            """
            
            results = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            return results[0] if results else {
                'total_incidents': 0,
                'open_incidents': 0,
                'p1_incidents': 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get incident metrics: {str(e)}")
            raise