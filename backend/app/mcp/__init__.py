"""
HealthConnect AI - MCP Package
===============================
Model Context Protocol (MCP) servers and tools.

Features:
- MCP server management
- Tool registry
- Tool routing
- Database, Calendar, Email, Knowledge Base, Analytics, Notification servers
"""

from app.mcp.mcp_server import BaseMCPServer, MCPTool, MCPToolResult
from app.mcp.mcp_registry import MCPRegistry
from app.mcp.mcp_router import MCPRouter

__all__ = [
    "BaseMCPServer",
    "MCPTool",
    "MCPToolResult",
    "MCPRegistry",
    "MCPRouter",
]