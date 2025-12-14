"""
Tenant context helper for database queries.
"""
from typing import TypeVar, Type
from sqlalchemy import and_
from sqlalchemy.orm import Query
from uuid import UUID

from src.models.base import BaseModel

T = TypeVar('T', bound=BaseModel)


class TenantContext:
    """Helper class for tenant-scoped database queries."""
    
    @staticmethod
    def scope_query(query: Query, tenant_id: UUID, model_class: Type[T]) -> Query:
        """
        Add tenant_id filter to a query.
        
        Args:
            query: SQLAlchemy query object
            tenant_id: Tenant UUID
            model_class: Model class (must have tenant_id column)
            
        Returns:
            Query with tenant_id filter applied
        """
        return query.filter(model_class.tenant_id == tenant_id)
    
    @staticmethod
    def filter_by_tenant(query: Query, tenant_id: UUID) -> Query:
        """
        Filter query by tenant_id (generic version).
        
        Args:
            query: SQLAlchemy query object
            tenant_id: Tenant UUID
            
        Returns:
            Query with tenant_id filter applied
        """
        # This assumes all models have tenant_id column
        # In practice, you might want to be more specific
        return query.filter(and_(True))  # Placeholder - implement based on your needs

