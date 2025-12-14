"""
Product service for managing products.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.models.product import Product
from src.database.tenant_context import get_current_tenant_id


class ProductService:
    """Service for product operations."""
    
    @staticmethod
    def get_all(db: Session, tenant_id: UUID, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get all products for a tenant."""
        return db.query(Product).filter(
            Product.tenant_id == tenant_id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, product_id: UUID, tenant_id: UUID) -> Optional[Product]:
        """Get a product by ID."""
        return db.query(Product).filter(
            and_(
                Product.id == product_id,
                Product.tenant_id == tenant_id
            )
        ).first()
    
    @staticmethod
    def get_by_sku(db: Session, sku: str, tenant_id: UUID) -> Optional[Product]:
        """Get a product by SKU."""
        return db.query(Product).filter(
            and_(
                Product.sku == sku,
                Product.tenant_id == tenant_id
            )
        ).first()
    
    @staticmethod
    def create(db: Session, product_data: dict, tenant_id: UUID) -> Product:
        """Create a new product."""
        product = Product(
            tenant_id=tenant_id,
            **product_data
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    
    @staticmethod
    def update(db: Session, product_id: UUID, product_data: dict, tenant_id: UUID) -> Optional[Product]:
        """Update a product."""
        product = ProductService.get_by_id(db, product_id, tenant_id)
        if not product:
            return None
        
        for key, value in product_data.items():
            setattr(product, key, value)
        
        db.commit()
        db.refresh(product)
        return product
    
    @staticmethod
    def delete(db: Session, product_id: UUID, tenant_id: UUID) -> bool:
        """Delete a product."""
        product = ProductService.get_by_id(db, product_id, tenant_id)
        if not product:
            return False
        
        db.delete(product)
        db.commit()
        return True
