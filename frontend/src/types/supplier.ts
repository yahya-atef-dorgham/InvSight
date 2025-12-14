export interface Supplier {
  id: string;
  tenant_id: string;
  name: string;
  contact_email: string | null;
  contact_phone: string | null;
  address: string | null;
  city: string | null;
  state: string | null;
  country: string | null;
  postal_code: string | null;
  payment_terms: string | null;
  tax_id: string | null;
  is_active: boolean;
  performance_score: number | null;
  created_at: string;
  updated_at: string;
}

export interface SupplierCreate {
  name: string;
  contact_email?: string | null;
  contact_phone?: string | null;
  address?: string | null;
  city?: string | null;
  state?: string | null;
  country?: string | null;
  postal_code?: string | null;
  payment_terms?: string | null;
  tax_id?: string | null;
  is_active?: boolean;
}
