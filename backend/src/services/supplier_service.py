"""
Supplier service for managing suppliers.
"""
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from src.models.supplier import Supplier
from src.models.purchase_order import PurchaseOrder, PurchaseOrderStatus


class SupplierService:
    """Service for supplier operations."""
    
    @staticmethod
    def get_all(db: Session, tenant_id: UUID, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[Supplier]:
        """Get all suppliers for a tenant."""
        query = db.query(Supplier).filter(Supplier.tenant_id == tenant_id)
        
        if active_only:
            query = query.filter(Supplier.is_active == True)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, supplier_id: UUID, tenant_id: UUID) -> Optional[Supplier]:
        """Get a supplier by ID."""
        return db.query(Supplier).filter(
            and_(
                Supplier.id == supplier_id,
                Supplier.tenant_id == tenant_id
            )
        ).first()
    
    @staticmethod
    def create(db: Session, supplier_data: dict, tenant_id: UUID) -> Supplier:
        """Create a new supplier."""
        supplier = Supplier(
            tenant_id=tenant_id,
            **supplier_data
        )
        db.add(supplier)
        db.commit()
        db.refresh(supplier)
        return supplier
    
    @staticmethod
    def update(db: Session, supplier_id: UUID, supplier_data: dict, tenant_id: UUID) -> Optional[Supplier]:
        """Update a supplier."""
        supplier = SupplierService.get_by_id(db, supplier_id, tenant_id)
        if not supplier:
            return None
        
        for key, value in supplier_data.items():
            setattr(supplier, key, value)
        
        db.commit()
        db.refresh(supplier)
        return supplier
    
    @staticmethod
    def calculate_performance_score(db: Session, supplier_id: UUID, tenant_id: UUID) -> Optional[Decimal]:
        """
        Calculate supplier performance score based on purchase order fulfillment.
        
        Returns:
            Performance score (0-100) or None if no orders
        """
        # Get completed purchase orders
        completed_pos = db.query(PurchaseOrder).filter(
            and_(
                PurchaseOrder.tenant_id == tenant_id,
                PurchaseOrder.supplier_id == supplier_id,
                PurchaseOrder.status.in_([PurchaseOrderStatus.RECEIVED.value, PurchaseOrderStatus.PARTIALLY_RECEIVED.value])
            )
        ).all()
        
        if not completed_pos:
            return None
        
        # Calculate metrics
        total_orders = len(completed_pos)
        on_time_deliveries = sum(
            1 for po in completed_pos
            if po.actual_delivery_date and po.expected_delivery_date
            and po.actual_delivery_date <= po.expected_delivery_date
        )
        
        on_time_rate = (on_time_deliveries / total_orders) * 100 if total_orders > 0 else 0
        
        # Simple performance score (can be enhanced)
        performance_score = min(100, on_time_rate * 1.2)  # Bonus for on-time delivery
        
        return Decimal(str(round(performance_score, 2)))
    
    @staticmethod
    def update_performance_score(db: Session, supplier_id: UUID, tenant_id: UUID) -> Optional[Supplier]:
        """Update supplier performance score."""
        supplier = SupplierService.get_by_id(db, supplier_id, tenant_id)
        if not supplier:
            return None
        
        score = SupplierService.calculate_performance_score(db, supplier_id, tenant_id)
        if score is not None:
            supplier.performance_score = score
            db.commit()
            db.refresh(supplier)
        
        return supplier
