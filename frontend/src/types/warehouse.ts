export interface Warehouse {
  id: string;
  tenant_id: string;
  name: string;
  address: string | null;
  city: string | null;
  state: string | null;
  country: string | null;
  postal_code: string | null;
  capacity_total: number | null;
  capacity_unit: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface WarehouseCreate {
  name: string;
  address?: string | null;
  city?: string | null;
  state?: string | null;
  country?: string | null;
  postal_code?: string | null;
  capacity_total?: number | null;
  capacity_unit?: string | null;
  is_active?: boolean;
}

export interface WarehouseUpdate {
  name?: string | null;
  address?: string | null;
  city?: string | null;
  state?: string | null;
  country?: string | null;
  postal_code?: string | null;
  capacity_total?: number | null;
  capacity_unit?: string | null;
  is_active?: boolean | null;
}
