import azure.functions as func
import os
import mimetypes

app = func.FunctionApp()

@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS)
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        "The security platform is running",
        status_code=200,
        mimetype="text/plain"
    )

@app.route(route="dashboard", auth_level=func.AuthLevel.ANONYMOUS)
async def serve_dashboard(req: func.HttpRequest) -> func.HttpResponse:
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'src', 'dashboard', 'index.html')
        
        print(f"Looking for dashboard at: {file_path}")  # Debug print
        
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

@app.route(route="dashboard/static/{*filepath}", auth_level=func.AuthLevel.ANONYMOUS)
async def serve_static_files(req: func.HttpRequest) -> func.HttpResponse:
    try:
        filepath = req.route_params.get('filepath')
        if not filepath:
            return func.HttpResponse("File not specified", status_code=400)
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(current_dir, 'src', 'dashboard', 'static', filepath)
        
        print(f"Looking for static file at: {full_path}")  # Debug print
        
        if not os.path.exists(full_path):
            return func.HttpResponse(
                f"File not found: {filepath}",
                status_code=404
            )
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content_type, _ = mimetypes.guess_type(filepath)
        if not content_type:
            content_type = 'application/octet-stream'
        
        return func.HttpResponse(
            content,
            mimetype=content_type
        )
    except Exception as e:
        return func.HttpResponse(
            f"Error serving static file: {str(e)}",
            status_code=500
        )