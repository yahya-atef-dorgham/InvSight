import { useQuery } from '@tanstack/react-query';
import apiClient from '../services/api';
import { Product } from '../types/product';

export const useProducts = () => {
  return useQuery<Product[]>({
    queryKey: ['products'],
    queryFn: async () => {
      const response = await apiClient.get<Product[]>('/products');
      return response.data;
    },
  });
};
