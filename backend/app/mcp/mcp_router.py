"""
HealthConnect AI - MCP Router
==============================
Routes tool requests to appropriate MCP servers.

Features:
- Tool routing
- Load balancing
- Fallback handling
- Request tracing
"""

import time
import uuid
from typing import Dict, List, Any, Optional

from app.mcp.mcp_server import MCPToolResult, MCPToolStatus
from app.mcp.mcp_registry import MCPRegistry

from config.logging_config import get_logger

logger = get_logger(__name__)


class MCPRouter:
    """
    MCP Router.
    Routes tool requests to appropriate servers.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.registry = MCPRegistry()
        self._route_cache: Dict[str, str] = {}
        self._request_count = 0
        logger.info("MCPRouter initialized")
    
    async def route_tool(
        self,
        tool_name: str,
        **kwargs,
    ) -> MCPToolResult:
        """
        Route tool request to appropriate server.
        
        Args:
            tool_name: Tool name
            **kwargs: Tool parameters
            
        Returns:
            MCPToolResult: Execution result
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())
        self._request_count += 1
        
        # Check cache for route
        server_name = self._route_cache.get(tool_name)
        
        if not server_name:
            server_name = self.registry.get_tool_server(tool_name)
            
            if server_name:
                self._route_cache[tool_name] = server_name
        
        if not server_name:
            logger.warning(f"Route not found for tool: {tool_name}")
            return MCPToolResult(
                tool_name=tool_name,
                status=MCPToolStatus.NOT_FOUND,
                error=f"No route found for tool: {tool_name}",
                request_id=request_id,
            )
        
        # Execute tool
        result = await self.registry.execute_tool(tool_name, **kwargs)
        
        # Add routing metadata
        result.request_id = request_id
        
        logger.debug(
            f"Routed {tool_name} to {server_name} "
            f"({result.execution_time_ms:.1f}ms)"
        )
        
        return result
    
    async def route_batch(
        self,
        tool_requests: List[Dict[str, Any]],
    ) -> List[MCPToolResult]:
        """
        Route multiple tool requests.
        
        Args:
            tool_requests: List of {tool_name, params}
            
        Returns:
            List[MCPToolResult]: Results
        """
        results = []
        
        for request in tool_requests:
            tool_name = request.get("tool_name", "")
            params = request.get("params", {})
            
            result = await self.route_tool(tool_name, **params)
            results.append(result)
        
        return results
    
    def clear_cache(self) -> None:
        """Clear route cache"""
        self._route_cache = {}
        logger.info("MCP router cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get router statistics"""
        return {
            "request_count": self._request_count,
            "cache_size": len(self._route_cache),
            "registry_stats": self.registry.get_stats(),
        }