import React from 'react';
import { Warehouse } from '../../types/warehouse';
import './WarehouseFilter.css';

interface WarehouseFilterProps {
  warehouses: Warehouse[];
  selectedWarehouseId: string | null;
  onWarehouseChange: (warehouseId: string | null) => void;
}

const WarehouseFilter: React.FC<WarehouseFilterProps> = ({
  warehouses,
  selectedWarehouseId,
  onWarehouseChange,
}) => {
  return (
    <div className="warehouse-filter">
      <label htmlFor="warehouse-filter" className="filter-label">
        Filter by Warehouse:
      </label>
      <select
        id="warehouse-filter"
        value={selectedWarehouseId || ''}
        onChange={(e) => onWarehouseChange(e.target.value || null)}
        className="filter-select"
      >
        <option value="">All Warehouses</option>
        {warehouses
          .filter((w) => w.is_active)
          .map((warehouse) => (
            <option key={warehouse.id} value={warehouse.id}>
              {warehouse.name}
            </option>
          ))}
      </select>
    </div>
  );
};

export default WarehouseFilter;
