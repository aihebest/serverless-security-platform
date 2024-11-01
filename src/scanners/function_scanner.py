import azure.functions as func
import logging
import json
import os
from datetime import datetime, UTC
from src.scanners.dependency_scanner import DependencyScanner

app = func.FunctionApp()

@app.route(route="health")
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint to verify the service is running"""
    logging.info('Health check HTTP trigger function processed a request.')
    return func.HttpResponse(
        json.dumps({
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat()
        }),
        mimetype="application/json",
        status_code=200
    )

@app.route(route="dashboard")
def serve_dashboard(req: func.HttpRequest) -> func.HttpResponse:
    """Serve the main dashboard HTML"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'src', 'dashboard', 'static', 'index.html')
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return func.HttpResponse(
            body=content,
            mimetype="text/html"
        )
    except Exception as e:
        logging.error(f"Failed to serve dashboard: {str(e)}")
        return func.HttpResponse(
            f"Dashboard error: {str(e)}",
            status_code=500
        )

@app.route(route="api/negotiate", auth_level=func.AuthLevel.ANONYMOUS)
def negotiate(req: func.HttpRequest) -> func.HttpResponse:
    """SignalR negotiation endpoint for real-time updates"""
    try:
        return func.SignalRConnectionInfo(hub_name="SecurityHub")
    except Exception as e:
        logging.error(f"SignalR negotiation failed: {str(e)}")
        return func.HttpResponse(str(e), status_code=500)

@app.route(route="api/security-scan", auth_level=func.AuthLevel.FUNCTION)
async def security_scan(req: func.HttpRequest) -> func.HttpResponse:
    """Execute security scan based on the request parameters"""
    logging.info('Security scan HTTP trigger function processed a request.')
    
    try:
        req_body = req.get_json()
        scan_type = req_body.get('scan_type')
        target = req_body.get('target')
        
        if not scan_type or not target:
            return func.HttpResponse(
                json.dumps({
                    "error": "Missing required parameters",
                    "message": "Please provide scan_type and target in the request body"
                }),
                mimetype="application/json",
                status_code=400
            )

        if scan_type == "dependency":
            scanner = DependencyScanner()
            results = await scanner.scan(target)
            
            # Prepare SignalR message
            message = {
                'scan_type': scan_type,
                'target': target,
                'timestamp': datetime.now(UTC).isoformat(),
                'results': results
            }
            
            # Send real-time update via SignalR
            try:
                await req.SignalROutput.send(
                    'newScanResult',
                    arguments=[message]
                )
            except Exception as signalr_error:
                logging.warning(f"Failed to send SignalR update: {str(signalr_error)}")
            
            return func.HttpResponse(
                json.dumps(results),
                mimetype="application/json",
                status_code=200
            )
        else:
            return func.HttpResponse(
                json.dumps({
                    "error": "Invalid scan type",
                    "message": f"Scan type '{scan_type}' is not supported"
                }),
                mimetype="application/json",
                status_code=400
            )

    except ValueError as ve:
        error_message = {
            "error": "Invalid request body",
            "message": str(ve)
        }
        return func.HttpResponse(
            json.dumps(error_message),
            mimetype="application/json",
            status_code=400
        )
    except Exception as e:
        logging.error(f"Scan failed: {str(e)}")
        error_message = {
            "error": "Internal server error",
            "message": str(e)
        }
        return func.HttpResponse(
            json.dumps(error_message),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="api/scan-history")
def get_scan_history(req: func.HttpRequest) -> func.HttpResponse:
    """Retrieve scan history"""
    try:
        # In a real implementation, this would fetch from a database
        # For now, return mock data
        history = [
            {
                "id": "1",
                "scan_type": "dependency",
                "timestamp": datetime.now(UTC).isoformat(),
                "status": "completed",
                "findings": 2
            }
        ]
        return func.HttpResponse(
            json.dumps(history),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Failed to retrieve scan history: {str(e)}")
        return func.HttpResponse(str(e), status_code=500)

@app.route(route="api/export-report")
def export_report(req: func.HttpRequest) -> func.HttpResponse:
    """Export security scan report"""
    try:
        # Get query parameters
        scan_id = req.params.get('scan_id')
        format = req.params.get('format', 'json')

        if not scan_id:
            return func.HttpResponse(
                "Missing scan_id parameter",
                status_code=400
            )

        # Mock report data
        report = {
            "scan_id": scan_id,
            "generated_at": datetime.now(UTC).isoformat(),
            "results": {
                "vulnerabilities": [],
                "compliance": [],
                "recommendations": []
            }
        }

        if format == 'json':
            return func.HttpResponse(
                json.dumps(report),
                mimetype="application/json",
                status_code=200
            )
        else:
            return func.HttpResponse(
                "Unsupported format",
                status_code=400
            )
    except Exception as e:
        logging.error(f"Failed to export report: {str(e)}")
        return func.HttpResponse(str(e), status_code=500)