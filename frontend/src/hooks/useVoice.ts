import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../services/api';
import { VoiceQuery, VoiceQueryResponse, AIInteraction } from '../types/voice';

export interface InteractionFilters {
  user_id?: string;
  intent?: string;
  skip?: number;
  limit?: number;
}

export const useVoiceQuery = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (query: VoiceQuery) => {
      const response = await apiClient.post<VoiceQueryResponse>('/ai/voice/query', query);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-interactions'] });
    },
  });
};

export const useInteractionHistory = (filters: InteractionFilters = {}) => {
  return useQuery<AIInteraction[]>({
    queryKey: ['ai-interactions', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.user_id) params.append('user_id', filters.user_id);
      if (filters.intent) params.append('intent', filters.intent);
      if (filters.skip !== undefined) params.append('skip', filters.skip.toString());
      if (filters.limit !== undefined) params.append('limit', filters.limit.toString());

      const response = await apiClient.get<AIInteraction[]>(`/ai/interactions?${params.toString()}`);
      return response.data;
    },
  });
};
