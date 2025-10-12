"""Base connector class for external services"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseConnector(ABC):
    """Abstract base class for all connectors"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the connector
        
        Args:
            config: Configuration dictionary for the connector
        """
        self.config = config
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to the service
        
        Returns:
            True if connection successful
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Close connection to the service
        
        Returns:
            True if disconnection successful
        """
        pass
