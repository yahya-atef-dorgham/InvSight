export interface Product {
  id: string;
  tenant_id: string;
  sku: string;
  name: string;
  description: string | null;
  category: string | null;
  unit_of_measure: string;
  created_at: string;
  updated_at: string;
}

export interface ProductCreate {
  sku: string;
  name: string;
  description?: string | null;
  category?: string | null;
  unit_of_measure: string;
}

export interface ProductUpdate {
  name?: string | null;
  description?: string | null;
  category?: string | null;
  unit_of_measure?: string | null;
}
