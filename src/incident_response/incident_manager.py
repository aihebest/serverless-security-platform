# src/incident_response/incident_manager.py

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from enum import Enum
import uuid
from src.monitoring.app_insights import app_insights

logger = logging.getLogger(__name__)

class IncidentStatus(Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    MITIGATING = "MITIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class IncidentPriority(Enum):
    P1 = "P1"  # Critical
    P2 = "P2"  # High
    P3 = "P3"  # Medium
    P4 = "P4"  # Low

class IncidentManager:
    async def create_incident(self, severity: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new security incident."""
        try:
            incident_id = str(uuid.uuid4())
            
            # Track incident creation
            app_insights.track_event("IncidentCreated", {
                'incident_id': incident_id,
                'severity': severity,
                'type': details.get('type')
            })
            
            incident = {
                'id': incident_id,
                'status': IncidentStatus.OPEN.value,
                'severity': severity,
                'details': details,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Track severity metrics
            app_insights.track_metric(f"Incidents_{severity.lower()}", 1)
            
            return incident
            
        except Exception as e:
            app_insights.track_exception(e)
            raise
            
    async def update_incident(self, incident_id: str, status: str = None):
        try:
            # Track incident update
            app_insights.track_event("IncidentUpdated", {
                'incident_id': incident_id,
                'new_status': status
            })
            
            # Update incident logic here
            pass
            
        except Exception as e:
            app_insights.track_exception(e)
            raise