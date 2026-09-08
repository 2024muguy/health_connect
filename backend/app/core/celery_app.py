"""
HealthConnect AI - Celery Configuration
========================================
Celery task queue configuration for background processing.

Tasks:
- Email sending
- SMS notifications
- Document ingestion
- Model training
- Analytics processing
- Report generation
"""

from celery import Celery
from celery.schedules import crontab

from config.settings import get_settings

settings = get_settings()

# Create Celery application
celery_app = Celery(
    "healthconnect",
    broker=settings.redis.URL,
    backend=settings.redis.URL,
    include=[
        "app.services.notification_service",
        "app.rag.document_ingestion",
        "app.services.analytics_service",
    ],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=3600,
    broker_connection_retry_on_startup=True,
)

# Scheduled tasks
celery_app.conf.beat_schedule = {
    "send-appointment-reminders": {
        "task": "send_appointment_reminders",
        "schedule": crontab(hour="*/2"),  # Every 2 hours
    },
    "process-pending-escalations": {
        "task": "process_pending_escalations",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
    },
    "generate-daily-reports": {
        "task": "generate_daily_reports",
        "schedule": crontab(hour=0, minute=0),  # Daily at midnight
    },
    "cleanup-expired-sessions": {
        "task": "cleanup_expired_sessions",
        "schedule": crontab(hour="*/6"),  # Every 6 hours
    },
    "refresh-knowledge-base": {
        "task": "refresh_knowledge_base",
        "schedule": crontab(hour=1, minute=0),  # Daily at 1 AM
    },
}


@celery_app.task(name="send_appointment_reminders")
def send_appointment_reminders():
    """Send appointment reminders to patients"""
    from app.services.notification_service import NotificationService
    service = NotificationService()
    return service.send_appointment_reminders()


@celery_app.task(name="process_pending_escalations")
def process_pending_escalations():
    """Process pending escalation tickets"""
    from app.services.escalation_service import EscalationService
    service = EscalationService()
    return service.process_pending_escalations()


@celery_app.task(name="generate_daily_reports")
def generate_daily_reports():
    """Generate daily analytics reports"""
    from app.services.analytics_service import AnalyticsService
    service = AnalyticsService()
    return service.generate_daily_reports()


@celery_app.task(name="cleanup_expired_sessions")
def cleanup_expired_sessions():
    """Clean up expired conversation sessions"""
    from app.services.chat_service import ChatService
    service = ChatService()
    return service.cleanup_expired_sessions()


@celery_app.task(name="refresh_knowledge_base")
def refresh_knowledge_base():
    """Refresh knowledge base indexing"""
    from app.rag.document_ingestion import DocumentIngestionPipeline
    pipeline = DocumentIngestionPipeline()
    return pipeline.refresh_index()