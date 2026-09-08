"""
HealthConnect AI - Email MCP Server
====================================
MCP server for email operations.

Tools:
- send_email: Send email
- send_template_email: Send templated email
- send_appointment_reminder: Send appointment reminder
"""

from typing import Dict, List, Any, Optional

from app.mcp.mcp_server import BaseMCPServer, MCPTool

from config.logging_config import get_logger

logger = get_logger(__name__)


class EmailMCPServer(BaseMCPServer):
    """
    Email MCP Server.
    Provides tools for email operations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("email", config)
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register email tools"""
        self.register_tools([
            MCPTool(
                name="send_email",
                description="Send an email",
                handler=self.send_email,
                parameters={
                    "to": {"type": "string", "description": "Recipient email"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body"},
                },
                timeout_seconds=15.0,
                requires_auth=True,
            ),
            MCPTool(
                name="send_template_email",
                description="Send email using template",
                handler=self.send_template_email,
                parameters={
                    "to": {"type": "string", "description": "Recipient email"},
                    "template_name": {"type": "string", "description": "Template name"},
                    "template_vars": {"type": "object", "description": "Template variables"},
                },
                timeout_seconds=15.0,
                requires_auth=True,
            ),
            MCPTool(
                name="send_appointment_reminder",
                description="Send appointment reminder email",
                handler=self.send_appointment_reminder,
                parameters={
                    "to": {"type": "string", "description": "Patient email"},
                    "patient_name": {"type": "string", "description": "Patient name"},
                    "appointment_datetime": {"type": "string", "description": "Appointment datetime"},
                    "clinic_location": {"type": "string", "description": "Clinic location"},
                },
                timeout_seconds=15.0,
                requires_auth=True,
            ),
        ])
    
    async def initialize(self) -> None:
        """Initialize email server"""
        self._initialized = True
        logger.info("Email MCP Server initialized")
    
    async def close(self) -> None:
        """Close email server"""
        self._initialized = False
        logger.info("Email MCP Server closed")
    
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
    ) -> Dict[str, Any]:
        """Send email"""
        return {
            "status": "sent",
            "to": to,
            "subject": subject,
            "sent_at": None,
        }
    
    async def send_template_email(
        self,
        to: str,
        template_name: str,
        template_vars: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Send templated email"""
        templates = {
            "appointment_confirmation": "Your appointment is confirmed for {appointment_datetime} at {clinic_location}.",
            "appointment_reminder": "Reminder: You have an appointment on {appointment_datetime} at {clinic_location}.",
            "appointment_cancellation": "Your appointment on {appointment_datetime} has been cancelled.",
            "appointment_reschedule": "Your appointment has been rescheduled to {appointment_datetime}.",
        }
        
        template_body = templates.get(template_name, "")
        body = template_body.format(**(template_vars or {}))
        
        return {
            "status": "sent",
            "to": to,
            "template": template_name,
            "body": body,
        }
    
    async def send_appointment_reminder(
        self,
        to: str,
        patient_name: str,
        appointment_datetime: str,
        clinic_location: str,
    ) -> Dict[str, Any]:
        """Send appointment reminder"""
        subject = "Appointment Reminder - HealthConnect Clinic"
        body = (
            f"Dear {patient_name},\n\n"
            f"This is a reminder for your upcoming appointment on {appointment_datetime} "
            f"at {clinic_location}.\n\n"
            f"If you need to reschedule or cancel, please contact us at least 24 hours in advance.\n\n"
            f"Thank you,\nHealthConnect Clinic"
        )
        
        return await self.send_email(to, subject, body)