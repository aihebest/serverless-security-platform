import azure.functions as func
from datetime import datetime, timezone, timedelta
import json
import random
import os
import mimetypes

# Create the FunctionApp instance
app = func.FunctionApp()

def add_cors_headers(resp: func.HttpResponse) -> func.HttpResponse:
    """Add CORS headers to the response"""
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return resp

@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS)
async def health_check(req: func.HttpRequest) -> func.HttpResponse:
    response = func.HttpResponse(
        "The security platform is running",
        status_code=200,
        mimetype="text/plain"
    )
    return add_cors_headers(response)

@app.route(route="dashboard-data", auth_level=func.AuthLevel.ANONYMOUS)
async def get_dashboard_data(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Generate sample data
        current_time = datetime.now(timezone.utc)
        
        # Generate sample scan history
        scan_history = []
        for i in range(5):
            scan_time = current_time - timedelta(hours=i)
            scan_history.append({
                "timestamp": scan_time.isoformat(),
                "scan_type": "dependency" if i % 2 == 0 else "compliance",
                "results": {
                    "scan_status": "completed",
                    "total_issues": random.randint(2, 8),
                    "risk_score": round(random.uniform(60, 95), 2),
                    "findings": [
                        {"severity": "critical", "details": "Sample critical issue"},
                        {"severity": "high", "details": "Sample high issue"},
                        {"severity": "medium", "details": "Sample medium issue"},
                        {"severity": "low", "details": "Sample low issue"}
                    ]
                }
            })

        dashboard_data = {
            "security_score": {
                "current": round(random.uniform(70, 95), 2),
                "trend": {
                    "direction": "improving" if random.random() > 0.5 else "degrading",
                    "change": round(random.uniform(1, 5), 2)
                }
            },
            "active_issues": {
                "total": sum(scan["results"]["total_issues"] for scan in scan_history),
                "by_severity": {
                    "critical": random.randint(1, 3),
                    "high": random.randint(2, 5),
                    "medium": random.randint(3, 7),
                    "low": random.randint(4, 8)
                }
            },
            "compliance_status": {
                "score": round(random.uniform(75, 98), 2),
                "status": "Compliant"
            },
            "recent_scans": scan_history
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

@app.route(route="dashboard", auth_level=func.AuthLevel.ANONYMOUS)
async def serve_dashboard(req: func.HttpRequest) -> func.HttpResponse:
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'src', 'dashboard', 'index.html')
        
        if not os.path.exists(file_path):
            return func.HttpResponse(
                f"Dashboard file not found at: {file_path}",
                status_code=404
            )
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return func.HttpResponse(
            content,
            mimetype="text/html"
        )
    except Exception as e:
        return func.HttpResponse(
            f"Error serving dashboard: {str(e)}",
            status_code=500
        )
    
@app.route(route="scan/dependencies", auth_level=func.AuthLevel.ANONYMOUS)
async def scan_dependencies(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Initialize scanner
        scanner = DependencyScanner()

        # Get requirements file path from request or use default
        requirements_file = req.params.get('file', 'requirements.txt')
        file_path = os.path.join(os.path.dirname(__file__), requirements_file)
        
        if not os.path.exists(file_path):
            return func.HttpResponse(
                json.dumps({
                    "error": f"Requirements file not found: {requirements_file}"
                }),
                status_code=404,
                mimetype="application/json"
            )
        
        # Initialize and run scanner
        scanner = DependencyScanner()
        results = await scanner.scan(requirements_file)
        
        # Store results (in production, you'd use proper storage)
        scan_history = results.copy()
        scan_history['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        response = func.HttpResponse(
            json.dumps(results),
            mimetype="application/json"
        )
        return func.HttpResponse(
            json.dumps(results),
            mimetype="application/json"
        )
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
        
        # Get the absolute path to the static directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        static_dir = os.path.join(current_dir, 'src', 'dashboard', 'static')
        file_path = os.path.join(static_dir, filepath)
        
        # Security check - ensure file path is within static directory
        if not os.path.abspath(file_path).startswith(os.path.abspath(static_dir)):
            return func.HttpResponse("Invalid file path", status_code=403)
        
        if not os.path.exists(file_path):
            return func.HttpResponse(f"File not found: {filepath}", status_code=404)
        
        # Read file content
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Determine content type
        content_type, _ = mimetypes.guess_type(filepath)
        if not content_type:
            if filepath.endswith('.js'):
                content_type = 'application/javascript'
            elif filepath.endswith('.css'):
                content_type = 'text/css'
            else:
                content_type = 'application/octet-stream'
        
        response = func.HttpResponse(
            content,
            mimetype=content_type
        )
        return add_cors_headers(response)
    
    except Exception as e:
        response = func.HttpResponse(
            f"Error serving static file: {str(e)}",
            status_code=500
        )
        return add_cors_headers(response)