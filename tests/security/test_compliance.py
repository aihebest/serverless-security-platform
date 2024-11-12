# tests/security/test_compliance.py
import pytest
from src.reporting.report_generator import ReportGenerator

@pytest.mark.asyncio
async def test_compliance_report_generation(test_config):
    report_generator = ReportGenerator(test_config)
    report_data = await report_generator.generate_compliance_report()
    
    assert report_data is not None
    assert 'compliance_score' in report_data
    assert 'security_controls' in report_data
    assert 'recommendations' in report_data

@pytest.mark.asyncio
async def test_security_control_validation():
    report_generator = ReportGenerator()
    controls = await report_generator.validate_security_controls()
    
    assert controls is not None
    assert 'encryption' in controls
    assert 'access_control' in controls
    assert 'network_security' in controls
    
    # Verify specific security controls
    assert controls['encryption']['status'] == 'enabled'
    assert controls['access_control']['rbac_enabled'] == True

@pytest.mark.asyncio
async def test_compliance_status():
    report_generator = ReportGenerator()
    status = await report_generator.get_compliance_status()
    
    assert status is not None
    assert 'overall_status' in status
    assert 'last_scan_date' in status
    assert 'critical_findings' in status