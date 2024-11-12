# src/api/router.py

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Models for request/response
class ScanRequest(BaseModel):
    project_id: str
    scan_type: str = "dependency"
    dependencies: List[Dict[str, str]]
    metadata: Optional[Dict[str, Any]] = None

class ScanResponse(BaseModel):
    scan_id: str
    status: str
    timestamp: str
    message: Optional[str] = None

class ScanResult(BaseModel):
    scan_id: str
    scan_type: str
    findings: List[Dict[str, Any]]
    summary: Dict[str, Any]
    timestamp: str

# Create router
router = APIRouter(prefix="/api/v1")

# Services
from ..scanners.scanning_service import ScanningService
from ..monitors.security_monitor import SecurityMonitor
from .signalr_client import SignalRClient

class SecurityAPI:
    def __init__(self):
        self.scanning_service = ScanningService()
        self.security_monitor = SecurityMonitor()
        self.signalr_client = SignalRClient()

    async def initialize(self):
        """Initialize API services"""
        await self.signalr_client.initialize()
        logger.info("API services initialized")

    async def start_scan(self, scan_request: ScanRequest, background_tasks: BackgroundTasks) -> ScanResponse:
        """Start a security scan"""
        try:
            # Validate request
            if not scan_request.dependencies:
                raise HTTPException(status_code=400, detail="No dependencies provided")

            # Create scan record
            scan_id = f"scan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Start scan in background
            background_tasks.add_task(
                self._run_scan,
                scan_id,
                scan_request
            )
            
            return ScanResponse(
                scan_id=scan_id,
                status="initiated",
                timestamp=datetime.utcnow().isoformat(),
                message="Scan started successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to start scan: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _run_scan(self, scan_id: str, scan_request: ScanRequest):
        """Run scan in background"""
        try:
            # Notify scan start
            await self.signalr_client.send_message(
                "scanStarted",
                {
                    "scan_id": scan_id,
                    "project_id": scan_request.project_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Run scan
            results = await self.scanning_service.scan_dependencies(
                scan_request.dependencies
            )
            
            # Process results
            await self.security_monitor.process_scan_results(results)
            
            # Notify scan completion
            await self.signalr_client.send_message(
                "scanCompleted",
                {
                    "scan_id": scan_id,
                    "findings_count": len(results['findings']),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Scan failed: {str(e)}")
            # Notify scan failure
            await self.signalr_client.send_message(
                "scanFailed",
                {
                    "scan_id": scan_id,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

# Initialize API
api = SecurityAPI()

@router.on_event("startup")
async def startup_event():
    await api.initialize()

@router.post("/scan", response_model=ScanResponse)
async def start_scan(
    scan_request: ScanRequest,
    background_tasks: BackgroundTasks
):
    return await api.start_scan(scan_request, background_tasks)

@router.get("/scan/{scan_id}", response_model=ScanResult)
async def get_scan_results(scan_id: str):
    """Get scan results by ID"""
    try:
        results = await api.scanning_service.get_scan_results(scan_id)
        if not results:
            raise HTTPException(status_code=404, detail="Scan not found")
        return results
    except Exception as e:
        logger.error(f"Failed to get scan results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scans/recent", response_model=List[ScanResult])
async def get_recent_scans(limit: int = 10):
    """Get recent scan results"""
    try:
        return await api.scanning_service.get_recent_scans(limit)
    except Exception as e:
        logger.error(f"Failed to get recent scans: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_security_metrics():
    """Get security metrics"""
    try:
        return await api.security_monitor.get_current_metrics()
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
# In your router.py or API handler
@app.post("/api/scan/full")
async def run_full_scan():
    scanning_service = ScanningService()
    return await scanning_service.scan_all()

@app.post("/api/scan/compliance")
async def run_compliance_scan():
    scanning_service = ScanningService()
    return await scanning_service.scan_compliance()