"""
Purchase order service with state machine and business logic.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from src.models.purchase_order import PurchaseOrder, PurchaseOrderStatus
from src.models.purchase_order_item import PurchaseOrderItem
from src.models.ai_recommendation import AIRecommendation
from src.models.inventory import Inventory
from src.services.inventory_service import InventoryService
from src.services.audit_service import AuditService


class PurchaseOrderService:
    """Service for purchase order operations with state machine."""
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        PurchaseOrderStatus.DRAFT.value: [PurchaseOrderStatus.APPROVED.value, PurchaseOrderStatus.CANCELLED.value],
        PurchaseOrderStatus.APPROVED.value: [PurchaseOrderStatus.SENT.value, PurchaseOrderStatus.CANCELLED.value],
        PurchaseOrderStatus.SENT.value: [PurchaseOrderStatus.PARTIALLY_RECEIVED.value, PurchaseOrderStatus.RECEIVED.value, PurchaseOrderStatus.CANCELLED.value],
        PurchaseOrderStatus.PARTIALLY_RECEIVED.value: [PurchaseOrderStatus.RECEIVED.value],
        PurchaseOrderStatus.RECEIVED.value: [],  # Terminal state
        PurchaseOrderStatus.CANCELLED.value: [],  # Terminal state
    }
    
    @staticmethod
    def create_from_recommendation(
        db: Session,
        recommendation_id: UUID,
        supplier_id: UUID,
        tenant_id: UUID,
        user_id: UUID,
        order_number: Optional[str] = None
    ) -> PurchaseOrder:
        """
        Create purchase order from AI recommendation.
        
        Args:
            db: Database session
            recommendation_id: AI recommendation ID
            supplier_id: Supplier ID
            tenant_id: Tenant ID
            user_id: User creating the PO
            order_number: Optional order number (auto-generated if not provided)
            
        Returns:
            Created PurchaseOrder
        """
        # Get recommendation
        recommendation = db.query(AIRecommendation).filter(
            and_(
                AIRecommendation.id == recommendation_id,
                AIRecommendation.tenant_id == tenant_id
            )
        ).first()
        
        if not recommendation:
            raise ValueError("Recommendation not found")
        
        if recommendation.status != 'active':
            raise ValueError("Only active recommendations can be used to create purchase orders")
        
        # Generate order number if not provided
        if not order_number:
            order_number = f"PO-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{recommendation.id.hex[:8].upper()}"
        
        # Create purchase order
        po = PurchaseOrder(
            tenant_id=tenant_id,
            order_number=order_number,
            supplier_id=supplier_id,
            status=PurchaseOrderStatus.DRAFT.value,
            currency='USD',
            created_by=user_id,
            ai_recommendation_id=recommendation_id,
            notes=f"Created from AI recommendation: {recommendation.explanation}"
        )
        
        db.add(po)
        db.flush()  # Get PO ID
        
        # Create purchase order item from recommendation
        if recommendation.recommended_value:
            item = PurchaseOrderItem(
                tenant_id=tenant_id,
                purchase_order_id=po.id,
                product_id=recommendation.product_id,  # Already UUID
                warehouse_id=recommendation.warehouse_id,  # Already UUID
                quantity=Decimal(str(recommendation.recommended_value)),
                unit_cost=Decimal('0'),  # Will be updated later
                total_cost=Decimal('0'),
                line_number=1
            )
            db.add(item)
        
        # Calculate total
        PurchaseOrderService._calculate_total(db, po.id)
        
        # Update recommendation status
        recommendation.status = 'approved'  # Mark as used
        recommendation.actioned_by = user_id
        recommendation.actioned_at = datetime.now(timezone.utc)
        
        # Audit log
        AuditService.log_action(
            db,
            tenant_id=tenant_id,
            user_id=user_id,
            action="purchase_order.create_from_recommendation",
            entity_type="PurchaseOrder",
            entity_id=po.id,
            changes={
                "recommendation_id": str(recommendation_id),
                "supplier_id": str(supplier_id),
                "order_number": order_number
            }
        )
        
        db.commit()
        db.refresh(po)
        
        return po
    
    @staticmethod
    def create(
        db: Session,
        supplier_id: UUID,
        items: List[Dict[str, Any]],
        tenant_id: UUID,
        user_id: UUID,
        order_number: Optional[str] = None,
        expected_delivery_date: Optional[date] = None,
        notes: Optional[str] = None
    ) -> PurchaseOrder:
        """Create a new purchase order."""
        if not order_number:
            order_number = f"PO-{datetime.utcnow().strftime('%Y%m%d')}-{UUID().hex[:8].upper()}"
        
        po = PurchaseOrder(
            tenant_id=tenant_id,
            order_number=order_number,
            supplier_id=supplier_id,
            status=PurchaseOrderStatus.DRAFT.value,
            currency='USD',
            created_by=user_id,
            expected_delivery_date=expected_delivery_date,
            notes=notes
        )
        
        db.add(po)
        db.flush()
        
        # Create items
        for idx, item_data in enumerate(items, start=1):
            item = PurchaseOrderItem(
                tenant_id=tenant_id,
                purchase_order_id=po.id,
                product_id=UUID(item_data['product_id']),
                warehouse_id=UUID(item_data['warehouse_id']) if item_data.get('warehouse_id') else None,
                quantity=Decimal(str(item_data['quantity'])),
                unit_cost=Decimal(str(item_data['unit_cost'])),
                total_cost=Decimal(str(item_data['quantity'])) * Decimal(str(item_data['unit_cost'])),
                line_number=idx
            )
            db.add(item)
        
        # Calculate total
        PurchaseOrderService._calculate_total(db, po.id)
        
        db.commit()
        db.refresh(po)
        
        return po
    
    @staticmethod
    def approve(
        db: Session,
        po_id: UUID,
        tenant_id: UUID,
        user_id: UUID
    ) -> Optional[PurchaseOrder]:
        """
        Approve a purchase order (state transition: draft -> approved).
        
        Args:
            db: Database session
            po_id: Purchase order ID
            tenant_id: Tenant ID
            user_id: User approving the PO
            
        Returns:
            Updated PurchaseOrder or None if not found
        """
        po = PurchaseOrderService.get_by_id(db, po_id, tenant_id)
        if not po:
            return None
        
        # Validate state transition
        if po.status != PurchaseOrderStatus.DRAFT.value:
            raise ValueError(f"Cannot approve PO in {po.status} status. Only draft POs can be approved.")
        
        # Update status
        po.status = PurchaseOrderStatus.APPROVED.value
        po.approved_by = user_id
        po.approved_at = datetime.now(timezone.utc)
        
        # Audit log
        AuditService.log_action(
            db,
            tenant_id=tenant_id,
            user_id=user_id,
            action="purchase_order.approve",
            entity_type="PurchaseOrder",
            entity_id=po.id,
            changes={
                "status": PurchaseOrderStatus.APPROVED.value,
                "approved_by": str(user_id)
            }
        )
        
        db.commit()
        db.refresh(po)
        
        return po
    
    @staticmethod
    def receive(
        db: Session,
        po_id: UUID,
        received_items: Dict[str, float],  # item_id -> received_quantity
        tenant_id: UUID,
        user_id: UUID
    ) -> Optional[PurchaseOrder]:
        """
        Receive purchase order items and update inventory.
        
        Args:
            db: Database session
            po_id: Purchase order ID
            received_items: Dictionary mapping item_id to received quantity
            tenant_id: Tenant ID
            user_id: User receiving the items
            
        Returns:
            Updated PurchaseOrder
        """
        po = PurchaseOrderService.get_by_id(db, po_id, tenant_id)
        if not po:
            return None
        
        if po.status not in [PurchaseOrderStatus.SENT.value, PurchaseOrderStatus.PARTIALLY_RECEIVED.value]:
            raise ValueError(f"Cannot receive PO in {po.status} status")
        
        # Update received quantities
        all_received = True
        for item in po.items:
            if str(item.id) in received_items:
                received_qty = Decimal(str(received_items[str(item.id)]))
                if received_qty > item.quantity:
                    raise ValueError(f"Received quantity ({received_qty}) cannot exceed ordered quantity ({item.quantity})")
                
                item.received_quantity = received_qty
                
                # Create inbound movement
                if item.warehouse_id:
                    InventoryService.create_inbound_movement(
                        db=db,
                        product_id=item.product_id,
                        destination_warehouse_id=item.warehouse_id,
                        quantity=received_qty,
                        tenant_id=tenant_id,
                        performed_by=user_id,
                        reference_number=po.order_number,
                        notes=f"Received from PO {po.order_number}"
                    )
            
            if item.received_quantity < item.quantity:
                all_received = False
        
        # Update PO status
        if all_received:
            po.status = PurchaseOrderStatus.RECEIVED.value
            po.received_at = datetime.utcnow()
        else:
            po.status = PurchaseOrderStatus.PARTIALLY_RECEIVED.value
        
        # Audit log
        AuditService.log_action(
            db,
            tenant_id=tenant_id,
            user_id=user_id,
            action="purchase_order.receive",
            entity_type="PurchaseOrder",
            entity_id=po.id,
            changes={
                "status": po.status,
                "received_items": received_items
            }
        )
        
        db.commit()
        db.refresh(po)
        
        return po
    
    @staticmethod
    def _calculate_total(db: Session, po_id: UUID):
        """Calculate and update purchase order total amount."""
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        if not po:
            return
        
        total = db.query(func.sum(PurchaseOrderItem.total_cost)).filter(
            PurchaseOrderItem.purchase_order_id == po_id
        ).scalar()
        
        po.total_amount = Decimal(str(total)) if total else Decimal('0')
    
    @staticmethod
    def get_by_id(db: Session, po_id: UUID, tenant_id: UUID) -> Optional[PurchaseOrder]:
        """Get a purchase order by ID."""
        return db.query(PurchaseOrder).filter(
            and_(
                PurchaseOrder.id == po_id,
                PurchaseOrder.tenant_id == tenant_id
            )
        ).first()
    
    @staticmethod
    def get_all(
        db: Session,
        tenant_id: UUID,
        supplier_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PurchaseOrder]:
        """Get all purchase orders with optional filters."""
        query = db.query(PurchaseOrder).filter(PurchaseOrder.tenant_id == tenant_id)
        
        if supplier_id:
            query = query.filter(PurchaseOrder.supplier_id == supplier_id)
        
        if status:
            query = query.filter(PurchaseOrder.status == status)
        
        return query.order_by(desc(PurchaseOrder.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(
        db: Session,
        po_id: UUID,
        po_data: Dict[str, Any],
        tenant_id: UUID
    ) -> Optional[PurchaseOrder]:
        """Update purchase order (only if in draft status)."""
        po = PurchaseOrderService.get_by_id(db, po_id, tenant_id)
        if not po:
            return None
        
        if po.status != PurchaseOrderStatus.DRAFT.value:
            raise ValueError(f"Cannot update PO in {po.status} status. Only draft POs can be modified.")
        
        # Update allowed fields
        allowed_fields = ['expected_delivery_date', 'notes', 'currency']
        for key, value in po_data.items():
            if key in allowed_fields:
                setattr(po, key, value)
        
        db.commit()
        db.refresh(po)
        
        return po
