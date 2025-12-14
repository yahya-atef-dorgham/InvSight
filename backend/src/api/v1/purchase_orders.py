"""
Purchase Orders API endpoints.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.session import get_db
from src.api.middleware.tenant import get_tenant_id, get_user_id
from src.services.purchase_order_service import PurchaseOrderService

router = APIRouter(prefix="/purchase-orders", tags=["purchase-orders"])


class PurchaseOrderItemCreate(BaseModel):
    """Purchase order item creation model."""
    product_id: str
    warehouse_id: str | None = None
    quantity: float
    unit_cost: float


class PurchaseOrderCreate(BaseModel):
    """Purchase order creation model."""
    supplier_id: str
    items: List[PurchaseOrderItemCreate]
    order_number: str | None = None
    expected_delivery_date: str | None = None
    notes: str | None = None


class PurchaseOrderItemResponse(BaseModel):
    """Purchase order item response model."""
    id: str
    purchase_order_id: str
    product_id: str
    warehouse_id: str | None
    quantity: float
    unit_cost: float
    total_cost: float
    received_quantity: float
    line_number: int
    
    class Config:
        from_attributes = True


class PurchaseOrderResponse(BaseModel):
    """Purchase order response model."""
    id: str
    tenant_id: str
    order_number: str
    supplier_id: str
    status: str
    total_amount: float | None
    currency: str
    expected_delivery_date: str | None
    actual_delivery_date: str | None
    created_by: str
    created_at: str
    approved_by: str | None
    approved_at: str | None
    sent_at: str | None
    received_at: str | None
    cancelled_at: str | None
    cancelled_by: str | None
    cancellation_reason: str | None
    ai_recommendation_id: str | None
    notes: str | None
    items: List[PurchaseOrderItemResponse] = []
    
    class Config:
        from_attributes = True


class PurchaseOrderUpdate(BaseModel):
    """Purchase order update model."""
    expected_delivery_date: str | None = None
    notes: str | None = None
    currency: str | None = None


class PurchaseOrderReceive(BaseModel):
    """Purchase order receive model."""
    received_items: dict[str, float]  # item_id -> received_quantity


@router.get("", response_model=List[PurchaseOrderResponse])
async def list_purchase_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    supplier_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get list of purchase orders."""
    purchase_orders = PurchaseOrderService.get_all(
        db=db,
        tenant_id=tenant_id,
        supplier_id=supplier_id,
        status=status,
        skip=skip,
        limit=limit
    )
    return purchase_orders


@router.get("/{po_id}", response_model=PurchaseOrderResponse)
async def get_purchase_order(
    po_id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get a purchase order by ID."""
    po = PurchaseOrderService.get_by_id(db, po_id, tenant_id)
    if not po:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found"
        )
    return po


@router.post("", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    po_data: PurchaseOrderCreate,
    tenant_id: UUID = Depends(get_tenant_id),
    user_id: UUID = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """Create a new purchase order."""
    from datetime import datetime as dt
    
    expected_date = None
    if po_data.expected_delivery_date:
        expected_date = dt.fromisoformat(po_data.expected_delivery_date).date()
    
    po = PurchaseOrderService.create(
        db=db,
        supplier_id=UUID(po_data.supplier_id),
        items=[item.model_dump() for item in po_data.items],
        tenant_id=tenant_id,
        user_id=user_id,
        order_number=po_data.order_number,
        expected_delivery_date=expected_date,
        notes=po_data.notes
    )
    
    return po


@router.post("/from-recommendation/{recommendation_id}", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_po_from_recommendation(
    recommendation_id: UUID,
    supplier_id: str,
    order_number: str | None = None,
    tenant_id: UUID = Depends(get_tenant_id),
    user_id: UUID = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """Create purchase order from AI recommendation."""
    try:
        po = PurchaseOrderService.create_from_recommendation(
            db=db,
            recommendation_id=recommendation_id,
            supplier_id=UUID(supplier_id),
            tenant_id=tenant_id,
            user_id=user_id,
            order_number=order_number
        )
        return po
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{po_id}", response_model=PurchaseOrderResponse)
async def update_purchase_order(
    po_id: UUID,
    po_data: PurchaseOrderUpdate,
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Update a purchase order (only if in draft status)."""
    from datetime import datetime as dt
    
    update_data = po_data.model_dump(exclude_unset=True)
    if 'expected_delivery_date' in update_data and update_data['expected_delivery_date']:
        update_data['expected_delivery_date'] = dt.fromisoformat(update_data['expected_delivery_date']).date()
    
    try:
        po = PurchaseOrderService.update(db, po_id, update_data, tenant_id)
        if not po:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found"
            )
        return po
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{po_id}/approve", response_model=PurchaseOrderResponse)
async def approve_purchase_order(
    po_id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    user_id: UUID = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """Approve a purchase order (requires inventory_manager role)."""
    # Check permissions (RBAC)
    # Note: In production, use require_permission decorator
    # For now, we'll allow if authenticated
    
    try:
        po = PurchaseOrderService.approve(db, po_id, tenant_id, user_id)
        if not po:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found"
            )
        return po
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{po_id}/receive", response_model=PurchaseOrderResponse)
async def receive_purchase_order(
    po_id: UUID,
    receive_data: PurchaseOrderReceive,
    tenant_id: UUID = Depends(get_tenant_id),
    user_id: UUID = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """Receive purchase order items and update inventory."""
    try:
        po = PurchaseOrderService.receive(
            db=db,
            po_id=po_id,
            received_items=receive_data.received_items,
            tenant_id=tenant_id,
            user_id=user_id
        )
        if not po:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found"
            )
        return po
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
