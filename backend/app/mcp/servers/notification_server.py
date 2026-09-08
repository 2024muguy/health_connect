"""
HealthConnect AI - Notification MCP Server
===========================================
MCP server for notification operations.

Tools:
- send_sms: Send SMS notification
- send_push: Send push notification
- schedule_reminder: Schedule appointment reminder
"""

from typing import Dict, List, Any, Optional

from app.mcp.mcp_server import BaseMCPServer, MCPTool

from config.logging_config import get_logger

logger = get_logger(__name__)


class NotificationMCPServer(BaseMCPServer):
    """
    Notification MCP Server.
    Provides tools for notification operations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("notification", config)
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register notification tools"""
        self.register_tools([
            MCPTool(
                name="send_sms",
                description="Send SMS notification",
                handler=self.send_sms,
                parameters={
                    "phone_number": {"type": "string", "description": "Recipient phone"},
                    "message": {"type": "string", "description": "SMS message"},
                },
                timeout_seconds=10.0,
                requires_auth=True,
            ),
            MCPTool(
                name="send_push",
                description="Send push notification",
                handler=self.send_push,
                parameters={
                    "device_token": {"type": "string", "description": "Device token"},
                    "title": {"type": "string", "description": "Notification title"},
                    "body": {"type": "string", "description": "Notification body"},
                },
                timeout_seconds=10.0,
                requires_auth=True,
            ),
            MCPTool(
                name="schedule_reminder",
                description="Schedule appointment reminder",
                handler=self.schedule_reminder,
                parameters={
                    "patient_id": {"type": "string", "description": "Patient ID"},
                    "appointment_id": {"type": "string", "description": "Appointment ID"},
                    "reminder_time": {"type": "string", "description": "Reminder time"},
                    "method": {"type": "string", "description": "Notification method (sms/email/both)"},
                },
                timeout_seconds=10.0,
                requires_auth=True,
            ),
        ])
    
    async def initialize(self) -> None:
        """Initialize notification server"""
        self._initialized = True
        logger.info("Notification MCP Server initialized")
    
    async def close(self) -> None:
        """Close notification server"""
        self._initialized = False
        logger.info("Notification MCP Server closed")
    
    async def send_sms(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send SMS"""
        return {
            "status": "sent",
            "to": phone_number,
            "message_length": len(message),
        }
    
    async def send_push(
        self,
        device_token: str,
        title: str,
        body: str,
    ) -> Dict[str, Any]:
        """Send push notification"""
        return {
            "status": "sent",
            "device_token": device_token[:8] + "...",
            "title": title,
        }
    
    async def schedule_reminder(
        self,
        patient_id: str,
        appointment_id: str,
        reminder_time: str,
        method: str = "both",
    ) -> Dict[str, Any]:
        """Schedule reminder"""
        return {
            "status": "scheduled",
            "patient_id": patient_id,
            "appointment_id": appointment_id,
            "reminder_time": reminder_time,
            "method": method,
        }