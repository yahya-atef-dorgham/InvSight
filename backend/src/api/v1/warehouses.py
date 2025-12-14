"""
Warehouses API endpoints.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.session import get_db
from src.api.middleware.tenant import get_tenant_id
from src.services.warehouse_service import WarehouseService

router = APIRouter(prefix="/warehouses", tags=["warehouses"])


class WarehouseCreate(BaseModel):
    """Warehouse creation model."""
    name: str
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None
    capacity_total: float | None = None
    capacity_unit: str | None = None
    is_active: bool = True


class WarehouseUpdate(BaseModel):
    """Warehouse update model."""
    name: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None
    capacity_total: float | None = None
    capacity_unit: str | None = None
    is_active: bool | None = None


class WarehouseResponse(BaseModel):
    """Warehouse response model."""
    id: str
    tenant_id: str
    name: str
    address: str | None
    city: str | None
    state: str | None
    country: str | None
    postal_code: str | None
    capacity_total: float | None
    capacity_unit: str | None
    is_active: bool
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[WarehouseResponse])
async def list_warehouses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get list of warehouses."""
    warehouses = WarehouseService.get_all(db, tenant_id, skip=skip, limit=limit, active_only=active_only)
    return warehouses


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(
    warehouse_id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get a warehouse by ID."""
    warehouse = WarehouseService.get_by_id(db, warehouse_id, tenant_id)
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )
    return warehouse


@router.post("", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    warehouse_data: WarehouseCreate,
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Create a new warehouse."""
    warehouse = WarehouseService.create(db, warehouse_data.model_dump(), tenant_id)
    return warehouse


@router.put("/{warehouse_id}", response_model=WarehouseResponse)
async def update_warehouse(
    warehouse_id: UUID,
    warehouse_data: WarehouseUpdate,
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Update a warehouse."""
    warehouse = WarehouseService.update(db, warehouse_id, warehouse_data.model_dump(exclude_unset=True), tenant_id)
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )
    return warehouse


@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_warehouse(
    warehouse_id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Delete a warehouse."""
    success = WarehouseService.delete(db, warehouse_id, tenant_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )
