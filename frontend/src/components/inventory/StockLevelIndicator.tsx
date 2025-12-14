import React from 'react';
import './StockLevelIndicator.css';

interface StockLevelIndicatorProps {
  quantity: number;
  minimumStock: number | null;
  isLowStock: boolean;
}

const StockLevelIndicator: React.FC<StockLevelIndicatorProps> = ({
  quantity,
  minimumStock,
  isLowStock,
}) => {
  const getStatusClass = () => {
    if (isLowStock) return 'status-low';
    if (minimumStock && quantity < minimumStock * 1.5) return 'status-warning';
    return 'status-ok';
  };

  const getStatusText = () => {
    if (isLowStock) return 'Low Stock';
    if (minimumStock && quantity < minimumStock * 1.5) return 'Warning';
    return 'OK';
  };

  return (
    <div className={`stock-indicator ${getStatusClass()}`}>
      <span className="status-dot"></span>
      <span className="status-text">{getStatusText()}</span>
    </div>
  );
};

export default StockLevelIndicator;
