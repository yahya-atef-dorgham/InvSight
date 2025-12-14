import { useQuery } from '@tanstack/react-query';
import apiClient from '../services/api';
import { Warehouse } from '../types/warehouse';

export const useWarehouses = (activeOnly: boolean = false) => {
  return useQuery<Warehouse[]>({
    queryKey: ['warehouses', activeOnly],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (activeOnly) params.append('active_only', 'true');
      
      const response = await apiClient.get<Warehouse[]>(`/warehouses?${params.toString()}`);
      return response.data;
    },
  });
};
