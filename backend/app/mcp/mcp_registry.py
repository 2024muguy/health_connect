"""
HealthConnect AI - MCP Registry
================================
Registry for all MCP servers.

Features:
- Server registration
- Server discovery
- Tool lookup
- Server lifecycle management
"""

from typing import Dict, List, Any, Optional

from app.mcp.mcp_server import BaseMCPServer, MCPTool, MCPToolResult

from config.logging_config import get_logger

logger = get_logger(__name__)


class MCPRegistry:
    """
    Registry for MCP servers.
    Manages server lifecycle and tool discovery.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.servers: Dict[str, BaseMCPServer] = {}
        self._tool_map: Dict[str, tuple] = {}  # tool_name -> (server_name, tool)
        logger.info("MCPRegistry initialized")
    
    async def initialize(self) -> None:
        """Initialize all registered servers"""
        # Import and register servers
        from app.mcp.servers.database_server import DatabaseMCPServer
        from app.mcp.servers.calendar_server import CalendarMCPServer
        from app.mcp.servers.email_server import EmailMCPServer
        from app.mcp.servers.knowledge_base_server import KnowledgeBaseMCPServer
        from app.mcp.servers.analytics_server import AnalyticsMCPServer
        from app.mcp.servers.notification_server import NotificationMCPServer
        
        servers = [
            DatabaseMCPServer(),
            CalendarMCPServer(),
            EmailMCPServer(),
            KnowledgeBaseMCPServer(),
            AnalyticsMCPServer(),
            NotificationMCPServer(),
        ]
        
        for server in servers:
            self.register_server(server)
            await server.initialize()
        
        logger.info(f"Initialized {len(self.servers)} MCP servers")
    
    async def close(self) -> None:
        """Close all servers"""
        for server in self.servers.values():
            await server.close()
        
        self.servers = {}
        self._tool_map = {}
        logger.info("MCP servers closed")
    
    def register_server(self, server: BaseMCPServer) -> None:
        """
        Register a server.
        
        Args:
            server: Server to register
        """
        self.servers[server.server_name] = server
        
        # Index tools
        for tool_name, tool in server.tools.items():
            self._tool_map[tool_name] = (server.server_name, tool)
        
        logger.info(f"Registered MCP server: {server.server_name}")
    
    def unregister_server(self, server_name: str) -> None:
        """Unregister a server"""
        server = self.servers.pop(server_name, None)
        
        if server:
            # Remove tools from index
            for tool_name in server.tools:
                self._tool_map.pop(tool_name, None)
            
            logger.info(f"Unregistered MCP server: {server_name}")
    
    def get_server(self, server_name: str) -> Optional[BaseMCPServer]:
        """Get server by name"""
        return self.servers.get(server_name)
    
    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Get tool by name"""
        entry = self._tool_map.get(tool_name)
        if entry:
            return entry[1]
        return None
    
    def get_tool_server(self, tool_name: str) -> Optional[str]:
        """Get server name for a tool"""
        entry = self._tool_map.get(tool_name)
        if entry:
            return entry[0]
        return None
    
    def list_servers(self) -> List[str]:
        """List all server names"""
        return list(self.servers.keys())
    
    def list_all_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """List all tools grouped by server"""
        result = {}
        
        for server_name, server in self.servers.items():
            result[server_name] = server.list_tools()
        
        return result
    
    async def execute_tool(
        self,
        tool_name: str,
        **kwargs,
    ) -> MCPToolResult:
        """
        Execute a tool by name.
        
        Args:
            tool_name: Tool name
            **kwargs: Tool parameters
            
        Returns:
            MCPToolResult: Execution result
        """
        server_name = self.get_tool_server(tool_name)
        
        if not server_name:
            return MCPToolResult(
                tool_name=tool_name,
                status=MCPToolResult.__annotations__.get("status", "not_found"),
                error=f"Tool not found: {tool_name}",
            )
        
        server = self.get_server(server_name)
        return await server.execute_tool(tool_name, **kwargs)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            "server_count": len(self.servers),
            "tool_count": len(self._tool_map),
            "servers": {
                name: server.get_stats()
                for name, server in self.servers.items()
            },
        }