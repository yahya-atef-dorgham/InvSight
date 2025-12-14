export interface Inventory {
  id: string;
  product_id: string;
  product_sku: string;
  product_name: string;
  warehouse_id: string;
  warehouse_name: string;
  quantity: number;
  reserved_quantity: number;
  available_quantity: number;
  minimum_stock: number | null;
  safety_stock: number | null;
  is_low_stock: boolean;
  unit_of_measure: string;
  last_movement_at: string | null;
}

export interface InventoryUpdate {
  type: 'inventory_update';
  data: Inventory;
  timestamp: number;
}
