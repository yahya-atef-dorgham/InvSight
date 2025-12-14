# Data Model: AI-Powered Inventory Management System

**Feature**: 001-ai-inventory-voice  
**Date**: 2025-01-27  
**Database**: PostgreSQL 15+

## Multi-Tenancy

All tables include `tenant_id UUID NOT NULL` for tenant isolation. Row-Level Security (RLS) policies enforce tenant isolation at the database level. All queries must include tenant_id in WHERE clauses.

**Index**: `CREATE INDEX idx_<table>_tenant ON <table>(tenant_id);` on all tables.

## Entities

### 1. Product

**Purpose**: Represents items in the inventory catalog.

**Table**: `products`

**Columns**:
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `tenant_id` UUID NOT NULL (FK to tenants, with RLS)
- `sku` VARCHAR(100) NOT NULL
- `name` VARCHAR(255) NOT NULL
- `description` TEXT
- `category` VARCHAR(100)
- `unit_of_measure` VARCHAR(50) NOT NULL (e.g., 'pieces', 'kg', 'liters')
- `created_at` TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
- `updated_at` TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
- `created_by` UUID (FK to users)
- `updated_by` UUID (FK to users)

**Constraints**:
- UNIQUE(tenant_id, sku) - SKU must be unique per tenant
- CHECK (unit_of_measure IN ('pieces', 'kg', 'liters', 'meters', 'boxes', ...))

**Indexes**:
- idx_products_tenant_id
- idx_products_tenant_sku (UNIQUE)
- idx_products_category (for filtering)

**Relationships**:
- Has many: Inventory (one per warehouse)
- Has many: InventoryMovement
- Has many: PurchaseOrderItem
- Has many: Forecast

**Validation Rules**:
- SKU required, max 100 characters, alphanumeric and dashes only
- Name required, max 255 characters
- Unit of measure required, must be from allowed list

---

### 2. Warehouse

**Purpose**: Represents physical storage locations.

**Table**: `warehouses`

**Columns**:
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `tenant_id` UUID NOT NULL
- `name` VARCHAR(255) NOT NULL
- `address` TEXT
- `city` VARCHAR(100)
- `state` VARCHAR(100)
- `country` VARCHAR(100)
- `postal_code` VARCHAR(20)
- `capacity_total` DECIMAL(15,2) (total capacity in unit_of_measure)
- `capacity_unit` VARCHAR(50) (e.g., 'cubic_meters', 'square_meters')
- `is_active` BOOLEAN NOT NULL DEFAULT true
- `created_at` TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
- `updated_at` TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
- `created_by` UUID (FK to users)
- `updated_by` UUID (FK to users)

**Constraints**:
- UNIQUE(tenant_id, name) - Warehouse name unique per tenant

**Indexes**:
- idx_warehouses_tenant_id
- idx_warehouses_tenant_name (UNIQUE)
- idx_warehouses_active (WHERE is_active = true)

**Relationships**:
- Has many: Inventory (one per product)
- Source for: InventoryMovement (outbound/transfer)
- Destination for: InventoryMovement (inbound/transfer)

**Validation Rules**:
- Name required, max 255 characters
- Capacity constraints validated before accepting inbound movements

---

### 3. Inventory

**Purpose**: Represents current stock level for a product at a specific warehouse.

**Table**: `inventory`

**Columns**:
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `tenant_id` UUID NOT NULL
- `product_id` UUID NOT NULL (FK to products)
- `warehouse_id` UUID NOT NULL (FK to warehouses)
- `quantity` DECIMAL(15,3) NOT NULL DEFAULT 0
- `reserved_quantity` DECIMAL(15,3) NOT NULL DEFAULT 0 (for pending outbound movements)
- `minimum_stock` DECIMAL(15,3)
- `safety_stock` DECIMAL(15,3)
- `reorder_point` DECIMAL(15,3) (calculated from forecasts)
- `last_movement_at` TIMESTAMP WITH TIME ZONE
- `last_updated_at` TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
- `version` INTEGER NOT NULL DEFAULT 0 (for optimistic locking)

