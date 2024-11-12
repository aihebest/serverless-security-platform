# tests/test_integration/test_full_system.py

import pytest
from azure.functions import HttpRequest, Context
import json
from src.scanners.dependency_scanner import DependencyScanner
from src.monitors.security_monitor import SecurityMonitor
from src.incident_response.incident_manager import IncidentManager
from src.reporting.report_generator import ReportGenerator

class TestFullSystem:
    @pytest.fixture
    def setup_system(self):
        """Setup complete system components"""
        self.dependency_scanner = DependencyScanner()
        self.security_monitor = SecurityMonitor()
        self.incident_manager = IncidentManager()
        self.report_generator = ReportGenerator()
        
    def test_complete_security_workflow(self, setup_system):
        """Test complete security scanning and reporting workflow"""
        # 1. Simulate dependency scanning
        sample_project = {
            "name": "test-project",
            "dependencies": [
                {"name": "requests", "version": "2.26.0"},
                {"name": "flask", "version": "2.0.1"}
            ]
        }
        
        scan_results = self.dependency_scanner.scan(sample_project)
        assert scan_results is not None
        assert "vulnerabilities" in scan_results
        
        # 2. Test security monitoring
        security_metrics = self.security_monitor.analyze_scan_results(scan_results)
        assert security_metrics is not None
        assert "risk_score" in security_metrics
        
        # 3. Test incident response
        if security_metrics["risk_score"] > 7.0:
            incident = self.incident_manager.create_incident(
                severity="HIGH",
                details=scan_results
            )
            assert incident["status"] == "OPEN"
            
        # 4. Test report generation
        report = self.report_generator.generate_security_report(
            scan_results=scan_results,
            security_metrics=security_metrics
        )
        assert report is not None
        assert "summary" in report
        assert "detailed_findings" in report

    def test_api_integration(self):
        """Test API endpoints integration"""
        # Test /scan/dependencies endpoint
        req = HttpRequest(
            method='POST',
            url='/api/scan/dependencies',
            body=json.dumps({
                "project_name": "test-project",
                "dependencies": []
            }).encode()
        )
        
        # TODO: Add actual endpoint function call and response validation
        
    def test_dashboard_data_flow(self):
        """Test dashboard data flow and updates"""
        # Test dashboard data retrieval
        req = HttpRequest(
            method='GET',
            url='/api/dashboard-data',
            body=None
        )
        
        # TODO: Add actual dashboard data endpoint test
        
    def test_performance_requirements(self):
        """Test system performance under load"""
        import time
        
        start_time = time.time()
        
        # Perform scanning operation
        scan_results = self.dependency_scanner.scan({
            "name": "test-project",
            "dependencies": [{"name": "requests", "version": "2.26.0"}]
        })
        
        scan_duration = time.time() - start_time
        assert scan_duration < 5.0  # Scanning should complete within 5 seconds