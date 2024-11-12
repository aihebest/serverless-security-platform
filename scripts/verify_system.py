# scripts/verify_system.py

import asyncio
import logging
import json
from datetime import datetime
import os
from typing import Dict, Any

from src.monitors.security_monitor import SecurityMonitor
from src.incident_response.incident_manager import IncidentManager
from src.scanners.scanning_service import ScanningService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemVerification:
    def __init__(self):
        self.security_monitor = SecurityMonitor()
        self.incident_manager = IncidentManager()
        self.scanning_service = ScanningService()
        self.results = {}

    async def verify_all_systems(self):
        """Run complete system verification"""
        logger.info("Starting system verification...")
        
        try:
            # 1. Verify Security Scanning
            logger.info("\n=== Testing Security Scanner ===")
            scan_result = await self.test_security_scanner()
            self.log_test_result("Security Scanner", scan_result)

            # 2. Verify Security Monitoring
            logger.info("\n=== Testing Security Monitor ===")
            monitor_result = await self.test_security_monitor()
            self.log_test_result("Security Monitor", monitor_result)

            # 3. Verify Incident Management
            logger.info("\n=== Testing Incident Management ===")
            incident_result = await self.test_incident_management()
            self.log_test_result("Incident Management", incident_result)

            # Save verification report
            self.save_verification_report()
            
            return all(result.get('success', False) for result in self.results.values())

        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            return False

    async def test_security_scanner(self) -> Dict[str, Any]:
        """Test security scanning functionality"""
        try:
            # Test dependency scan
            test_dependencies = [
                {"name": "requests", "version": "2.26.0"},
                {"name": "django", "version": "2.2.24"}
            ]
            
            scan_results = await self.scanning_service.scan_dependencies(test_dependencies)
            
            success = (
                scan_results is not None and
                'findings' in scan_results and
                'summary' in scan_results
            )
            
            return {
                'success': success,
                'timestamp': datetime.utcnow().isoformat(),
                'details': {
                    'scan_id': scan_results.get('scan_id'),
                    'findings_count': len(scan_results.get('findings', [])),
                    'has_critical': any(
                        f.get('severity') == 'CRITICAL' 
                        for f in scan_results.get('findings', [])
                    )
                }
            }
            
        except Exception as e:
            logger.error(f"Scanner test failed: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def test_security_monitor(self) -> Dict[str, Any]:
        """Test security monitoring functionality"""
        try:
            # Get current metrics
            metrics = await self.security_monitor.get_current_metrics()
            
            # Verify metrics structure
            required_fields = ['risk_score', 'active_issues', 'incidents']
            has_required_fields = all(field in metrics for field in required_fields)
            
            return {
                'success': has_required_fields,
                'timestamp': datetime.utcnow().isoformat(),
                'details': {
                    'risk_score': metrics.get('risk_score'),
                    'active_issues': metrics.get('active_issues'),
                    'metrics_timestamp': metrics.get('timestamp')
                }
            }
            
        except Exception as e:
            logger.error(f"Monitor test failed: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def test_incident_management(self) -> Dict[str, Any]:
        """Test incident management functionality"""
        try:
            # Create test incident
            test_incident = {
                'severity': 'HIGH',
                'title': 'Test Incident',
                'description': 'Verification test incident'
            }
            
            # Test incident creation
            incident = await self.incident_manager.create_incident(test_incident)
            
            # Test incident update
            updated_incident = await self.incident_manager.update_incident(
                incident['id'],
                {'status': 'INVESTIGATING'}
            )
            
            # Test incident retrieval
            active_incidents = await self.incident_manager.get_active_incidents()
            
            success = all([
                incident is not None,
                updated_incident is not None,
                isinstance(active_incidents, list)
            ])
            
            return {
                'success': success,
                'timestamp': datetime.utcnow().isoformat(),
                'details': {
                    'incident_id': incident['id'],
                    'creation_successful': incident is not None,
                    'update_successful': updated_incident is not None,
                    'active_incidents': len(active_incidents)
                }
            }
            
        except Exception as e:
            logger.error(f"Incident management test failed: {str(e)}")
            return {'success': False, 'error': str(e)}

    def log_test_result(self, component: str, result: Dict[str, Any]):
        """Log test results"""
        self.results[component] = result
        status = "✅ PASSED" if result.get('success') else "❌ FAILED"
        logger.info(f"{component}: {status}")
        
        if 'details' in result:
            for key, value in result['details'].items():
                logger.info(f"  {key}: {value}")

    def save_verification_report(self):
        """Save verification results to file"""
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'results': self.results,
            'overall_status': all(r.get('success', False) for r in self.results.values())
        }
        
        with open('verification_report.json', 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"\nVerification report saved to verification_report.json")

async def main():
    verifier = SystemVerification()
    success = await verifier.verify_all_systems()
    
    if success:
        logger.info("\n✅ All systems verified successfully!")
        exit(0)
    else:
        logger.error("\n❌ System verification failed!")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())