**Constraints**:
- UNIQUE(tenant_id, product_id, warehouse_id)
- CHECK (quantity >= 0 OR tenant.allow_negative_inventory = true)
- CHECK (reserved_quantity >= 0)
- CHECK (reserved_quantity <= quantity)

**Indexes**:
- idx_inventory_tenant_id
- idx_inventory_product_warehouse (UNIQUE)
- idx_inventory_low_stock (WHERE quantity < minimum_stock)
- idx_inventory_warehouse (for warehouse-level queries)

**Relationships**:
- Belongs to: Product
- Belongs to: Warehouse
- Has many: InventoryMovement (history)

**Validation Rules**:
- Quantity cannot go negative (unless tenant allows it for backorders)
- Minimum stock and safety stock cannot be negative
- Optimistic locking via version column for concurrent updates

**State Transitions**:
- On inbound movement: quantity increases, last_movement_at updated
- On outbound movement: quantity decreases (if sufficient stock), last_movement_at updated
- On transfer: quantity decreases at source, increases at destination atomically

---

### 4. InventoryMovement

**Purpose**: Represents a change in inventory quantity (audit trail).

**Table**: `inventory_movements`

**Columns**:
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `tenant_id` UUID NOT NULL
- `movement_type` VARCHAR(20) NOT NULL ('inbound', 'outbound', 'transfer')
- `product_id` UUID NOT NULL (FK to products)
- `source_warehouse_id` UUID (FK to warehouses, NULL for inbound)
- `destination_warehouse_id` UUID (FK to warehouses, NULL for outbound)
- `quantity` DECIMAL(15,3) NOT NULL
- `quantity_before` DECIMAL(15,3) NOT NULL (at source for transfers)
- `quantity_after` DECIMAL(15,3) NOT NULL (at destination for transfers)
- `reference_number` VARCHAR(100) (e.g., PO number, shipment number)
- `notes` TEXT
- `performed_by` UUID NOT NULL (FK to users)
- `performed_at` TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
- `approved_by` UUID (FK to users, for large movements if required)
- `approved_at` TIMESTAMP WITH TIME ZONE

**Constraints**:
- CHECK (movement_type IN ('inbound', 'outbound', 'transfer'))
- CHECK (movement_type = 'inbound' AND source_warehouse_id IS NULL AND destination_warehouse_id IS NOT NULL)
- CHECK (movement_type = 'outbound' AND source_warehouse_id IS NOT NULL AND destination_warehouse_id IS NULL)
- CHECK (movement_type = 'transfer' AND source_warehouse_id IS NOT NULL AND destination_warehouse_id IS NOT NULL)
- CHECK (quantity > 0)

**Indexes**:
- idx_inventory_movements_tenant_id
- idx_inventory_movements_product_id
- idx_inventory_movements_warehouse_id (on both source and destination)
- idx_inventory_movements_performed_at (for time-based queries)
- idx_inventory_movements_performed_by
- idx_inventory_movements_type

**Relationships**:
- Belongs to: Product
- Belongs to: Warehouse (source and/or destination)
- Belongs to: User (performed_by, approved_by)

**Validation Rules**:
- Quantity must be positive
- Outbound movements must have sufficient stock (validated before insert)
- Transfers must have sufficient stock at source (validated before insert)
- All movements recorded in audit trail with before/after quantities

**Partitioning**: Consider partitioning by `performed_at` date for large datasets (e.g., monthly partitions).

---

### 5. Supplier

**Purpose**: Represents external vendors who provide products.

**Table**: `suppliers`

**Columns**:
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `tenant_id` UUID NOT NULL
- `name` VARCHAR(255) NOT NULL
- `contact_email` VARCHAR(255)
- `contact_phone` VARCHAR(50)
- `address` TEXT
- `city` VARCHAR(100)
- `state` VARCHAR(100)
- `country` VARCHAR(100)
- `postal_code` VARCHAR(20)
- `payment_terms` VARCHAR(100) (e.g., 'Net 30', 'Net 60')
- `tax_id` VARCHAR(100)
- `is_active` BOOLEAN NOT NULL DEFAULT true
- `performance_score` DECIMAL(5,2) (calculated from fulfillment history, 0-100)
- `created_at` TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
- `updated_at` TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
- `created_by` UUID (FK to users)
- `updated_by` UUID (FK to users)

**Constraints**:
- UNIQUE(tenant_id, name)

**Indexes**:
- idx_suppliers_tenant_id
- idx_suppliers_tenant_name (UNIQUE)
- idx_suppliers_active (WHERE is_active = true)

**Relationships**:
- Has many: PurchaseOrder

**Validation Rules**:
- Name required, max 255 characters
- Email format validation if provided
- Payment terms required for purchase order creation

---

### 6. PurchaseOrder

**Purpose**: Represents a request to purchase inventory from a supplier.

**Table**: `purchase_orders`

**Columns**:
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `tenant_id` UUID NOT NULL
- `order_number` VARCHAR(100) NOT NULL (tenant-scoped unique identifier)
- `supplier_id` UUID NOT NULL (FK to suppliers)
- `status` VARCHAR(20) NOT NULL DEFAULT 'draft' ('draft', 'approved', 'sent', 'partially_received', 'received', 'cancelled')
- `total_amount` DECIMAL(15,2) (calculated from items)
- `currency` VARCHAR(3) NOT NULL DEFAULT 'USD'
- `expected_delivery_date` DATE
- `actual_delivery_date` DATE
- `created_by` UUID NOT NULL (FK to users)
- `created_at` TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
- `approved_by` UUID (FK to users)
- `approved_at` TIMESTAMP WITH TIME ZONE
- `sent_at` TIMESTAMP WITH TIME ZONE
- `received_at` TIMESTAMP WITH TIME ZONE
- `cancelled_at` TIMESTAMP WITH TIME ZONE
- `cancelled_by` UUID (FK to users)
- `cancellation_reason` TEXT
- `ai_recommendation_id` UUID (FK to ai_recommendations, if created from AI)
- `notes` TEXT

**Constraints**:
- UNIQUE(tenant_id, order_number)
- CHECK (status IN ('draft', 'approved', 'sent', 'partially_received', 'received', 'cancelled'))

**Indexes**:
- idx_purchase_orders_tenant_id
- idx_purchase_orders_tenant_order_number (UNIQUE)
- idx_purchase_orders_supplier_id
- idx_purchase_orders_status
- idx_purchase_orders_created_at
- idx_purchase_orders_ai_recommendation_id

**Relationships**:
- Belongs to: Supplier
- Has many: PurchaseOrderItem
- Belongs to: AIRecommendation (if AI-generated)
- Belongs to: User (created_by, approved_by, cancelled_by)

**Validation Rules**:
- Order number required, unique per tenant
- Cannot transition from 'received' or 'cancelled' to other states
- Total amount calculated from items
- Approved status requires approved_by and approved_at

**State Machine**:
```
draft → approved → sent → partially_received → received
  ↓         ↓         ↓
cancelled  cancelled cancelled
```

---

### 7. PurchaseOrderItem

**Purpose**: Items within a purchase order.

**Table**: `purchase_order_items`

**Columns**:
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `tenant_id` UUID NOT NULL
- `purchase_order_id` UUID NOT NULL (FK to purchase_orders)
- `product_id` UUID NOT NULL (FK to products)
- `warehouse_id` UUID (FK to warehouses, destination for received stock)
- `quantity` DECIMAL(15,3) NOT NULL
- `unit_cost` DECIMAL(15,2) NOT NULL
- `total_cost` DECIMAL(15,2) NOT NULL (quantity * unit_cost)
- `received_quantity` DECIMAL(15,3) NOT NULL DEFAULT 0
- `line_number` INTEGER NOT NULL (ordering within PO)

**Constraints**:
- CHECK (quantity > 0)
- CHECK (unit_cost >= 0)
- CHECK (received_quantity >= 0)
- CHECK (received_quantity <= quantity)

