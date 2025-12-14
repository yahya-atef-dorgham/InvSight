export type MovementType = 'inbound' | 'outbound' | 'transfer';

export interface InventoryMovement {
  id: string;
  tenant_id: string;
  movement_type: MovementType;
  product_id: string;
  source_warehouse_id: string | null;
  destination_warehouse_id: string | null;
  quantity: number;
  quantity_before: number | null;
  quantity_after: number | null;
  reference_number: string | null;
  notes: string | null;
  performed_by: string;
  performed_at: string;
  approved_by: string | null;
  approved_at: string | null;
}

export interface MovementCreate {
  movement_type: MovementType;
  product_id: string;
  source_warehouse_id?: string | null;
  destination_warehouse_id?: string | null;
  quantity: number;
  reference_number?: string | null;
  notes?: string | null;
  expected_version?: number | null;
}
