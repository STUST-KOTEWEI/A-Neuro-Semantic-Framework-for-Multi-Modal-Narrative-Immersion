"""HTTP connector for REST API calls"""
from typing import Dict, Any, Optional
import httpx
from .base_connector import BaseConnector


class HTTPConnector(BaseConnector):
    """Connector for HTTP/REST API services"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize HTTP connector
        
        Args:
            config: Configuration dictionary with 'url' and optional headers
        """
        super().__init__(config)
        self.url = config.get('url', '')
        self.headers = config.get('headers', {})
        self.client: Optional[httpx.AsyncClient] = None
    
    async def connect(self) -> bool:
        """Establish HTTP client"""
        self.client = httpx.AsyncClient(headers=self.headers, timeout=30.0)
        return True
    
    async def disconnect(self) -> bool:
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()
            self.client = None
        return True
    
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a POST request
        
        Args:
            endpoint: API endpoint path
            data: Request body data
            
        Returns:
            Response data as dictionary
        """
        if not self.client:
            await self.connect()
        
        url = f"{self.url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            response = await self.client.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {'error': str(e)}
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GET request
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            Response data as dictionary
        """
        if not self.client:
            await self.connect()
        
        url = f"{self.url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {'error': str(e)}
