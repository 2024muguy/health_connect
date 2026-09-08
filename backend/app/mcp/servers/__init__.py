"""
HealthConnect AI - MCP Servers Package
=======================================
MCP server implementations.

Servers:
- Database Server
- Calendar Server
- Email Server
- Knowledge Base Server
- Analytics Server
- Notification Server
"""

from app.mcp.servers.database_server import DatabaseMCPServer
from app.mcp.servers.calendar_server import CalendarMCPServer
from app.mcp.servers.email_server import EmailMCPServer
from app.mcp.servers.knowledge_base_server import KnowledgeBaseMCPServer
from app.mcp.servers.analytics_server import AnalyticsMCPServer
from app.mcp.servers.notification_server import NotificationMCPServer

__all__ = [
    "DatabaseMCPServer",
    "CalendarMCPServer",
    "EmailMCPServer",
    "KnowledgeBaseMCPServer",
    "AnalyticsMCPServer",
    "NotificationMCPServer",
]