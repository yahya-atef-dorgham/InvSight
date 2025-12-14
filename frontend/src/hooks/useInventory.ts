import { useQuery } from '@tanstack/react-query';
import apiClient from '../services/api';
import { Inventory } from '../types/inventory';

export interface InventoryFilters {
  warehouse_id?: string;
  low_stock?: boolean;
  skip?: number;
  limit?: number;
}

export const useInventory = (filters: InventoryFilters = {}) => {
  return useQuery<Inventory[]>({
    queryKey: ['inventory', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.warehouse_id) params.append('warehouse_id', filters.warehouse_id);
      if (filters.low_stock) params.append('low_stock', 'true');
      if (filters.skip !== undefined) params.append('skip', filters.skip.toString());
      if (filters.limit !== undefined) params.append('limit', filters.limit.toString());

      const response = await apiClient.get<Inventory[]>(`/inventory?${params.toString()}`);
      return response.data;
    },
    refetchInterval: 30000, // Refetch every 30 seconds as fallback
  });
};

export const useLowStockInventory = (warehouse_id?: string) => {
  return useQuery<Inventory[]>({
    queryKey: ['inventory', 'low-stock', warehouse_id],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (warehouse_id) params.append('warehouse_id', warehouse_id);

      const response = await apiClient.get<Inventory[]>(`/inventory/low-stock?${params.toString()}`);
      return response.data;
    },
    refetchInterval: 30000,
  });
};