**Indexes**:
- idx_purchase_order_items_tenant_id
- idx_purchase_order_items_purchase_order_id
- idx_purchase_order_items_product_id

**Relationships**:
- Belongs to: PurchaseOrder
- Belongs to: Product
- Belongs to: Warehouse (destination)

**Validation Rules**:
- Quantity and unit cost must be positive
- Received quantity cannot exceed ordered quantity
- When received_quantity = quantity, PO item is fully received

---

### 8. Forecast

**Purpose**: AI-generated demand predictions.

**Table**: `forecasts`

**Columns**:
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `tenant_id` UUID NOT NULL
- `product_id` UUID NOT NULL (FK to products)
- `warehouse_id` UUID NOT NULL (FK to warehouses)
- `forecast_horizon_days` INTEGER NOT NULL (7, 30, or 90)
- `forecast_date` DATE NOT NULL (date for which forecast is generated)
- `predicted_demand` DECIMAL(15,3) NOT NULL
- `confidence_lower` DECIMAL(15,3) (lower bound of confidence interval)
- `confidence_upper` DECIMAL(15,3) (upper bound of confidence interval)
- `confidence_level` DECIMAL(5,2) (e.g., 0.80 for 80% confidence)
- `model_version` VARCHAR(50) NOT NULL (AI model version used)
- `model_type` VARCHAR(50) (e.g., 'arima', 'exponential_smoothing', 'lstm')
- `generated_at` TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
- `features_json` JSONB (model input features for explainability)

**Constraints**:
- CHECK (forecast_horizon_days IN (7, 30, 90))
- CHECK (predicted_demand >= 0)
- UNIQUE(tenant_id, product_id, warehouse_id, forecast_horizon_days, forecast_date)

**Indexes**:
- idx_forecasts_tenant_id
- idx_forecasts_product_warehouse
- idx_forecasts_horizon_date (for time-based queries)
- idx_forecasts_model_version
- idx_forecasts_generated_at

**Relationships**:
- Belongs to: Product
- Belongs to: Warehouse
- Referenced by: AIRecommendation

**Validation Rules**:
- Forecast horizon must be 7, 30, or 90 days
- Predicted demand cannot be negative
- Model version required for auditability

---

### 9. AIRecommendation

**Purpose**: AI-generated recommendations for reorder points, quantities, and purchase orders.

**Table**: `ai_recommendations`

**Columns**:
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `tenant_id` UUID NOT NULL
- `recommendation_type` VARCHAR(50) NOT NULL ('reorder_point', 'reorder_quantity', 'purchase_order')
- `product_id` UUID NOT NULL (FK to products)
- `warehouse_id` UUID NOT NULL (FK to warehouses)
- `forecast_id` UUID (FK to forecasts, if based on forecast)
- `recommended_value` DECIMAL(15,3) (reorder point or quantity)
- `current_value` DECIMAL(15,3) (current stock level or reorder point)
- `urgency_score` DECIMAL(5,2) (0-100, higher = more urgent)
- `confidence_score` DECIMAL(5,2) (0-100)
- `explanation` TEXT (human-readable explanation of recommendation)
- `explanation_json` JSONB (structured explanation data: features, reasoning)
- `status` VARCHAR(20) NOT NULL DEFAULT 'active' ('active', 'approved', 'rejected', 'superseded')
- `created_at` TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
- `actioned_at` TIMESTAMP WITH TIME ZONE (when user acted on recommendation)
- `actioned_by` UUID (FK to users)
- `purchase_order_id` UUID (FK to purchase_orders, if created PO)

**Constraints**:
- CHECK (recommendation_type IN ('reorder_point', 'reorder_quantity', 'purchase_order'))
- CHECK (status IN ('active', 'approved', 'rejected', 'superseded'))
- CHECK (recommended_value >= 0)

**Indexes**:
- idx_ai_recommendations_tenant_id
- idx_ai_recommendations_product_warehouse
- idx_ai_recommendations_type_status
- idx_ai_recommendations_urgency (ORDER BY urgency_score DESC)
- idx_ai_recommendations_created_at

