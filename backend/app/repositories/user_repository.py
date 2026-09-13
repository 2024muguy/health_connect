"""
HealthConnect AI - User Repository
===================================
Database access layer for User model.
Works with both SQLite and Postgres via SQLAlchemy.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from config.logging_config import get_logger

logger = get_logger(__name__)


class UserRepository:
    """User data access."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter(User.email == email.lower().strip()).first()

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.session.query(User).filter(User.id == user_id).first()

    def create(
        self,
        email: str,
        hashed_password: str,
        full_name: str,
        phone: Optional[str] = None,
        roles: str = "user",
    ) -> User:
        user = User(
            email=email.lower().strip(),
            hashed_password=hashed_password,
            full_name=full_name.strip(),
            phone=phone,
            roles=roles,
            is_active=True,
            is_verified=False,
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        logger.info(f"User created: {user.email} ({user.id})")
        return user

    def update_last_login(self, user: User) -> None:
        user.last_login_at = datetime.now(timezone.utc)
        self.session.commit()

    def email_exists(self, email: str) -> bool:
        return self.get_by_email(email) is not None
