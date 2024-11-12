# src/api/security_hub.py

from signalr_core import Hub
from typing import Dict, Any, Optional
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class SecurityHub(Hub):
    def __init__(self):
        super().__init__()
        self._connected_clients = set()
        self._metrics_cache = {}
        self._update_task = None

    async def on_connect(self):
        """Handle client connection."""
        client_id = self.context.connection_id
        self._connected_clients.add(client_id)
        logger.info(f"Client connected: {client_id}")
        
        # Send initial data
        await self.send_initial_data(client_id)
        
        # Start update task if not running
        if not self._update_task:
            self._update_task = asyncio.create_task(self._periodic_updates())

    async def on_disconnect(self):
        """Handle client disconnection."""
        client_id = self.context.connection_id
        self._connected_clients.remove(client_id)
        logger.info(f"Client disconnected: {client_id}")
        
        # Stop update task if no clients
        if not self._connected_clients and self._update_task:
            self._update_task.cancel()
            self._update_task = None

    async def send_initial_data(self, client_id: str):
        """Send initial data to newly connected client."""
        try:
            # Get current metrics
            metrics = await self._get_current_metrics()
            
            # Send to specific client
            await self.clients.client(client_id).invoke(
                "InitialData",
                {
                    "metrics": metrics,
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error sending initial data: {str(e)}")

    async def broadcast_security_alert(self, alert: Dict[str, Any]):
        """Broadcast security alert to all clients."""
        try:
            await self.clients.all.invoke(
                "SecurityAlert",
                {
                    **alert,
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error broadcasting alert: {str(e)}")

    async def _periodic_updates(self):
        """Send periodic updates to all clients."""
        while self._connected_clients:
            try:
                # Get updated metrics
                metrics = await self._get_current_metrics()
                
                # Broadcast to all clients
                await self.clients.all.invoke(
                    "SecurityMetricsUpdate",
                    {
                        "metrics": metrics,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                # Cache metrics
                self._metrics_cache = metrics
                
                # Wait for next update
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in periodic update: {str(e)}")
                await asyncio.sleep(5)  # Short delay on error

    async def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current security metrics."""
        # Implementation depends on your metrics collection system
        return {
            "riskScore": 0.0,
            "vulnerabilities": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "incidents": {
                "open": 0,
                "investigating": 0,
                "resolved": 0
            },
            "lastUpdated": datetime.now().isoformat()
        }

    # Client-invokable methods
    async def request_metrics_update(self):
        """Handle client request for metrics update."""
        try:
            metrics = await self._get_current_metrics()
            await self.clients.caller.invoke(
                "SecurityMetricsUpdate",
                {
                    "metrics": metrics,
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error handling metrics update request: {str(e)}")

    async def sync_offline_data(self, data_type: str, offline_data: List[Dict[str, Any]]):
        """Handle offline data synchronization."""
        try:
            # Process offline data based on type
            if data_type == "findings":
                await self._sync_offline_findings(offline_data)
            elif data_type == "incidents":
                await self._sync_offline_incidents(offline_data)
                
            # Send confirmation to client
            await self.clients.caller.invoke(
                "SyncConfirmation",
                {
                    "type": data_type,
                    "status": "success",
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error syncing offline data: {str(e)}")
            await self.clients.caller.invoke(
                "SyncConfirmation",
                {
                    "type": data_type,
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )

    async def _sync_offline_findings(self, findings: List[Dict[str, Any]]):
        """Sync offline security findings."""
        # Implementation depends on your data storage system
        pass

    async def _sync_offline_incidents(self, incidents: List[Dict[str, Any]]):
        """Sync offline security incidents."""
        # Implementation depends on your data storage system
        pass