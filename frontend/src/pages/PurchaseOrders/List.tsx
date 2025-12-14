import React, { useState } from 'react';
import { usePurchaseOrders } from '../../hooks/usePurchaseOrders';
import PurchaseOrderList from '../../components/purchase-orders/PurchaseOrderList';
import PurchaseOrderDetail from '../../components/purchase-orders/PurchaseOrderDetail';
import { PurchaseOrder } from '../../types/purchase_order';
import './List.css';

const PurchaseOrdersList: React.FC = () => {
  const [selectedPO, setSelectedPO] = useState<PurchaseOrder | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('');

  const { data: purchaseOrders, isLoading } = usePurchaseOrders({
    status: statusFilter as any,
  });

  return (
    <div className="purchase-orders-page">
      <div className="page-header">
        <h1>Purchase Orders</h1>
      </div>

      <div className="page-filters">
        <div className="filter-group">
          <label htmlFor="status-filter">Filter by Status:</label>
          <select
            id="status-filter"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">All Statuses</option>
            <option value="draft">Draft</option>
            <option value="approved">Approved</option>
            <option value="sent">Sent</option>
            <option value="partially_received">Partially Received</option>
            <option value="received">Received</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      {selectedPO ? (
        <div className="detail-view">
          <PurchaseOrderDetail
            purchaseOrder={selectedPO}
            onClose={() => setSelectedPO(null)}
          />
        </div>
      ) : (
        <PurchaseOrderList
          purchaseOrders={purchaseOrders || []}
          isLoading={isLoading}
          onPOClick={setSelectedPO}
        />
      )}
    </div>
  );
};

export default PurchaseOrdersList;
