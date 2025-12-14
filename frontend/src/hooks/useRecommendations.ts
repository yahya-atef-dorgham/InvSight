import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../services/api';
import { Recommendation, RecommendationCreate, RecommendationExplanation } from '../types/recommendation';

export interface RecommendationFilters {
  product_id?: string;
  warehouse_id?: string;
  recommendation_type?: 'reorder_point' | 'reorder_quantity' | 'purchase_order';
  status?: 'active' | 'approved' | 'rejected' | 'superseded';
  urgency_min?: number;
  skip?: number;
  limit?: number;
}

export const useRecommendations = (filters: RecommendationFilters = {}) => {
  return useQuery<Recommendation[]>({
    queryKey: ['recommendations', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.product_id) params.append('product_id', filters.product_id);
      if (filters.warehouse_id) params.append('warehouse_id', filters.warehouse_id);
      if (filters.recommendation_type) params.append('recommendation_type', filters.recommendation_type);
      if (filters.status) params.append('status', filters.status);
      if (filters.urgency_min !== undefined) params.append('urgency_min', filters.urgency_min.toString());
      if (filters.skip !== undefined) params.append('skip', filters.skip.toString());
      if (filters.limit !== undefined) params.append('limit', filters.limit.toString());

      const response = await apiClient.get<Recommendation[]>(`/recommendations?${params.toString()}`);
      return response.data;
    },
  });
};

export const useRecommendation = (id: string) => {
  return useQuery<Recommendation>({
    queryKey: ['recommendations', id],
    queryFn: async () => {
      const response = await apiClient.get<Recommendation>(`/recommendations/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useRecommendationExplanation = (id: string) => {
  return useQuery<RecommendationExplanation>({
    queryKey: ['recommendations', id, 'explanation'],
    queryFn: async () => {
      const response = await apiClient.get<RecommendationExplanation>(`/recommendations/${id}/explanation`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateRecommendation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (recommendation: RecommendationCreate) => {
      const response = await apiClient.post<Recommendation>('/recommendations', recommendation);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
    },
  });
};

export const useUpdateRecommendationStatus = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, status }: { id: string; status: string }) => {
      const response = await apiClient.put<Recommendation>(`/recommendations/${id}/status`, { status });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
    },
  });
};
