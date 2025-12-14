"""
Base model with common fields for all entities.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr

from src.database.session import Base


class BaseModel(Base):
    """Base model with common fields: id, tenant_id, timestamps."""
    
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    @declared_attr
    def __tablename__(cls):
        """Generate table name from class name."""
        return cls.__name__.lower() + "s"  # Pluralize

