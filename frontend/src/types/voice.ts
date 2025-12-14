export type InteractionType = 'voice' | 'text';

export interface VoiceQuery {
  query_text: string;
  interaction_type: InteractionType;
  language?: string;
}

export interface VoiceQueryResponse {
  id: string;
  query_text: string;
  intent: string | null;
  response_text: string;
  response_audio_url: string | null;
  confidence_score: number | null;
  processing_duration_ms: number | null;
  entities_json: Record<string, any> | null;
  created_at: string;
}

export interface AIInteraction {
  id: string;
  tenant_id: string;
  user_id: string;
  interaction_type: InteractionType;
  query_text: string;
  intent: string | null;
  response_text: string;
  confidence_score: number | null;
  created_at: string;
}
