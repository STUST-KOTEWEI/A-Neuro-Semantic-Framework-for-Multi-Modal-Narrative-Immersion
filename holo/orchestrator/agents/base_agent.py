"""Base agent class for all agents in the orchestrator"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, agent_id: str, connectors: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent
        
        Args:
            agent_id: Unique identifier for the agent
            connectors: Dictionary of connector instances for external services
        """
        self.agent_id = agent_id
        self.connectors = connectors or {}
    
    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input data and return results
        
        Args:
            data: Input data dictionary
            
        Returns:
            Dictionary containing processing results
        """
        pass
    
    def get_connector(self, name: str) -> Any:
        """Get a connector by name"""
        return self.connectors.get(name)
