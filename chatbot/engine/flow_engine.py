"""
Flow Engine
Manages chatbot conversation flows loaded from JSON configuration.
No hardcoded conversation text - all content comes from chatbot_flows.json.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from ..core.logger import setup_logger

logger = setup_logger(__name__)


class FlowEngine:
    """
    Manages rule-based conversation flows for EV charging support.
    
    This engine loads flow definitions from JSON and handles node-based navigation.
    All conversation text, options, and steps are externalized in the flows file.
    """
    
    def __init__(self, flows_path: Optional[str] = None):
        """
        Initialize the flow engine.
        
        Args:
            flows_path: Path to the flows JSON file
        """
        self.flows: Dict[str, Any] = {}
        self.flows_path = flows_path or self._get_default_flows_path()
        
    def _get_default_flows_path(self) -> str:
        """Get default path to flows JSON file."""
        base_path = Path(__file__).parent.parent
        return str(base_path / "flows" / "chatbot_flows.json")
    
    async def load_flows(self) -> None:
        """
        Load conversation flows from JSON file.
        Called during application startup.
        """
        try:
            with open(self.flows_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.flows = data.get("flows", {})
            
            logger.info(
                f"Loaded {len(self.flows)} conversation flows from {self.flows_path}"
            )
        except FileNotFoundError:
            logger.error(f"Flows file not found: {self.flows_path}")
            # Initialize with minimal default flow
            self.flows = {
                "start": {
                    "text": "Welcome to EV Charging Technical Support. How can I help you?",
                    "options": ["Report Error", "Get Help"],
                    "steps": None,
                    "action": None
                }
            }
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in flows file: {e}")
            self.flows = {}
    
    async def get_node(self, node_id: str) -> Dict[str, Any]:
        """
        Retrieve a flow node by ID.
        
        Args:
            node_id: Node identifier
            
        Returns:
            Node data or fallback to 'start' node
        """
        # Try to get requested node
        node = self.flows.get(node_id)
        
        if node:
            logger.debug(f"Retrieved flow node: {node_id}")
            return node
        
        # Graceful fallback to start node
        logger.warning(f"Node '{node_id}' not found, falling back to 'start'")
        return self.flows.get("start", {
            "text": "How can I assist you with EV charging today?",
            "options": None,
            "steps": None,
            "action": None
        })
    
    async def get_start_node(self) -> Dict[str, Any]:
        """
        Get the initial conversation node.
        
        Returns:
            Start node data
        """
        return await self.get_node("start")
    
    def is_flow_loaded(self) -> bool:
        """
        Check if flows are loaded.
        
        Returns:
            True if flows are loaded, False otherwise
        """
        return len(self.flows) > 0
