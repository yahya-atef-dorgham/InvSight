import React from 'react';
import { Inventory } from '../../types/inventory';
import StockLevelIndicator from './StockLevelIndicator';
import './InventoryList.css';

interface InventoryListProps {
  items: Inventory[];
  isLoading?: boolean;
}

const InventoryList: React.FC<InventoryListProps> = ({ items, isLoading }) => {
  if (isLoading) {
    return (
      <div className="inventory-list-loading">
        <div className="loading-spinner">Loading inventory...</div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="inventory-list-empty">
        <p>No inventory items found.</p>
      </div>
    );
  }

  return (
    <div className="inventory-list">
      <table className="inventory-table">
        <thead>
          <tr>
            <th>Product SKU</th>
            <th>Product Name</th>
            <th>Warehouse</th>
            <th>Quantity</th>
            <th>Available</th>
            <th>Status</th>
            <th>Last Movement</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id} className={item.is_low_stock ? 'low-stock' : ''}>
              <td>{item.product_sku}</td>
              <td>{item.product_name}</td>
              <td>{item.warehouse_name}</td>
              <td>
                {item.quantity.toLocaleString()} {item.unit_of_measure}
              </td>
              <td>
                {item.available_quantity.toLocaleString()} {item.unit_of_measure}
              </td>
              <td>
                <StockLevelIndicator
                  quantity={item.quantity}
                  minimumStock={item.minimum_stock}
                  isLowStock={item.is_low_stock}
                />
              </td>
              <td>
                {item.last_movement_at
                  ? new Date(item.last_movement_at).toLocaleString()
                  : 'Never'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default InventoryList;
