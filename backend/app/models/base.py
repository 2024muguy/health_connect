"""
HealthConnect AI - Base Model
===============================
Abstract base model with common fields and utilities.

Features:
- UUID primary keys
- Timestamp tracking (created_at, updated_at)
- Soft delete support
- Serialization methods
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import Column, DateTime, String, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr, declarative_base

# Create declarative base
Base = declarative_base()


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Record creation timestamp",
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Record last update timestamp",
    )


class SoftDeleteMixin:
    """Mixin for soft delete functionality"""
    
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Soft delete flag",
    )
    
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Soft delete timestamp",
    )
    
    def soft_delete(self) -> None:
        """Mark record as deleted"""
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
    
    def restore(self) -> None:
        """Restore soft-deleted record"""
        self.is_deleted = False
        self.deleted_at = None


class BaseModel(Base, TimestampMixin):
    """
    Abstract base model for all database models.
    
    Provides:
    - UUID primary key
    - Timestamp tracking
    - Serialization
    """
    
    __abstract__ = True
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        comment="Primary key UUID",
    )
    
    def to_dict(self, exclude: Optional[list] = None) -> Dict[str, Any]:
        """
        Convert model to dictionary.
        
        Args:
            exclude: List of fields to exclude
            
        Returns:
            Dict: Model as dictionary
        """
        exclude = exclude or []
        result = {}
        
        for column in self.__table__.columns:
            if column.name in exclude:
                continue
            
            value = getattr(self, column.name)
            
            # Convert UUID to string
            if isinstance(value, uuid.UUID):
                value = str(value)
            
            # Convert datetime to ISO format
            elif isinstance(value, datetime):
                value = value.isoformat()
            
            result[column.name] = value
        
        return result
    
    def __repr__(self) -> str:
        """String representation"""
        return f"<{self.__class__.__name__}(id={self.id})>"