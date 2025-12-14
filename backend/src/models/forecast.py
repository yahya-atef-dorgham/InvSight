"""
Forecast model representing AI-generated demand predictions.
"""
from sqlalchemy import Column, Integer, Date, Numeric, String, DateTime, ForeignKey, UniqueConstraint, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import func

from src.models.base import BaseModel


class Forecast(BaseModel):
    """Forecast entity representing AI-generated demand predictions."""
    
    __tablename__ = "forecasts"
    
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False, index=True)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey('warehouses.id'), nullable=False, index=True)
    forecast_horizon_days = Column(Integer, nullable=False)  # 7, 30, or 90
    forecast_date = Column(Date, nullable=False, index=True)
    predicted_demand = Column(Numeric(15, 3), nullable=False)
    confidence_lower = Column(Numeric(15, 3), nullable=True)
    confidence_upper = Column(Numeric(15, 3), nullable=True)
    confidence_level = Column(Numeric(5, 2), nullable=True)  # e.g., 0.80 for 80%
    model_version = Column(String(50), nullable=False, index=True)
    model_type = Column(String(50), nullable=True)  # e.g., 'arima', 'exponential_smoothing', 'lstm'
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    features_json = Column(JSONB, nullable=True)  # Model input features for explainability
    
    # Relationships
    product = relationship("Product", backref="forecasts")
    warehouse = relationship("Warehouse", backref="forecasts")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint(
            'tenant_id', 'product_id', 'warehouse_id', 'forecast_horizon_days', 'forecast_date',
            name='uq_forecasts_unique'
        ),
        Index('idx_forecasts_product_warehouse', 'product_id', 'warehouse_id'),
        Index('idx_forecasts_horizon_date', 'forecast_horizon_days', 'forecast_date'),
        Index('idx_forecasts_model_version', 'model_version'),
        CheckConstraint('forecast_horizon_days IN (7, 30, 90)', name='ck_forecast_horizon'),
        CheckConstraint('predicted_demand >= 0', name='ck_forecast_demand_non_negative'),
    )
    
    def __repr__(self):
        return f"<Forecast(id={self.id}, product_id={self.product_id}, horizon={self.forecast_horizon_days}d, demand={self.predicted_demand})>"
