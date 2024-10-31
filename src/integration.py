from scanners.dependency_scanner import DependencyScanner
from scanners.config_scanner import ConfigurationScanner
from monitors.request_analyzer import RequestAnalyzer
from monitors.rate_limiter import RateLimiter

class SecurityManager:
    def __init__(self, config: Dict):
        self.dependency_scanner = DependencyScanner()
        self.config_scanner = ConfigurationScanner(
            config['credential'],
            config['subscription_id']
        )
        self.request_analyzer = RequestAnalyzer()
        self.rate_limiter = RateLimiter(config['redis_url'])
        
    async def analyze_request(self, request_data: Dict) -> Dict:
        """Comprehensive request analysis"""
        results = {}
        
        # Check rate limits
        rate_limit = await self.rate_limiter.check_rate_limit(
            request_data.get('client_id')
        )
        if rate_limit['limited']:
            return {'blocked': True, 'reason': 'rate_limit_exceeded'}
            
        # Analyze request patterns
        threat_analysis = await self.request_analyzer.analyze_request(request_data)
        if threat_analysis['block_recommended']:
            return {'blocked': True, 'reason': 'security_threat'}
            
        return {'blocked': False, 'analysis': threat_analysis}