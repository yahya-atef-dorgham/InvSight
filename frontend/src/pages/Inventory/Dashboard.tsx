import React, { useState, useEffect, useCallback } from 'react';
import { useInventory } from '../../hooks/useInventory';
import { useWarehouses } from '../../hooks/useWarehouses';
import { useAuth } from '../../contexts/AuthContext';
import { WebSocketClient } from '../../services/websocket';
import { Inventory } from '../../types/inventory';
import InventoryList from '../../components/inventory/InventoryList';
import WarehouseFilter from '../../components/inventory/WarehouseFilter';
import { useToast } from '../../components/common/Toast';
import './Dashboard.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const Dashboard: React.FC = () => {
  const [selectedWarehouseId, setSelectedWarehouseId] = useState<string | null>(null);
  const [lowStockOnly, setLowStockOnly] = useState(false);
  const [inventoryData, setInventoryData] = useState<Inventory[]>([]);
  const [wsClient, setWsClient] = useState<WebSocketClient | null>(null);
  
  const { user } = useAuth();
  const { showToast } = useToast();
  
  const { data: warehouses, isLoading: warehousesLoading } = useWarehouses(true);
  const { data: inventory, isLoading: inventoryLoading, refetch } = useInventory({
    warehouse_id: selectedWarehouseId || undefined,
    low_stock: lowStockOnly,
  });

  // Initialize inventory data
  useEffect(() => {
    if (inventory) {
      setInventoryData(inventory);
    }
  }, [inventory]);

  // Setup WebSocket connection
  useEffect(() => {
    if (!user) return;

    const token = localStorage.getItem('auth_token');
    if (!token) return;

    const client = new WebSocketClient(API_BASE_URL, token);
    
    client.on('inventory_update', (update: Inventory) => {
      setInventoryData((prev) => {
        const index = prev.findIndex((item) => item.id === update.id);
        if (index >= 0) {
          // Update existing item
          const updated = [...prev];
          updated[index] = update;
          return updated;
        } else {
          // Add new item
          return [...prev, update];
        }
      });
      
      // Show toast notification for low stock items
      if (update.is_low_stock) {
        showToast(
          `Low stock alert: ${update.product_name} at ${update.warehouse_name}`,
          'warning'
        );
      }
    });

    client.connect().catch((error) => {
      console.error('Failed to connect WebSocket:', error);
      showToast('Real-time updates unavailable', 'warning');
    });

    setWsClient(client);

    return () => {
      client.disconnect();
    };
  }, [user, showToast]);

  const handleWarehouseChange = useCallback((warehouseId: string | null) => {
    setSelectedWarehouseId(warehouseId);
  }, []);

  const handleLowStockToggle = useCallback(() => {
    setLowStockOnly((prev) => !prev);
  }, []);

  return (
    <div className="inventory-dashboard">
      <div className="dashboard-header">
        <h1>Inventory Dashboard</h1>
        <div className="dashboard-actions">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={lowStockOnly}
              onChange={handleLowStockToggle}
            />
            Show Low Stock Only
          </label>
        </div>
      </div>

      {warehouses && (
        <WarehouseFilter
          warehouses={warehouses}
          selectedWarehouseId={selectedWarehouseId}
          onWarehouseChange={handleWarehouseChange}
        />
      )}

      <div className="dashboard-stats">
        <div className="stat-card">
          <div className="stat-label">Total Items</div>
          <div className="stat-value">{inventoryData.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Low Stock Items</div>
          <div className="stat-value warning">
            {inventoryData.filter((item) => item.is_low_stock).length}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Warehouses</div>
          <div className="stat-value">{warehouses?.length || 0}</div>
        </div>
      </div>

      <InventoryList items={inventoryData} isLoading={inventoryLoading || warehousesLoading} />
    </div>
  );
};

export default Dashboard;
