from .security_workflow import SecurityWorkflow
from .security_manager import SecurityManager

class SecurityManager:
    def __init__(self, config):
        self.config = config
        self.workflow = SecurityWorkflow(config)

    async def analyze_request(self, request_data):
        return await self.workflow.analyze_request(request_data)