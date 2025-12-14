"""
Warehouse service for managing warehouses.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.models.warehouse import Warehouse
from src.database.tenant_context import get_current_tenant_id


class WarehouseService:
    """Service for warehouse operations."""
    
    @staticmethod
    def get_all(db: Session, tenant_id: UUID, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[Warehouse]:
        """Get all warehouses for a tenant."""
        query = db.query(Warehouse).filter(Warehouse.tenant_id == tenant_id)
        
        if active_only:
            query = query.filter(Warehouse.is_active == True)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, warehouse_id: UUID, tenant_id: UUID) -> Optional[Warehouse]:
        """Get a warehouse by ID."""
        return db.query(Warehouse).filter(
            and_(
                Warehouse.id == warehouse_id,
                Warehouse.tenant_id == tenant_id
            )
        ).first()
    
    @staticmethod
    def create(db: Session, warehouse_data: dict, tenant_id: UUID) -> Warehouse:
        """Create a new warehouse."""
        warehouse = Warehouse(
            tenant_id=tenant_id,
            **warehouse_data
        )
        db.add(warehouse)
        db.commit()
        db.refresh(warehouse)
        return warehouse
    
    @staticmethod
    def update(db: Session, warehouse_id: UUID, warehouse_data: dict, tenant_id: UUID) -> Optional[Warehouse]:
        """Update a warehouse."""
        warehouse = WarehouseService.get_by_id(db, warehouse_id, tenant_id)
        if not warehouse:
            return None
        
        for key, value in warehouse_data.items():
            setattr(warehouse, key, value)
        
        db.commit()
        db.refresh(warehouse)
        return warehouse
    
    @staticmethod
    def delete(db: Session, warehouse_id: UUID, tenant_id: UUID) -> bool:
        """Delete a warehouse."""
        warehouse = WarehouseService.get_by_id(db, warehouse_id, tenant_id)
        if not warehouse:
            return False
        
        db.delete(warehouse)
        db.commit()
        return True
