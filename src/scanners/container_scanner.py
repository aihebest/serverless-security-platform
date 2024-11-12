# src/scanners/container_scanner.py
import logging
import docker
from typing import Dict, Any, List
from datetime import datetime
from .base_scanner import BaseScanner

logger = logging.getLogger(__name__)

class ContainerScanner(BaseScanner):
    def __init__(self):
        super().__init__(scan_type="container")
        self.docker_client = docker.from_env()

    async def scan(self, image_name: str = None) -> Dict[str, Any]:
        """Scan container images for security issues"""
        try:
            scan_id = f"container_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            findings = []

            # Get image information
            if image_name:
                # Scan specific image
                findings.extend(await self._scan_image(image_name))
            else:
                # Scan all local images
                images = self.docker_client.images.list()
                for image in images:
                    for tag in image.tags:
                        findings.extend(await self._scan_image(tag))

            return {
                'scan_id': scan_id,
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'completed',
                'findings': findings,
                'total_findings': len(findings)
            }

        except Exception as e:
            error_msg = f"Container scan failed: {str(e)}"
            logger.error(error_msg)
            return {
                'scan_id': scan_id if 'scan_id' in locals() else 'error',
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'failed',
                'error': error_msg
            }

    async def _scan_image(self, image_name: str) -> List[Dict[str, Any]]:
        """Scan individual container image"""
        findings = []
        try:
            # Get image details
            image = self.docker_client.images.get(image_name)
            history = image.history()
            config = image.attrs['Config']

            # Check for security issues
            findings.extend(self._check_base_image(image_name, history))
            findings.extend(self._check_exposed_ports(config))
            findings.extend(self._check_environment(config))
            findings.extend(self._check_user(config))
            findings.extend(self._check_healthcheck(config))

        except Exception as e:
            logger.error(f"Error scanning image {image_name}: {str(e)}")

        return findings

    def _check_base_image(self, image_name: str, history: List[Dict]) -> List[Dict[str, Any]]:
        """Check base image security"""
        findings = []
        try:
            base_image = history[-1]['Tags'][0] if history[-1].get('Tags') else 'unknown'
            if 'latest' in base_image:
                findings.append({
                    'type': 'base_image',
                    'severity': 'MEDIUM',
                    'finding': f'Using latest tag in base image: {base_image}',
                    'image': image_name
                })
        except Exception as e:
            logger.error(f"Error checking base image: {str(e)}")
        return findings

    def _check_exposed_ports(self, config: Dict) -> List[Dict[str, Any]]:
        """Check exposed ports"""
        findings = []
        try:
            exposed_ports = config.get('ExposedPorts', {})
            for port in exposed_ports:
                if port.endswith('/tcp'):
                    port_num = int(port.split('/')[0])
                    if port_num < 1024:
                        findings.append({
                            'type': 'exposed_port',
                            'severity': 'MEDIUM',
                            'finding': f'Exposed privileged port: {port}',
                            'recommendation': 'Use non-privileged ports (>1024)'
                        })
        except Exception as e:
            logger.error(f"Error checking exposed ports: {str(e)}")
        return findings

    def _check_environment(self, config: Dict) -> List[Dict[str, Any]]:
        """Check environment variables"""
        findings = []
        try:
            env_vars = config.get('Env', [])
            for env in env_vars:
                if any(secret in env.lower() for secret in ['password', 'secret', 'key', 'token']):
                    findings.append({
                        'type': 'environment',
                        'severity':