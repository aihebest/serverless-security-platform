# src/pages/dashboard.py
import os
import json
from azure.functions import HttpRequest, HttpResponse
import azure.functions as func
from ..scanners.scanning_service import ScanningService
from ..utils.cosmos_client import CosmosDBClient

async def main(req: HttpRequest) -> HttpResponse:
    try:
        # Initialize Cosmos DB client
        cosmos_client = CosmosDBClient()
        
        # Get latest dashboard metrics
        dashboard_data = await cosmos_client.get_latest_dashboard_metrics()
        
        # Return dashboard data
        return HttpResponse(
            body=json.dumps(dashboard_data),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        return HttpResponse(
            body=json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )