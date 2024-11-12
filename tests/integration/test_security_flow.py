import pytest
import asyncio
from azure.identity import DefaultAzureCredential
from src.monitors.security_monitor import SecurityMonitor  # Updated import
from src.core.orchestrator import Orchestrator
from src.scanners.scanning_service import ScanningService
from src.incident_response.incident_manager import IncidentManager

class TestSecurityFlow:
    @pytest.fixture(autouse=True)
    async def setup(self):
        # Initialize with Azure credentials
        self.credential = DefaultAzureCredential()
        self.orchestrator = Orchestrator(credential=self.credential)
        self.scanning_service = ScanningService(credential=self.credential)
        self.incident_manager = IncidentManager(credential=self.credential)
        self.security_monitor = SecurityMonitor(credential=self.credential)  # Added monitor
        
        # Test configuration
        self.test_config = {
            "project_id": "test-project",
            "environment": "production",
            "scan_type": "security",
            "dependencies": [
                {"name": "requests", "version": "2.26.0"},
                {"name": "django", "version": "2.2.24"}
            ]
        }
        
        yield
        await self.orchestrator.shutdown()

    @pytest.mark.asyncio
    async def test_security_scan_pipeline(self):
        """Test the complete security scanning pipeline"""
        # 1. Initialize security scan
        scan_id = await self.orchestrator.initiate_security_scan(self.test_config)
        assert scan_id is not None

        # 2. Verify dependency scanning
        dependency_results = await self.scanning_service.scan_dependencies(
            self.test_config["dependencies"]
        )
        assert "vulnerabilities" in dependency_results

        # 3. Test monitoring
        metrics = await self.security_monitor.get_current_metrics()  # Added monitoring check
        assert "risk_score" in metrics
        
        # 4. Check incident creation for vulnerabilities
        if dependency_results.get("vulnerabilities"):
            incident = await self.incident_manager.create_incident({
                "scan_id": scan_id,
                "severity": "HIGH",
                "source": "dependency_scan",
                "findings": dependency_results["vulnerabilities"]
            })
            assert incident["status"] == "open"

    @pytest.mark.asyncio
    async def test_monitoring_integration(self):
        """Test security monitoring integration"""
        # 1. Get security metrics
        metrics = await self.security_monitor.get_current_metrics()
        assert metrics is not None
        
        # 2. Test alert generation
        alert_data = {
            "severity": "HIGH",
            "title": "Security Policy Violation",
            "description": "Unauthorized access attempt detected"
        }
        alert = await self.security_monitor.create_alert(alert_data)
        assert alert["id"] is not None