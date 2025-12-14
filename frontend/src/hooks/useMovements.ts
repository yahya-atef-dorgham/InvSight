import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../services/api';
import { InventoryMovement, MovementCreate } from '../types/inventory_movement';

export interface MovementFilters {
  product_id?: string;
  warehouse_id?: string;
  movement_type?: 'inbound' | 'outbound' | 'transfer';
  skip?: number;
  limit?: number;
}

export const useMovements = (filters: MovementFilters = {}) => {
  return useQuery<InventoryMovement[]>({
    queryKey: ['movements', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.product_id) params.append('product_id', filters.product_id);
      if (filters.warehouse_id) params.append('warehouse_id', filters.warehouse_id);
      if (filters.movement_type) params.append('movement_type', filters.movement_type);
      if (filters.skip !== undefined) params.append('skip', filters.skip.toString());
      if (filters.limit !== undefined) params.append('limit', filters.limit.toString());

      const response = await apiClient.get<InventoryMovement[]>(`/inventory/movements?${params.toString()}`);
      return response.data;
    },
  });
};

export const useCreateMovement = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (movement: MovementCreate) => {
      const response = await apiClient.post<InventoryMovement>('/inventory/movement', movement);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['movements'] });
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
    },
  });
};
