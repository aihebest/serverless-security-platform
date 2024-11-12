# src/api/signalr_client.py

import os
import aiohttp
import json
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class SignalRClient:
    def __init__(self):
        self.connection_string = os.getenv('SIGNALR_CONNECTION_STRING')
        self.hub_url = None
        self.access_token = None
        self.session = None

    async def initialize(self):
        """Initialize SignalR client"""
        try:
            # Parse connection string
            config = dict(item.split('=') for item in self.connection_string.split(';'))
            self.hub_url = f"{config['Endpoint']}/api/v1/hubs/security"
            
            # Get access token
            self.access_token = await self._get_access_token()
            
            # Create session
            self.session = aiohttp.ClientSession()
            
            logger.info("SignalR client initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize SignalR client: {str(e)}")
            raise

    async def _get_access_token(self) -> str:
        """Get SignalR access token"""
        try:
            endpoint = f"{self.hub_url}/negotiate"
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['accessToken']
                    raise Exception(f"Failed to get access token: {response.status}")
        except Exception as e:
            logger.error(f"Failed to get access token: {str(e)}")
            raise

    async def send_message(self, event: str, data: Dict[str, Any]):
        """Send message to SignalR hub"""
        try:
            if not self.session:
                await self.initialize()
                
            message = {
                'event': event,
                'data': {
                    **data,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            async with self.session.post(
                f"{self.hub_url}/messages",
                json=message,
                headers=headers
            ) as response:
                if response.status != 200:
                    logger.error(f"Failed to send message: {response.status}")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            return False

    async def close(self):
        """Close SignalR client"""
        if self.session:
            await self.session.close()