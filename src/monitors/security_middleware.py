import azure.functions as func
from .runtime_monitor import RuntimeMonitor

def security_middleware(function_app: func.FunctionApp):
    monitor = RuntimeMonitor()
    
    async def middleware_handler(req: func.HttpRequest) -> func.HttpResponse:
        try:
            # Pre-execution monitoring
            request_data = await monitor.monitor_request(req)
            
            # Behavioral analysis
            analysis = await monitor.analyze_behavior(request_data)
            
            if analysis.get('threat_detected'):
                return func.HttpResponse(
                    "Access denied due to security policy",
                    status_code=403
                )
            
            # Execute original function
            response = await function_app.handle_request(req)
            
            return response
            
        except Exception as e:
            logging.error(f"Security middleware error: {str(e)}")
            raise
            
    return middleware_handler