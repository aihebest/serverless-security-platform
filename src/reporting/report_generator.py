# src/reporting/report_generator.py

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import logging
from jinja2 import Environment, FileSystemLoader
import aiofiles
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ReportConfig:
    template_dir: str = "templates"
    output_dir: str = "reports"
    report_format: str = "html"
    include_metrics: bool = True
    include_graphs: bool = True

class ReportGenerator:
    def __init__(self, config: Optional[ReportConfig] = None):
        self.config = config or ReportConfig()
        self.env = Environment(
            loader=FileSystemLoader(self.config.template_dir),
            autoescape=True
        )
        os.makedirs(self.config.output_dir, exist_ok=True)

    async def generate_security_report(
        self,
        scan_results: Dict[str, Any],
        security_metrics: Dict[str, Any],
        report_type: str = "full"
    ) -> Dict[str, Any]:
        """Generate a comprehensive security report."""
        try:
            report_data = await self._prepare_report_data(scan_results, security_metrics)
            
            # Generate different report formats
            report_files = await asyncio.gather(
                self._generate_html_report(report_data),
                self._generate_json_report(report_data),
                self._generate_pdf_report(report_data) if self.config.report_format == "pdf" else None
            )
            
            return {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'report_type': report_type,
                'report_files': [f for f in report_files if f],
                'summary': report_data['summary']
            }
            
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            return {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

    async def _prepare_report_data(
        self,
        scan_results: Dict[str, Any],
        security_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare and organize data for reporting."""
        # Process vulnerabilities by severity
        vulnerabilities = self._process_vulnerabilities(scan_results.get('findings', []))
        
        # Calculate risk metrics
        risk_metrics = self._calculate_risk_metrics(vulnerabilities)
        
        # Generate trends
        trends = await self._generate_trends(security_metrics)
        
        return {
            'summary': {
                'total_scans': scan_results.get('total_scans', 0),
                'total_vulnerabilities': len(scan_results.get('findings', [])),
                'risk_score': security_metrics.get('risk_score', 0),
                'last_scan': scan_results.get('timestamp')
            },
            'vulnerabilities': vulnerabilities,
            'metrics': risk_metrics,
            'trends': trends,
            'recommendations': await self._generate_recommendations(vulnerabilities)
        }

    def _process_vulnerabilities(self, findings: List[Dict[str, Any]]) -> Dict[str, List]:
        """Process and categorize vulnerabilities."""
        categories = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        for finding in findings:
            severity = finding.get('severity', 'medium').lower()
            if severity in categories:
                categories[severity].append({
                    'id': finding.get('id'),
                    'description': finding.get('description'),
                    'affected_component': finding.get('component'),
                    'remediation': finding.get('remediation'),
                    'cvss_score': finding.get('cvss_score'),
                    'references': finding.get('references', [])
                })
                
        return categories

    def _calculate_risk_metrics(self, vulnerabilities: Dict[str, List]) -> Dict[str, Any]:
        """Calculate risk metrics from vulnerabilities."""
        total = sum(len(v) for v in vulnerabilities.values())
        
        return {
            'total_vulnerabilities': total,
            'severity_distribution': {
                severity: len(vulns) / total * 100 if total > 0 else 0
                for severity, vulns in vulnerabilities.items()
            },
            'risk_score': self._calculate_risk_score(vulnerabilities)
        }

    def _calculate_risk_score(self, vulnerabilities: Dict[str, List]) -> float:
        """Calculate overall risk score."""
        severity_weights = {
            'critical': 10,
            'high': 7.5,
            'medium': 5,
            'low': 2.5
        }
        
        total_score = sum(
            len(vulns) * severity_weights[severity]
            for severity, vulns in vulnerabilities.items()
        )
        
        total_findings = sum(len(v) for v in vulnerabilities.values())
        
        return total_score / total_findings if total_findings > 0 else 0

    async def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML format report."""
        template = self.env.get_template('security_report.html')
        report_content = template.render(**report_data)
        
        filename = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.config.output_dir, filename)
        
        async with aiofiles.open(filepath, 'w') as f:
            await f.write(report_content)
            
        return filepath

    async def _generate_json_report(self, report_data: Dict[str, Any]) -> str:
        """Generate JSON format report."""
        filename = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.config.output_dir, filename)
        
        async with aiofiles.open(filepath, 'w') as f:
            await f.write(json.dumps(report_data, indent=2))
            
        return filepath

    async def _generate_trends(self, security_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate security trends data."""
        # Implementation depends on your historical data storage
        return {
            'vulnerability_trends': await self._get_vulnerability_trends(),
            'risk_score_trends': await self._get_risk_score_trends(),
            'incident_trends': await self._get_incident_trends()
        }

    async def _generate_recommendations(self, vulnerabilities: Dict[str, List]) -> List[Dict[str, Any]]:
        """Generate security recommendations based on findings."""
        recommendations = []
        
        # Process critical vulnerabilities first
        if vulnerabilities['critical']:
            recommendations.append({
                'priority': 'Immediate',
                'title': 'Critical Vulnerabilities Remediation',
                'description': 'Address all critical vulnerabilities immediately',
                'items': [v['remediation'] for v in vulnerabilities['critical'] if 'remediation' in v]
            })
            
        # Generate general recommendations
        if any(vulnerabilities.values()):
            recommendations.extend([
                {
                    'priority': 'High',
                    'title': 'Security Patch Management',
                    'description': 'Implement regular security patching schedule'
                },
                {
                    'priority': 'Medium',
                    'title': 'Dependency Updates',
                    'description': 'Regular update of project dependencies'
                }
            ])
            
        return recommendations