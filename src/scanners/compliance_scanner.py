# src/scanners/compliance_scanner.py
from typing import Dict, List
import yaml
from .base_scanner import BaseScanner

class ComplianceScanner(BaseScanner):
    """Scanner for checking compliance against security standards"""
    
    def __init__(self, logger=None):
        super().__init__(logger)
        self.compliance_rules = self._load_compliance_rules()
    
    def _load_compliance_rules(self) -> Dict:
        """Load compliance rules from configuration"""
        # In practice, load from a file or service
        return {
            'password_policy': {
                'min_length': 12,
                'require_special_chars': True,
                'require_numbers': True,
                'max_age_days': 90
            },
            'encryption': {
                'require_tls': True,
                'min_tls_version': '1.2',
                'require_at_rest': True
            },
            'access_control': {
                'require_mfa': True,
                'max_session_duration': 12,
                'require_rbac': True
            }
        }
    
    async def scan(self, config: Dict) -> Dict:
        """Scan configuration for compliance violations"""
        try:
            violations = []
            
            # Check password policy
            if 'password_policy' in config:
                violations.extend(
                    self._check_password_policy(config['password_policy'])
                )
            
            # Check encryption settings
            if 'encryption' in config:
                violations.extend(
                    self._check_encryption(config['encryption'])
                )
            
            # Check access control
            if 'access_control' in config:
                violations.extend(
                    self._check_access_control(config['access_control'])
                )
            
            return self.generate_report(violations)
            
        except Exception as e:
            if self.logger:
                self.logger.log_alert(
                    "high",
                    f"Compliance scan failed: {str(e)}",
                    {"config": config}
                )
            return {
                'timestamp': datetime.now(UTC).isoformat(),
                'error': str(e),
                'scan_status': 'failed'
            }
    
    def _check_password_policy(self, policy: Dict) -> List[Dict]:
        """Check password policy compliance"""
        violations = []
        rules = self.compliance_rules['password_policy']
        
        if policy.get('min_length', 0) < rules['min_length']:
            violations.append({
                'severity': 'high',
                'category': 'password_policy',
                'message': f"Password minimum length ({policy.get('min_length')}) below required {rules['min_length']}"
            })
        
        if not policy.get('require_special_chars') and rules['require_special_chars']:
            violations.append({
                'severity': 'medium',
                'category': 'password_policy',
                'message': "Special characters not required in passwords"
            })
        
        return violations
    
    def _check_encryption(self, config: Dict) -> List[Dict]:
        """Check encryption settings compliance"""
        violations = []
        rules = self.compliance_rules['encryption']
        
        if not config.get('require_tls') and rules['require_tls']:
            violations.append({
                'severity': 'critical',
                'category': 'encryption',
                'message': "TLS encryption not enforced"
            })
        
        if not config.get('require_at_rest') and rules['require_at_rest']:
            violations.append({
                'severity': 'high',
                'category': 'encryption',
                'message': "At-rest encryption not enforced"
            })
        
        return violations
    
    def _check_access_control(self, config: Dict) -> List[Dict]:
        """Check access control compliance"""
        violations = []
        rules = self.compliance_rules['access_control']
        
        if not config.get('require_mfa') and rules['require_mfa']:
            violations.append({
                'severity': 'critical',
                'category': 'access_control',
                'message': "Multi-factor authentication not required"
            })
        
        if not config.get('require_rbac') and rules['require_rbac']:
            violations.append({
                'severity': 'high',
                'category': 'access_control',
                'message': "Role-based access control not implemented"
            })
        
        return violations