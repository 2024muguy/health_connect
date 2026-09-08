"""
HealthConnect AI - Notification Service
========================================
Business logic for notification management.

Features:
- Email notifications
- SMS notifications
- Push notifications
- Appointment reminders
- Notification templates
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

from app.mcp.servers.email_server import EmailMCPServer
from app.mcp.servers.notification_server import NotificationMCPServer

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class NotificationService:
    """
    Notification Service.
    Manages all notification operations.
    """
    
    def __init__(self):
        self.email_server = EmailMCPServer()
        self.notification_server = NotificationMCPServer()
        self._notification_log: List[Dict[str, Any]] = []
        logger.info("NotificationService initialized")
    
    async def send_appointment_reminder(
        self,
        patient_email: str,
        patient_name: str,
        appointment_datetime: str,
        clinic_location: str,
    ) -> Dict[str, Any]:
        """
        Send appointment reminder email.
        
        Args:
            patient_email: Patient email
            patient_name: Patient name
            appointment_datetime: Appointment datetime
            clinic_location: Clinic location
            
        Returns:
            Dict: Result
        """
        result = await self.email_server.send_appointment_reminder(
            to=patient_email,
            patient_name=patient_name,
            appointment_datetime=appointment_datetime,
            clinic_location=clinic_location,
        )
        
        self._log_notification("email_reminder", patient_email, result)
        return result
    
    async def send_appointment_confirmation(
        self,
        patient_email: str,
        patient_name: str,
        appointment_datetime: str,
        clinic_location: str,
    ) -> Dict[str, Any]:
        """
        Send appointment confirmation email.
        
        Args:
            patient_email: Patient email
            patient_name: Patient name
            appointment_datetime: Appointment datetime
            clinic_location: Clinic location
            
        Returns:
            Dict: Result
        """
        result = await self.email_server.send_template_email(
            to=patient_email,
            template_name="appointment_confirmation",
            template_vars={
                "patient_name": patient_name,
                "appointment_datetime": appointment_datetime,
                "clinic_location": clinic_location,
            },
        )
        
        self._log_notification("email_confirmation", patient_email, result)
        return result
    
    async def send_sms_notification(
        self,
        phone_number: str,
        message: str,
    ) -> Dict[str, Any]:
        """
        Send SMS notification.
        
        Args:
            phone_number: Recipient phone
            message: SMS message
            
        Returns:
            Dict: Result
        """
        result = await self.notification_server.send_sms(phone_number, message)
        self._log_notification("sms", phone_number, result)
        return result
    
    async def send_push_notification(
        self,
        device_token: str,
        title: str,
        body: str,
    ) -> Dict[str, Any]:
        """
        Send push notification.
        
        Args:
            device_token: Device token
            title: Notification title
            body: Notification body
            
        Returns:
            Dict: Result
        """
        result = await self.notification_server.send_push(device_token, title, body)
        self._log_notification("push", device_token[:8] + "...", result)
        return result
    
    async def schedule_reminder(
        self,
        patient_id: str,
        appointment_id: str,
        reminder_time: str,
        method: str = "both",
    ) -> Dict[str, Any]:
        """
        Schedule appointment reminder.
        
        Args:
            patient_id: Patient ID
            appointment_id: Appointment ID
            reminder_time: Reminder time
            method: Notification method
            
        Returns:
            Dict: Result
        """
        result = await self.notification_server.schedule_reminder(
            patient_id=patient_id,
            appointment_id=appointment_id,
            reminder_time=reminder_time,
            method=method,
        )
        
        self._log_notification("scheduled_reminder", patient_id, result)
        return result
    
    def _log_notification(
        self,
        notification_type: str,
        recipient: str,
        result: Dict[str, Any],
    ) -> None:
        """Log notification"""
        self._notification_log.append({
            "type": notification_type,
            "recipient": recipient,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        
        # Trim log
        if len(self._notification_log) > 1000:
            self._notification_log = self._notification_log[-1000:]
    
    async def get_notification_log(
        self,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get notification log"""
        return self._notification_log[-limit:]