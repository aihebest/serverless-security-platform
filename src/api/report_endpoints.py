# src/api/report_endpoints.py

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime
import logging

from ..reporting.report_generator import ReportGenerator
from ..reporting.report_storage import ReportStorage
from ..scanners.scanning_service import ScanningService
from ..monitors.security_monitor import SecurityMonitor
from ..incident_response.incident_manager import IncidentManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/reports")

class ReportRequest(BaseModel):
    report_type: str = "full"
    time_period: str = "last_7_days"
    include_charts: bool = True
    format: str = "html"

class ReportResponse(BaseModel):
    report_id: str
    status: str
    download_url: Optional[str] = None

class ReportServices:
    def __init__(self):
        self.report_generator = ReportGenerator()
        self.report_storage = ReportStorage()
        self.scanning_service = ScanningService()
        self.security_monitor = SecurityMonitor()
        self.incident_manager = IncidentManager()

    async def generate_report(self, request: ReportRequest) -> Dict[str, Any]:
        """Generate a new security report"""
        try:
            # Gather data from different services
            metrics = await self.security_monitor.get_current_metrics()
            scan_results = await self.scanning_service.get_recent_scans(10)
            incidents = await self.incident_manager.get_active_incidents()

            # Generate report
            report = await self.report_generator.generate_security_report(
                scan_results=scan_results,
                metrics=metrics,
                incidents=incidents,
                report_type=request.report_type,
                time_period=request.time_period
            )

            # Store report
            report_id = await self.report_storage.store_report(report)

            return {
                'report_id': report_id,
                'status': 'completed',
                'download_url': f"/api/v1/reports/{report_id}/download"
            }

        except Exception as e:
            logger.error(f"Failed to generate report: {str(e)}")
            raise

report_services = ReportServices()

@router.post("", response_model=ReportResponse)
async def create_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Create a new security report"""
    try:
        return await report_services.generate_report(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{report_id}")
async def get_report(report_id: str) -> Dict[str, Any]:
    """Get a specific report"""
    try:
        report = await report_services.report_storage.get_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
async def list_reports(
    report_type: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """List available reports"""
    try:
        return await report_services.report_storage.list_reports(
            report_type=report_type,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{report_id}")
async def delete_report(report_id: str):
    """Delete a report"""
    try:
        await report_services.report_storage.delete_report(report_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))