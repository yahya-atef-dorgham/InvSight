"""
Inventory API endpoints.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.session import get_db
from src.api.middleware.tenant import get_tenant_id, get_user_id
from src.services.inventory_service import InventoryService
from src.models.inventory_movement import InventoryMovement

router = APIRouter(prefix="/inventory", tags=["inventory"])


class InventoryResponse(BaseModel):
    """Inventory response model with product and warehouse details."""
    id: str
    product_id: str
    product_sku: str
    product_name: str
    warehouse_id: str
    warehouse_name: str
    quantity: float
    reserved_quantity: float
    available_quantity: float
    minimum_stock: float | None
    safety_stock: float | None
    is_low_stock: bool
    unit_of_measure: str
    last_movement_at: str | None


@router.get("", response_model=List[InventoryResponse])
async def list_inventory(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    warehouse_id: Optional[UUID] = Query(None),
    low_stock: bool = Query(False, description="Filter to show only low stock items"),
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get list of inventory items with product and warehouse details."""
    inventory_items = InventoryService.get_inventory_with_details(
        db,
        tenant_id,
        warehouse_id=warehouse_id,
        low_stock_only=low_stock
    )
    
    # Apply pagination
    return inventory_items[skip:skip + limit]


@router.get("/low-stock", response_model=List[InventoryResponse])
async def get_low_stock_items(
    warehouse_id: Optional[UUID] = Query(None),
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get all inventory items with stock below minimum threshold."""
    inventory_items = InventoryService.get_inventory_with_details(
        db,
        tenant_id,
        warehouse_id=warehouse_id,
        low_stock_only=True
    )
    return inventory_items


class MovementCreate(BaseModel):
    """Movement creation model."""
    movement_type: str  # 'inbound', 'outbound', 'transfer'
    product_id: str
    source_warehouse_id: str | None = None  # Required for outbound/transfer
    destination_warehouse_id: str | None = None  # Required for inbound/transfer
    quantity: float
    reference_number: str | None = None
    notes: str | None = None
    expected_version: int | None = None  # For optimistic locking


class MovementResponse(BaseModel):
    """Movement response model."""
    id: str
    tenant_id: str
    movement_type: str
    product_id: str
    source_warehouse_id: str | None
    destination_warehouse_id: str | None
    quantity: float
    quantity_before: float | None
    quantity_after: float | None
    reference_number: str | None
    notes: str | None
    performed_by: str
    performed_at: str
    approved_by: str | None
    approved_at: str | None
    
    class Config:
        from_attributes = True


@router.post("/movement", response_model=MovementResponse, status_code=status.HTTP_201_CREATED)
async def create_movement(
    movement_data: MovementCreate,
    tenant_id: UUID = Depends(get_tenant_id),
    user_id: UUID = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """
    Create an inventory movement (inbound, outbound, or transfer).
    
    Movement types:
    - inbound: Receiving stock (requires destination_warehouse_id)
    - outbound: Shipping stock (requires source_warehouse_id)
    - transfer: Moving stock between warehouses (requires both)
    """
    from decimal import Decimal
    
    product_id = UUID(movement_data.product_id)
    quantity = Decimal(str(movement_data.quantity))
    
    try:
        if movement_data.movement_type == "inbound":
            if not movement_data.destination_warehouse_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="destination_warehouse_id is required for inbound movements"
                )
            
            movement = InventoryService.create_inbound_movement(
                db=db,
                product_id=product_id,
                destination_warehouse_id=UUID(movement_data.destination_warehouse_id),
                quantity=quantity,
                tenant_id=tenant_id,
                performed_by=user_id,
                reference_number=movement_data.reference_number,
                notes=movement_data.notes
            )
            
        elif movement_data.movement_type == "outbound":
            if not movement_data.source_warehouse_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="source_warehouse_id is required for outbound movements"
                )
            
            movement = InventoryService.create_outbound_movement(
                db=db,
                product_id=product_id,
                source_warehouse_id=UUID(movement_data.source_warehouse_id),
                quantity=quantity,
                tenant_id=tenant_id,
                performed_by=user_id,
                reference_number=movement_data.reference_number,
                notes=movement_data.notes,
                expected_version=movement_data.expected_version
            )
            
        elif movement_data.movement_type == "transfer":
            if not movement_data.source_warehouse_id or not movement_data.destination_warehouse_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Both source_warehouse_id and destination_warehouse_id are required for transfer movements"
                )
            
            movement = InventoryService.create_transfer_movement(
                db=db,
                product_id=product_id,
                source_warehouse_id=UUID(movement_data.source_warehouse_id),
                destination_warehouse_id=UUID(movement_data.destination_warehouse_id),
                quantity=quantity,
                tenant_id=tenant_id,
                performed_by=user_id,
                reference_number=movement_data.reference_number,
                notes=movement_data.notes,
                expected_version=movement_data.expected_version
            )
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid movement_type: {movement_data.movement_type}. Must be 'inbound', 'outbound', or 'transfer'"
            )
        
        return movement
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/movements", response_model=List[MovementResponse])
async def get_movement_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    product_id: Optional[UUID] = Query(None),
    warehouse_id: Optional[UUID] = Query(None),
    movement_type: Optional[str] = Query(None, description="Filter by type: inbound, outbound, transfer"),
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get movement history with optional filters."""
    # Validate movement_type if provided
    if movement_type and movement_type not in ["inbound", "outbound", "transfer"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid movement_type: {movement_type}. Must be 'inbound', 'outbound', or 'transfer'"
        )
    
    movements = InventoryService.get_movement_history(
        db=db,
        tenant_id=tenant_id,
        product_id=product_id,
        warehouse_id=warehouse_id,
        movement_type=movement_type,
        skip=skip,
        limit=limit
    )
    
    return movements
