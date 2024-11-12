# src/core/orchestrator.py

from typing import Dict, Any, List
import logging
from datetime import datetime
import asyncio
from ..scanners.scanning_service import ScanningService
from ..monitors.security_monitor import SecurityMonitor
from ..incident_response.incident_manager import IncidentManager
from ..reporting.report_generator import ReportGenerator
from ..reporting.report_storage import ReportStorage
from ..api.signalr_client import SignalRClient

logger = logging.getLogger(__name__)

class SecurityOrchestrator:
    def __init__(self):
        self.scanning_service = ScanningService()
        self.security_monitor = SecurityMonitor()
        self.incident_manager = IncidentManager()
        self.report_generator = ReportGenerator()
        self.report_storage = ReportStorage()
        self.signalr_client = SignalRClient()

    async def initialize(self):
        """Initialize all services"""
        try:
            await self.signalr_client.initialize()
            logger.info("Security orchestrator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {str(e)}")
            raise

    async def run_security_assessment(self, project_id: str, scan_config: Dict[str, Any]):
        """Run complete security assessment"""
        try:
            # Start assessment
            assessment_id = f"assessment_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            await self.signalr_client.send_message(
                "assessmentStarted",
                {
                    "assessment_id": assessment_id,
                    "project_id": project_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

            # Run security scan
            scan_results = await self.scanning_service.scan_dependencies(
                scan_config.get('dependencies', [])
            )

            # Process results
            await asyncio.gather(
                self.security_monitor.process_scan_results(scan_results),
                self.incident_manager.process_scan_findings(scan_results)
            )

            # Generate report
            metrics = await self.security_monitor.get_current_metrics()
            incidents = await self.incident_manager.get_active_incidents()
            
            report = await self.report_generator.generate_security_report(
                scan_results=[scan_results],
                metrics=metrics,
                incidents=incidents,
                report_type="full"
            )

            # Store report
            report_id = await self.report_storage.store_report(report)

            # Send completion notification
            await self.signalr_client.send_message(
                "assessmentCompleted",
                {
                    "assessment_id": assessment_id,
                    "project_id": project_id,
                    "report_id": report_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "summary": report['summary']
                }
            )

            return {
                "assessment_id": assessment_id,
                "report_id": report_id,
                "status": "completed",
                "summary": report['summary']
            }

        except Exception as e:
            logger.error(f"Assessment failed: {str(e)}")
            
            await self.signalr_client.send_message(
                "assessmentFailed",
                {
                    "assessment_id": assessment_id,
                    "project_id": project_id,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            raise

    async def get_security_status(self, project_id: str) -> Dict[str, Any]:
        """Get current security status"""
        try:
            metrics = await self.security_monitor.get_current_metrics()
            incidents = await self.incident_manager.get_active_incidents()
            recent_scans = await self.scanning_service.get_recent_scans(5)
            
            return {
                "project_id": project_id,
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": metrics,
                "active_incidents": len(incidents),
                "recent_scans": len(recent_scans),
                "status": self._determine_security_status(metrics, incidents)
            }
            
        except Exception as e:
            logger.error(f"Failed to get security status: {str(e)}")
            raise

    def _determine_security_status(
        self,
        metrics: Dict[str, Any],
        incidents: List[Dict[str, Any]]
    ) -> str:
        """Determine overall security status"""
        risk_score = metrics.get('risk_score', 0)
        critical_incidents = sum(1 for i in incidents if i['priority'] == 'P1')
        
        if critical_incidents > 0 or risk_score < 60:
            return "critical"
        elif risk_score < 80:
            return "warning"
        else:
            return "healthy"

    async def handle_security_alert(self, alert_data: Dict[str, Any]):
        """Handle incoming security alert"""
        try:
            # Create incident if needed
            if alert_data.get('severity') in ['CRITICAL', 'HIGH']:
                await self.incident_manager.create_incident({
                    'title': alert_data.get('title'),
                    'description': alert_data.get('description'),
                    'priority': 'P1' if alert_data['severity'] == 'CRITICAL' else 'P2',
                    'source': alert_data.get('source'),
                    'related_findings': alert_data.get('related_findings', [])
                })

            # Send notification
            await self.signalr_client.send_message(
                "securityAlert",
                {
                    **alert_data,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to handle security alert: {str(e)}")
            raise