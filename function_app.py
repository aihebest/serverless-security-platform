import azure.functions as func
import logging

app = func.FunctionApp()

@app.route(route="health")
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Health check HTTP trigger function processed a request.')
    return func.HttpResponse(
        "The security platform is running",
        status_code=200
    )

@app.route(route="security-scan", auth_level=func.AuthLevel.FUNCTION)
def security_scan(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Security scan HTTP trigger function processed a request.')
    
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "Please pass a scan configuration in the request body",
            status_code=400
        )
        
    return func.HttpResponse(
        "Security scan initiated",
        status_code=200
    )