**Relationships**:
- Belongs to: Product
- Belongs to: Warehouse
- Belongs to: Forecast (optional)
- Belongs to: PurchaseOrder (if created PO)
- Belongs to: User (actioned_by)

**Validation Rules**:
- Explanation required for transparency
- Status transitions: active → approved/rejected/superseded

---

### 10. AIInteraction

**Purpose**: Audit trail for AI assistant interactions including voice queries.

**Table**: `ai_interactions`

**Columns**:
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `tenant_id` UUID NOT NULL
- `user_id` UUID NOT NULL (FK to users)
- `interaction_type` VARCHAR(20) NOT NULL ('voice', 'text')
- `query_text` TEXT NOT NULL (transcribed or typed query)
- `query_audio_url` VARCHAR(500) (S3/object storage URL for voice audio, if applicable)
- `intent` VARCHAR(100) (detected intent: 'stock_query', 'low_stock_alert', 'forecast_query', 'po_creation', etc.)
- `response_text` TEXT NOT NULL
- `response_audio_url` VARCHAR(500) (TTS audio URL, if applicable)
- `processing_duration_ms` INTEGER (milliseconds to process query)
- `confidence_score` DECIMAL(5,2) (NLP confidence, 0-100)
- `entities_json` JSONB (extracted entities: product names, warehouse names, quantities)
- `created_at` TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()

**Constraints**:
- CHECK (interaction_type IN ('voice', 'text'))
- CHECK (processing_duration_ms >= 0)

**Indexes**:
- idx_ai_interactions_tenant_id
- idx_ai_interactions_user_id
- idx_ai_interactions_intent
- idx_ai_interactions_created_at

**Relationships**:
- Belongs to: User
- References: Product, Warehouse (via entities_json)

**Validation Rules**:
- Query text and response text required
- Processing duration tracked for performance monitoring

---

## Supporting Tables

### 11. AuditLog

**Purpose**: Comprehensive audit trail for all critical operations.

**Table**: `audit_logs`

**Columns**:
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
- `tenant_id` UUID NOT NULL
- `user_id` UUID (FK to users, NULL for system actions)
- `action` VARCHAR(100) NOT NULL (e.g., 'inventory.movement.create', 'purchase_order.approve')
- `entity_type` VARCHAR(50) NOT NULL (e.g., 'InventoryMovement', 'PurchaseOrder')
- `entity_id` UUID NOT NULL
- `changes_json` JSONB (before/after values for updates)
- `ip_address` INET
- `user_agent` TEXT
- `created_at` TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()

**Indexes**:
- idx_audit_logs_tenant_id
- idx_audit_logs_user_id
- idx_audit_logs_entity (entity_type, entity_id)
- idx_audit_logs_action
- idx_audit_logs_created_at

**Partitioning**: Consider partitioning by `created_at` (e.g., monthly) for large datasets.

---

## Database Migrations

### Migration 001: Initial Schema

1. Enable UUID extension: `CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`
2. Enable Row-Level Security: `ALTER DATABASE <dbname> SET row_security = on;`
3. Create all tables with columns, constraints, indexes
4. Create RLS policies for tenant isolation
5. Create functions for updated_at triggers
6. Create views for common queries (e.g., low_stock_alerts)

### Migration 002: Add Optimistic Locking

1. Add `version` column to `inventory` table
2. Create trigger to auto-increment version on update

### Migration 003: Add Partitioning (if needed)

1. Partition `inventory_movements` by `performed_at` (monthly)
2. Partition `audit_logs` by `created_at` (monthly)

## Validation Rules Summary

- All tenant_id columns required, enforced by RLS
- SKU unique per tenant
- Warehouse name unique per tenant
- Purchase order number unique per tenant
- Inventory quantity >= 0 (unless tenant allows negative)
- All movement quantities > 0
- All costs >= 0
- Forecast horizons: 7, 30, or 90 days
- Status values from predefined enums
- Optimistic locking on inventory for concurrent updates

