"""
Inventory service for managing inventory levels and queries.
"""
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.models.inventory import Inventory
from src.models.inventory_movement import InventoryMovement, MovementType
from src.models.product import Product
from src.models.warehouse import Warehouse
from src.services.audit_service import AuditService
from src.database.tenant_context import get_current_tenant_id
from datetime import datetime, timezone


class InventoryService:
    """Service for inventory operations."""
    
    @staticmethod
    def get_all(
        db: Session,
        tenant_id: UUID,
        warehouse_id: Optional[UUID] = None,
        low_stock_only: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[Inventory]:
        """Get all inventory items for a tenant, optionally filtered by warehouse or low stock."""
        query = db.query(Inventory).filter(Inventory.tenant_id == tenant_id)
        
        if warehouse_id:
            query = query.filter(Inventory.warehouse_id == warehouse_id)
        
        if low_stock_only:
            query = query.filter(
                and_(
                    Inventory.minimum_stock.isnot(None),
                    Inventory.quantity < Inventory.minimum_stock
                )
            )
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, inventory_id: UUID, tenant_id: UUID) -> Optional[Inventory]:
        """Get an inventory item by ID."""
        return db.query(Inventory).filter(
            and_(
                Inventory.id == inventory_id,
                Inventory.tenant_id == tenant_id
            )
        ).first()
    
    @staticmethod
    def get_by_product_and_warehouse(
        db: Session,
        product_id: UUID,
        warehouse_id: UUID,
        tenant_id: UUID
    ) -> Optional[Inventory]:
        """Get inventory for a specific product at a warehouse."""
        return db.query(Inventory).filter(
            and_(
                Inventory.product_id == product_id,
                Inventory.warehouse_id == warehouse_id,
                Inventory.tenant_id == tenant_id
            )
        ).first()
    
    @staticmethod
    def get_low_stock_items(db: Session, tenant_id: UUID, warehouse_id: Optional[UUID] = None) -> List[Inventory]:
        """Get all items with stock below minimum threshold."""
        query = db.query(Inventory).filter(
            and_(
                Inventory.tenant_id == tenant_id,
                Inventory.minimum_stock.isnot(None),
                Inventory.quantity < Inventory.minimum_stock
            )
        )
        
        if warehouse_id:
            query = query.filter(Inventory.warehouse_id == warehouse_id)
        
        return query.all()
    
    @staticmethod
    def create_or_update(
        db: Session,
        product_id: UUID,
        warehouse_id: UUID,
        quantity: Decimal,
        tenant_id: UUID,
        minimum_stock: Optional[Decimal] = None,
        safety_stock: Optional[Decimal] = None
    ) -> Inventory:
        """Create or update inventory for a product at a warehouse."""
        inventory = InventoryService.get_by_product_and_warehouse(
            db, product_id, warehouse_id, tenant_id
        )
        
        if inventory:
            inventory.quantity = quantity
            if minimum_stock is not None:
                inventory.minimum_stock = minimum_stock
            if safety_stock is not None:
                inventory.safety_stock = safety_stock
        else:
            inventory = Inventory(
                tenant_id=tenant_id,
                product_id=product_id,
                warehouse_id=warehouse_id,
                quantity=quantity,
                minimum_stock=minimum_stock,
                safety_stock=safety_stock
            )
            db.add(inventory)
        
        db.commit()
        db.refresh(inventory)
        return inventory
    
    @staticmethod
    def get_inventory_with_details(
        db: Session,
        tenant_id: UUID,
        warehouse_id: Optional[UUID] = None,
        low_stock_only: bool = False
    ) -> List[dict]:
        """Get inventory with product and warehouse details for dashboard."""
        query = db.query(
            Inventory,
            Product,
            Warehouse
        ).join(
            Product, Inventory.product_id == Product.id
        ).join(
            Warehouse, Inventory.warehouse_id == Warehouse.id
        ).filter(
            Inventory.tenant_id == tenant_id
        )
        
        if warehouse_id:
            query = query.filter(Inventory.warehouse_id == warehouse_id)
        
        if low_stock_only:
            query = query.filter(
                and_(
                    Inventory.minimum_stock.isnot(None),
                    Inventory.quantity < Inventory.minimum_stock
                )
            )
        
        results = query.all()
        
        return [
            {
                'id': str(inv.id),
                'product_id': str(inv.product_id),
                'product_sku': prod.sku,
                'product_name': prod.name,
                'warehouse_id': str(inv.warehouse_id),
                'warehouse_name': wh.name,
                'quantity': float(inv.quantity),
                'reserved_quantity': float(inv.reserved_quantity),
                'available_quantity': float(inv.available_quantity),
                'minimum_stock': float(inv.minimum_stock) if inv.minimum_stock else None,
                'safety_stock': float(inv.safety_stock) if inv.safety_stock else None,
                'is_low_stock': inv.is_low_stock,
                'unit_of_measure': prod.unit_of_measure,
                'last_movement_at': inv.last_movement_at.isoformat() if inv.last_movement_at else None,
            }
            for inv, prod, wh in results
        ]
    
    @staticmethod
    def create_inbound_movement(
        db: Session,
        product_id: UUID,
        destination_warehouse_id: UUID,
        quantity: Decimal,
        tenant_id: UUID,
        performed_by: UUID,
        reference_number: Optional[str] = None,
        notes: Optional[str] = None
    ) -> InventoryMovement:
        """
        Create an inbound movement (receiving stock).
        
        Args:
            db: Database session
            product_id: Product ID
            destination_warehouse_id: Warehouse receiving the stock
            quantity: Quantity being received
            tenant_id: Tenant ID
            performed_by: User ID performing the movement
            reference_number: Optional reference number (e.g., PO number)
            notes: Optional notes
            
        Returns:
            Created InventoryMovement
            
        Raises:
            ValueError: If quantity is invalid
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        # Get or create inventory record
        inventory = InventoryService.get_by_product_and_warehouse(
            db, product_id, destination_warehouse_id, tenant_id
        )
        
        quantity_before = Decimal('0')
        if inventory:
            quantity_before = inventory.quantity
            # Check optimistic locking (version will be incremented on update)
            current_version = inventory.version
        else:
            inventory = Inventory(
                tenant_id=tenant_id,
                product_id=product_id,
                warehouse_id=destination_warehouse_id,
                quantity=Decimal('0'),
                version=0
            )
            db.add(inventory)
            db.flush()  # Get the ID
        
        # Update inventory
        inventory.quantity += quantity
        inventory.version += 1
        inventory.last_movement_at = datetime.now(timezone.utc)
        
        quantity_after = inventory.quantity
        
        # Create movement record
        movement = InventoryMovement(
            tenant_id=tenant_id,
            movement_type=MovementType.INBOUND.value,
            product_id=product_id,
            destination_warehouse_id=destination_warehouse_id,
            quantity=quantity,
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            reference_number=reference_number,
            notes=notes,
            performed_by=performed_by,
            performed_at=datetime.now(timezone.utc)
        )
        db.add(movement)
        
        # Audit log
        AuditService.log_action(
            db,
            tenant_id=tenant_id,
            user_id=performed_by,
            action="inventory.movement.inbound",
            entity_type="InventoryMovement",
            entity_id=movement.id,
            changes={
                "product_id": str(product_id),
                "warehouse_id": str(destination_warehouse_id),
                "quantity": float(quantity),
                "quantity_before": float(quantity_before),
                "quantity_after": float(quantity_after)
            }
        )
        
        db.commit()
        db.refresh(movement)
        db.refresh(inventory)
        
        return movement
    
    @staticmethod
    def create_outbound_movement(
        db: Session,
        product_id: UUID,
        source_warehouse_id: UUID,
        quantity: Decimal,
        tenant_id: UUID,
        performed_by: UUID,
        reference_number: Optional[str] = None,
        notes: Optional[str] = None,
        expected_version: Optional[int] = None
    ) -> InventoryMovement:
        """
        Create an outbound movement (shipping stock).
        
        Args:
            db: Database session
            product_id: Product ID
            source_warehouse_id: Warehouse shipping the stock
            quantity: Quantity being shipped
            tenant_id: Tenant ID
            performed_by: User ID performing the movement
            reference_number: Optional reference number
            notes: Optional notes
            expected_version: Expected version for optimistic locking
            
        Returns:
            Created InventoryMovement
            
        Raises:
            ValueError: If insufficient stock or quantity invalid
            RuntimeError: If optimistic locking conflict
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        # Get inventory
        inventory = InventoryService.get_by_product_and_warehouse(
            db, product_id, source_warehouse_id, tenant_id
        )
        
        if not inventory:
            raise ValueError(f"Inventory not found for product {product_id} at warehouse {source_warehouse_id}")
        
        # Optimistic locking check
        if expected_version is not None and inventory.version != expected_version:
            raise RuntimeError("Inventory was modified by another operation. Please refresh and try again.")
        
        quantity_before = inventory.quantity
        available = inventory.available_quantity
        
        # Check sufficient stock
        if available < quantity:
            raise ValueError(
                f"Insufficient stock. Available: {available}, Requested: {quantity}"
            )
        
        # Update inventory
        inventory.quantity -= quantity
        inventory.version += 1
        inventory.last_movement_at = datetime.now(timezone.utc)
        
        quantity_after = inventory.quantity
        
        # Create movement record
        movement = InventoryMovement(
            tenant_id=tenant_id,
            movement_type=MovementType.OUTBOUND.value,
            product_id=product_id,
            source_warehouse_id=source_warehouse_id,
            quantity=quantity,
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            reference_number=reference_number,
            notes=notes,
            performed_by=performed_by,
            performed_at=datetime.now(timezone.utc)
        )
        db.add(movement)
        
        # Audit log
        AuditService.log_action(
            db,
            tenant_id=tenant_id,
            user_id=performed_by,
            action="inventory.movement.outbound",
            entity_type="InventoryMovement",
            entity_id=movement.id,
            changes_json={
                "product_id": str(product_id),
                "warehouse_id": str(source_warehouse_id),
                "quantity": float(quantity),
                "quantity_before": float(quantity_before),
                "quantity_after": float(quantity_after)
            }
        )
        
        db.commit()
        db.refresh(movement)
        db.refresh(inventory)
        
        return movement
    
    @staticmethod
    def create_transfer_movement(
        db: Session,
        product_id: UUID,
        source_warehouse_id: UUID,
        destination_warehouse_id: UUID,
        quantity: Decimal,
        tenant_id: UUID,
        performed_by: UUID,
        reference_number: Optional[str] = None,
        notes: Optional[str] = None,
        expected_version: Optional[int] = None
    ) -> InventoryMovement:
        """
        Create a transfer movement (moving stock between warehouses).
        This is an atomic operation - both source and destination are updated together.
        
        Args:
            db: Database session
            product_id: Product ID
            source_warehouse_id: Warehouse shipping the stock
            destination_warehouse_id: Warehouse receiving the stock
            quantity: Quantity being transferred
            tenant_id: Tenant ID
            performed_by: User ID performing the movement
            reference_number: Optional reference number
            notes: Optional notes
            expected_version: Expected version for optimistic locking (source inventory)
            
        Returns:
            Created InventoryMovement
            
        Raises:
            ValueError: If insufficient stock or quantity invalid
            RuntimeError: If optimistic locking conflict
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        if source_warehouse_id == destination_warehouse_id:
            raise ValueError("Source and destination warehouses must be different")
        
        # Get source inventory
        source_inventory = InventoryService.get_by_product_and_warehouse(
            db, product_id, source_warehouse_id, tenant_id
        )
        
        if not source_inventory:
            raise ValueError(f"Inventory not found for product {product_id} at source warehouse {source_warehouse_id}")
        
        # Optimistic locking check
        if expected_version is not None and source_inventory.version != expected_version:
            raise RuntimeError("Inventory was modified by another operation. Please refresh and try again.")
        
        source_quantity_before = source_inventory.quantity
        available = source_inventory.available_quantity
        
        # Check sufficient stock at source
        if available < quantity:
            raise ValueError(
                f"Insufficient stock at source. Available: {available}, Requested: {quantity}"
            )
        
        # Get or create destination inventory
        dest_inventory = InventoryService.get_by_product_and_warehouse(
            db, product_id, destination_warehouse_id, tenant_id
        )
        
        dest_quantity_before = Decimal('0')
        if dest_inventory:
            dest_quantity_before = dest_inventory.quantity
        else:
            dest_inventory = Inventory(
                tenant_id=tenant_id,
                product_id=product_id,
                warehouse_id=destination_warehouse_id,
                quantity=Decimal('0'),
                version=0
            )
            db.add(dest_inventory)
            db.flush()
        
        # Update both inventories atomically
        source_inventory.quantity -= quantity
        source_inventory.version += 1
        source_inventory.last_movement_at = datetime.utcnow()
        
        dest_inventory.quantity += quantity
        dest_inventory.version += 1
        dest_inventory.last_movement_at = datetime.utcnow()
        
        source_quantity_after = source_inventory.quantity
        dest_quantity_after = dest_inventory.quantity
        
        # Create movement record
        movement = InventoryMovement(
            tenant_id=tenant_id,
            movement_type=MovementType.TRANSFER.value,
            product_id=product_id,
            source_warehouse_id=source_warehouse_id,
            destination_warehouse_id=destination_warehouse_id,
            quantity=quantity,
            quantity_before=source_quantity_before,
            quantity_after=dest_quantity_after,  # Final quantity at destination
            reference_number=reference_number,
            notes=notes,
            performed_by=performed_by,
            performed_at=datetime.now(timezone.utc)
        )
        db.add(movement)
        
        # Audit log
        AuditService.log_action(
            db,
            tenant_id=tenant_id,
            user_id=performed_by,
            action="inventory.movement.transfer",
            entity_type="InventoryMovement",
            entity_id=movement.id,
            changes={
                "product_id": str(product_id),
                "source_warehouse_id": str(source_warehouse_id),
                "destination_warehouse_id": str(destination_warehouse_id),
                "quantity": float(quantity),
                "source_quantity_before": float(source_quantity_before),
                "source_quantity_after": float(source_quantity_after),
                "dest_quantity_before": float(dest_quantity_before),
                "dest_quantity_after": float(dest_quantity_after)
            }
        )
        
        db.commit()
        db.refresh(movement)
        db.refresh(source_inventory)
        db.refresh(dest_inventory)
        
        return movement
    
    @staticmethod
    def get_movement_history(
        db: Session,
        tenant_id: UUID,
        product_id: Optional[UUID] = None,
        warehouse_id: Optional[UUID] = None,
        movement_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[InventoryMovement]:
        """Get movement history with optional filters."""
        query = db.query(InventoryMovement).filter(
            InventoryMovement.tenant_id == tenant_id
        )
        
        if product_id:
            query = query.filter(InventoryMovement.product_id == product_id)
        
        if warehouse_id:
            query = query.filter(
                or_(
                    InventoryMovement.source_warehouse_id == warehouse_id,
                    InventoryMovement.destination_warehouse_id == warehouse_id
                )
            )
        
        if movement_type:
            query = query.filter(InventoryMovement.movement_type == movement_type)
        
        return query.order_by(InventoryMovement.performed_at.desc()).offset(skip).limit(limit).all()
