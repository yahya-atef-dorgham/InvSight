export type RecommendationType = 'reorder_point' | 'reorder_quantity' | 'purchase_order';
export type RecommendationStatus = 'active' | 'approved' | 'rejected' | 'superseded';

export interface Recommendation {
  id: string;
  tenant_id: string;
  recommendation_type: RecommendationType;
  product_id: string;
  warehouse_id: string;
  forecast_id: string | null;
  recommended_value: number | null;
  current_value: number | null;
  urgency_score: number | null;
  confidence_score: number | null;
  explanation: string | null;
  explanation_json: Record<string, any> | null;
  status: RecommendationStatus;
  created_at: string;
  actioned_at: string | null;
  actioned_by: string | null;
}

export interface RecommendationCreate {
  recommendation_type: RecommendationType;
  product_id: string;
  warehouse_id: string;
  forecast_id?: string | null;
}

export interface RecommendationExplanation {
  explanation: string;
  explanation_json: Record<string, any>;
  urgency_score: number | null;
  confidence_score: number | null;
  recommended_value: number | null;
  current_value: number | null;
}
