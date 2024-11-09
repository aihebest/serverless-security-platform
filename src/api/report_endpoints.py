# src/api/report_endpoints.py

from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Security
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import asyncio
import logging
import os
from datetime import datetime
from src.monitoring.app_insights import app_insights
from ..scanners.dependency_scanner import DependencyScanner
from ..monitors.security_monitor import SecurityMonitor
from ..incident_response.incident_manager import IncidentManager
from ..reporting.report_generator import ReportGenerator

app = FastAPI(title="Security Platform API")
api_key_header = APIKeyHeader(name="X-API-Key")
logger = logging.getLogger(__name__)

class ScanRequest(BaseModel):
    project_id: str
    repository_url: Optional[str] = None
    branch: str = "main"
    scan_type: str = "full"

class IncidentRequest(BaseModel):
    title: str
    severity: str
    description: str
    affected_components: list[str]

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@app.post("/api/v1/scan")
async def start_security_scan(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Security(verify_api_key)
) -> Dict[str, Any]:
    """Start a new security scan."""
    try:
        # Track API request
        app_insights.track_event("ScanRequestReceived", {
            'project_id': request.project_id,
            'scan_type': request.scan_type
        })
        
        scanner = DependencyScanner()
        
        # Start scan in background
        background_tasks.add_task(
            perform_security_scan,
            scanner,
            request.project_id,
            request.repository_url,
            request.branch
        )
        
        return {
            "status": "initiated",
            "scan_id": f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "project_id": request.project_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        app_insights.track_exception(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/metrics")
async def get_security_metrics(
    api_key: str = Security(verify_api_key)
) -> Dict[str, Any]:
    """Get current security metrics."""
    try:
        app_insights.track_event("MetricsRequested")
        
        monitor = SecurityMonitor()
        metrics = await monitor.get_current_metrics()
        
        # Track metrics retrieval
        app_insights.track_metric("MetricsAPILatency", metrics.get('latency', 0))
        
        return metrics
        
    except Exception as e:
        app_insights.track_exception(e)
        raise HTTPException(status_code=500, detail=str(e))