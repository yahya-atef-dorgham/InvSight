export interface Forecast {
  id: string;
  tenant_id: string;
  product_id: string;
  warehouse_id: string;
  forecast_horizon_days: number;
  forecast_date: string;
  predicted_demand: number;
  confidence_lower: number | null;
  confidence_upper: number | null;
  confidence_level: number | null;
  model_version: string;
  model_type: string | null;
  generated_at: string;
}

export interface ForecastCreate {
  product_id: string;
  warehouse_id: string;
  forecast_horizon_days: number;
  model_type?: string;
}
