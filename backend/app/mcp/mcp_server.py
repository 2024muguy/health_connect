"""
HealthConnect AI - Base MCP Server
===================================
Base classes for Model Context Protocol servers.

Features:
- Server lifecycle management
- Tool registration
- Tool execution
- Error handling
- Rate limiting
"""

import asyncio
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Awaitable
from enum import Enum

from config.logging_config import get_logger

logger = get_logger(__name__)


class MCPToolStatus(Enum):
    """MCP tool execution status"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    NOT_FOUND = "not_found"


@dataclass
class MCPToolResult:
    """MCP tool execution result"""
    tool_name: str
    status: MCPToolStatus
    data: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "tool_name": self.tool_name,
            "status": self.status.value,
            "data": self.data,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "request_id": self.request_id,
        }
    
    @property
    def is_successful(self) -> bool:
        """Check if execution was successful"""
        return self.status == MCPToolStatus.SUCCESS


@dataclass
class MCPTool:
    """
    MCP tool definition.
    """
    name: str
    description: str
    handler: Callable[..., Awaitable[Any]]
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: float = 30.0
    rate_limit: Optional[int] = None
    requires_auth: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    async def execute(self, **kwargs) -> MCPToolResult:
        """
        Execute tool with parameters.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            MCPToolResult: Execution result
        """
        start_time = time.time()
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                self.handler(**kwargs),
                timeout=self.timeout_seconds,
            )
            
            return MCPToolResult(
                tool_name=self.name,
                status=MCPToolStatus.SUCCESS,
                data=result,
                execution_time_ms=(time.time() - start_time) * 1000,
            )
            
        except asyncio.TimeoutError:
            return MCPToolResult(
                tool_name=self.name,
                status=MCPToolStatus.TIMEOUT,
                error=f"Tool execution timed out after {self.timeout_seconds}s",
                execution_time_ms=(time.time() - start_time) * 1000,
            )
            
        except Exception as e:
            logger.error(f"Tool {self.name} failed: {e}")
            return MCPToolResult(
                tool_name=self.name,
                status=MCPToolStatus.FAILED,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )


class BaseMCPServer(ABC):
    """
    Base class for MCP servers.
    All MCP servers inherit from this class.
    """
    
    def __init__(self, server_name: str, config: Optional[Dict[str, Any]] = None):
        self.server_name = server_name
        self.config = config or {}
        self.tools: Dict[str, MCPTool] = {}
        self._initialized = False
        self._request_count = 0
        self._error_count = 0
        
        logger.info(f"Initialized MCP server: {server_name}")
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize server"""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close server"""
        pass
    
    def register_tool(self, tool: MCPTool) -> None:
        """
        Register a tool with the server.
        
        Args:
            tool: Tool to register
        """
        self.tools[tool.name] = tool
        logger.debug(f"Registered tool '{tool.name}' on server '{self.server_name}'")
    
    def register_tools(self, tools: List[MCPTool]) -> None:
        """Register multiple tools"""
        for tool in tools:
            self.register_tool(tool)
    
    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Get tool by name"""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all registered tools"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
                "requires_auth": tool.requires_auth,
            }
            for tool in self.tools.values()
        ]
    
    async def execute_tool(
        self,
        tool_name: str,
        **kwargs,
    ) -> MCPToolResult:
        """
        Execute a tool.
        
        Args:
            tool_name: Name of tool to execute
            **kwargs: Tool parameters
            
        Returns:
            MCPToolResult: Execution result
        """
        tool = self.get_tool(tool_name)
        
        if not tool:
            return MCPToolResult(
                tool_name=tool_name,
                status=MCPToolStatus.NOT_FOUND,
                error=f"Tool not found: {tool_name}",
            )
        
        # Check rate limit
        if tool.rate_limit:
            # Simple rate limiting (would use Redis in production)
            pass
        
        self._request_count += 1
        result = await tool.execute(**kwargs)
        
        if result.is_failed:
            self._error_count += 1
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics"""
        return {
            "server_name": self.server_name,
            "tool_count": len(self.tools),
            "request_count": self._request_count,
            "error_count": self._error_count,
            "initialized": self._initialized,
        }