export type PurchaseOrderStatus = 'draft' | 'approved' | 'sent' | 'partially_received' | 'received' | 'cancelled';

export interface PurchaseOrderItem {
  id: string;
  purchase_order_id: string;
  product_id: string;
  warehouse_id: string | null;
  quantity: number;
  unit_cost: number;
  total_cost: number;
  received_quantity: number;
  line_number: number;
}

export interface PurchaseOrder {
  id: string;
  tenant_id: string;
  order_number: string;
  supplier_id: string;
  status: PurchaseOrderStatus;
  total_amount: number | null;
  currency: string;
  expected_delivery_date: string | null;
  actual_delivery_date: string | null;
  created_by: string;
  created_at: string;
  approved_by: string | null;
  approved_at: string | null;
  sent_at: string | null;
  received_at: string | null;
  cancelled_at: string | null;
  cancelled_by: string | null;
  cancellation_reason: string | null;
  ai_recommendation_id: string | null;
  notes: string | null;
  items: PurchaseOrderItem[];
}

export interface PurchaseOrderItemCreate {
  product_id: string;
  warehouse_id?: string | null;
  quantity: number;
  unit_cost: number;
}

export interface PurchaseOrderCreate {
  supplier_id: string;
  items: PurchaseOrderItemCreate[];
  order_number?: string | null;
  expected_delivery_date?: string | null;
  notes?: string | null;
}

export interface PurchaseOrderReceive {
  received_items: Record<string, number>;  // item_id -> received_quantity
}
