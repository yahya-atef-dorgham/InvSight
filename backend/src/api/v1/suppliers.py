"""
Suppliers API endpoints.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.session import get_db
from src.api.middleware.tenant import get_tenant_id
from src.services.supplier_service import SupplierService

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


class SupplierCreate(BaseModel):
    """Supplier creation model."""
    name: str
    contact_email: str | None = None
    contact_phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None
    payment_terms: str | None = None
    tax_id: str | None = None
    is_active: bool = True


class SupplierUpdate(BaseModel):
    """Supplier update model."""
    name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None
    payment_terms: str | None = None
    tax_id: str | None = None
    is_active: bool | None = None


class SupplierResponse(BaseModel):
    """Supplier response model."""
    id: str
    tenant_id: str
    name: str
    contact_email: str | None
    contact_phone: str | None
    address: str | None
    city: str | None
    state: str | None
    country: str | None
    postal_code: str | None
    payment_terms: str | None
    tax_id: str | None
    is_active: bool
    performance_score: float | None
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[SupplierResponse])
async def list_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get list of suppliers."""
    suppliers = SupplierService.get_all(db, tenant_id, skip=skip, limit=limit, active_only=active_only)
    return suppliers


@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get a supplier by ID."""
    supplier = SupplierService.get_by_id(db, supplier_id, tenant_id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    return supplier


@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    supplier_data: SupplierCreate,
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Create a new supplier."""
    supplier = SupplierService.create(db, supplier_data.model_dump(), tenant_id)
    return supplier


@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: UUID,
    supplier_data: SupplierUpdate,
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Update a supplier."""
    supplier = SupplierService.update(db, supplier_id, supplier_data.model_dump(exclude_unset=True), tenant_id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    return supplier
