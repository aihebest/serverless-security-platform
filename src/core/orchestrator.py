# Update to src/core/orchestrator.py

from typing import Dict, Any, List
from datetime import datetime
import logging
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

    # ... (keep your existing methods) ...

    async def run_scheduled_assessment(self) -> Dict[str, Any]:
        """
        Runs scheduled security assessment across all configured scan types
        """
        try:
            assessment_id = f"scheduled_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Notify assessment start
            await self.signalr_client.send_message(
                "scheduledAssessmentStarted",
                {
                    "assessment_id": assessment_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

            # Get scan configuration
            scan_config = await self._get_scheduled_scan_config()
            
            # Run all configured scans concurrently
            scan_tasks = []
            for scan_type, config in scan_config['scans'].items():
                scan_tasks.append(
                    self.scanning_service.execute_scan(scan_type, config)
                )
            
            # Wait for all scans to complete
            scan_results = await asyncio.gather(*scan_tasks, return_exceptions=True)
            
            # Process results and handle any errors
            processed_results = await self._process_scheduled_scan_results(
                scan_results, 
                scan_config['scans'].keys()
            )

            # Generate comprehensive report
            metrics = await self.security_monitor.get_current_metrics()
            incidents = await self.incident_manager.get_active_incidents()
            
            report = await self.report_generator.generate_security_report(
                scan_results=processed_results['successful_scans'],
                metrics=metrics,
                incidents=incidents,
                report_type="scheduled"
            )

            # Store report
            report_id = await self.report_storage.store_report(report)

            # Send completion notification
            await self.signalr_client.send_message(
                "scheduledAssessmentCompleted",
                {
                    "assessment_id": assessment_id,
                    "report_id": report_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "summary": report['summary'],
                    "failed_scans": processed_results['failed_scans']
                }
            )

            return {
                "assessment_id": assessment_id,
                "report_id": report_id,
                "status": "completed",
                "summary": report['summary'],
                "scan_results": processed_results
            }

        except Exception as e:
            logger.error(f"Scheduled assessment failed: {str(e)}")
            await self.signalr_client.send_message(
                "scheduledAssessmentFailed",
                {
                    "assessment_id": assessment_id,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            raise

    async def _get_scheduled_scan_config(self) -> Dict[str, Any]:
        """
        Gets configuration for scheduled scans
        """
        return {
            'scans': {
                'vulnerability': {
                    'severity_threshold': 'MEDIUM',
                    'scan_timeout': 300
                },
                'sast': {
                    'languages': ['python', 'javascript'],
                    'scan_timeout': 600
                },
                'container': {
                    'registries': ['acr.azurecr.io'],
                    'scan_timeout': 300
                },
                'compliance': {
                    'standards': ['CIS', 'NIST'],
                    'scan_timeout': 900
                }
            }
        }

    async def _process_scheduled_scan_results(
        self,
        scan_results: List[Any],
        scan_types: List[str]
    ) -> Dict[str, Any]:
        """
        Processes results from scheduled scans
        """
        successful_scans = []
        failed_scans = []

        for result, scan_type in zip(scan_results, scan_types):
            if isinstance(result, Exception):
                failed_scans.append({
                    'type': scan_type,
                    'error': str(result)
                })
                continue

            successful_scans.append(result)
            
            # Process critical findings immediately
            if any(finding['severity'] == 'CRITICAL' 
                  for finding in result.get('findings', [])):
                await self.handle_security_alert({
                    'severity': 'CRITICAL',
                    'title': f'Critical findings in {scan_type} scan',
                    'description': 'Scheduled scan detected critical security issues',
                    'source': 'scheduled_scan',
                    'related_findings': [f for f in result['findings'] 
                                       if f['severity'] == 'CRITICAL']
                })

        return {
            'successful_scans': successful_scans,
            'failed_scans': failed_scans
        }