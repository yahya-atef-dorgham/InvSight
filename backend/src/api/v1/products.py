"""
Products API endpoints.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.session import get_db
from src.api.middleware.tenant import get_tenant_id
from src.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


class ProductCreate(BaseModel):
    """Product creation model."""
    sku: str
    name: str
    description: str | None = None
    category: str | None = None
    unit_of_measure: str


class ProductUpdate(BaseModel):
    """Product update model."""
    name: str | None = None
    description: str | None = None
    category: str | None = None
    unit_of_measure: str | None = None


class ProductResponse(BaseModel):
    """Product response model."""
    id: str
    tenant_id: str
    sku: str
    name: str
    description: str | None
    category: str | None
    unit_of_measure: str
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[ProductResponse])
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get list of products."""
    products = ProductService.get_all(db, tenant_id, skip=skip, limit=limit)
    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get a product by ID."""
    product = ProductService.get_by_id(db, product_id, tenant_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Create a new product."""
    # Check if SKU already exists
    existing = ProductService.get_by_sku(db, product_data.sku, tenant_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with SKU '{product_data.sku}' already exists"
        )
    
    product = ProductService.create(db, product_data.model_dump(), tenant_id)
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Update a product."""
    product = ProductService.update(db, product_id, product_data.model_dump(exclude_unset=True), tenant_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Delete a product."""
    success = ProductService.delete(db, product_id, tenant_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
