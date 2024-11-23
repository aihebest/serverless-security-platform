import azure.functions as func
from datetime import datetime, timezone, timedelta
import json
import os
import mimetypes
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.router import router, api
from src.core.orchestrator import SecurityOrchestrator
from src.scanners.scanning_service import ScanningService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the FunctionApp instance
app = func.FunctionApp()

# Create FastAPI instance
fastapi_app = FastAPI(title="Security Platform API")

# Initialize orchestrator
orchestrator = SecurityOrchestrator()

# Add CORS middleware
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv('ALLOWED_ORIGINS', '*')],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
fastapi_app.include_router(router)

def add_cors_headers(resp: func.HttpResponse) -> func.HttpResponse:
    """Add CORS headers to the response"""
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return resp

@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS)
async def health_check(req: func.HttpRequest) -> func.HttpResponse:
    try:
        status = await orchestrator.get_security_status("system")
        response = func.HttpResponse(
            json.dumps({
                "status": "healthy",
                "security_status": status,
                "timestamp": datetime.utcnow().isoformat()
            }),
            mimetype="application/json"
        )
        return add_cors_headers(response)
    except Exception as e:
        response = func.HttpResponse(
            json.dumps({"status": "unhealthy", "error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
        return add_cors_headers(response)

@app.route(route="api/{*route}", auth_level=func.AuthLevel.ANONYMOUS)
async def api_routes(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Handle API routes using FastAPI"""
    return await func.AsgiMiddleware(fastapi_app).handle_async(req, context)

@app.route(route="dashboard-data", auth_level=func.AuthLevel.ANONYMOUS)
async def get_dashboard_data(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get security status from orchestrator
        status = await orchestrator.get_security_status("default")
        
        dashboard_data = {
            "security_score": {
                "current": status['metrics'].get('risk_score', 0),
                "trend": status['metrics'].get('trend', {})
            },
            "active_issues": {
                "total": status['metrics'].get('total_issues', 0),
                "by_severity": status['metrics'].get('issues_by_severity', {})
            },
            "compliance_status": {
                "score": status['metrics'].get('compliance_score', 0),
                "status": status.get('status', 'Unknown')
            },
            "active_incidents": status['active_incidents'],
            "recent_scans": status['recent_scans']
        }
        
        response = func.HttpResponse(
            json.dumps(dashboard_data),
            mimetype="application/json"
        )
        return add_cors_headers(response)
        
    except Exception as e:
        response = func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
        return add_cors_headers(response)

@app.route(route="scan/dependencies", auth_level=func.AuthLevel.ANONYMOUS)
async def scan_dependencies(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        project_id = req_body.get('project_id', 'default')
        
        # Create assessment config
        scan_config = {
            "scan_type": "dependency",
            "dependencies": req_body.get('dependencies', [])
        }
        
        # Run security assessment using orchestrator
        assessment_result = await orchestrator.run_security_assessment(
            project_id,
            scan_config
        )
        
        response = func.HttpResponse(
            json.dumps(assessment_result),
            mimetype="application/json"
        )
        return add_cors_headers(response)
        
    except Exception as e:
        response = func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
        return add_cors_headers(response)

@app.route(route="static/{*filepath}")
async def serve_static_files(req: func.HttpRequest) -> func.HttpResponse:
    try:
        filepath = req.route_params.get('filepath')
        if not filepath:
            return func.HttpResponse("File not specified", status_code=400)
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        static_dir = os.path.join(current_dir, 'src', 'dashboard', 'static')
        file_path = os.path.join(static_dir, filepath)
        
        if not os.path.abspath(file_path).startswith(os.path.abspath(static_dir)):
            return func.HttpResponse("Invalid file path", status_code=403)
        
        if not os.path.exists(file_path):
            return func.HttpResponse(f"File not found: {filepath}", status_code=404)
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        content_type, _ = mimetypes.guess_type(filepath)
        if not content_type:
            if filepath.endswith('.js'):
                content_type = 'application/javascript'
            elif filepath.endswith('.css'):
                content_type = 'text/css'
            else:
                content_type = 'application/octet-stream'
        
        response = func.HttpResponse(content, mimetype=content_type)
        return add_cors_headers(response)
    
    except Exception as e:
        response = func.HttpResponse(
            f"Error serving static file: {str(e)}",
            status_code=500
        )
        return add_cors_headers(response)

# Initialize services on startup
@app.function_name(name="startup")
async def startup():
    try:
        # Initialize both API and orchestrator
        await api.initialize()
        await orchestrator.initialize()
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        raise

# Add to your existing function_app.py

@app.schedule(schedule="0 0 * * * *", arg_name="mytimer", run_on_startup=False,
              use_monitor=True) 
async def automated_security_scan(mytimer: func.TimerRequest) -> None:
    """
    Timer trigger for automated security scans
    Runs every hour (adjust schedule as needed)
    """
    logging.info('Automated security scan timer trigger started')

    if mytimer.past_due:
        logging.info('Scan trigger is past due')

    try:
        # Run scheduled assessment using orchestrator
        results = await orchestrator.run_scheduled_assessment()
        
        logging.info(f"Completed scheduled assessment: {results['assessment_id']}")
        
        # Log summary metrics
        successful_scans = len(results['scan_results']['successful_scans'])
        failed_scans = len(results['scan_results']['failed_scans'])
        
        logging.info(f"Scan summary: {successful_scans} successful, {failed_scans} failed")
        
    except Exception as e:
        logging.error(f'Error in automated security scan: {str(e)}')
        raise