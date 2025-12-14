import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../services/api';
import { PurchaseOrder, PurchaseOrderCreate, PurchaseOrderReceive } from '../types/purchase_order';

export interface PurchaseOrderFilters {
  supplier_id?: string;
  status?: 'draft' | 'approved' | 'sent' | 'partially_received' | 'received' | 'cancelled';
  skip?: number;
  limit?: number;
}

export const usePurchaseOrders = (filters: PurchaseOrderFilters = {}) => {
  return useQuery<PurchaseOrder[]>({
    queryKey: ['purchase-orders', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.supplier_id) params.append('supplier_id', filters.supplier_id);
      if (filters.status) params.append('status', filters.status);
      if (filters.skip !== undefined) params.append('skip', filters.skip.toString());
      if (filters.limit !== undefined) params.append('limit', filters.limit.toString());

      const response = await apiClient.get<PurchaseOrder[]>(`/purchase-orders?${params.toString()}`);
      return response.data;
    },
  });
};

export const usePurchaseOrder = (id: string) => {
  return useQuery<PurchaseOrder>({
    queryKey: ['purchase-orders', id],
    queryFn: async () => {
      const response = await apiClient.get<PurchaseOrder>(`/purchase-orders/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreatePurchaseOrder = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (po: PurchaseOrderCreate) => {
      const response = await apiClient.post<PurchaseOrder>('/purchase-orders', po);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
    },
  });
};

export const useCreatePOFromRecommendation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ recommendation_id, supplier_id, order_number }: { recommendation_id: string; supplier_id: string; order_number?: string }) => {
      const response = await apiClient.post<PurchaseOrder>(
        `/purchase-orders/from-recommendation/${recommendation_id}`,
        { supplier_id, order_number }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
    },
  });
};

export const useApprovePurchaseOrder = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.post<PurchaseOrder>(`/purchase-orders/${id}/approve`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
    },
  });
};

export const useReceivePurchaseOrder = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, received_items }: { id: string; received_items: Record<string, number> }) => {
      const response = await apiClient.post<PurchaseOrder>(`/purchase-orders/${id}/receive`, { received_items });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
    },
  });
};
