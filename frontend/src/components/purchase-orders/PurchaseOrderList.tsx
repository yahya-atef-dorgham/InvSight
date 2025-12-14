import React from 'react';
import { PurchaseOrder } from '../../types/purchase_order';
import './PurchaseOrderList.css';

interface PurchaseOrderListProps {
  purchaseOrders: PurchaseOrder[];
  isLoading?: boolean;
  onPOClick?: (po: PurchaseOrder) => void;
}

const PurchaseOrderList: React.FC<PurchaseOrderListProps> = ({
  purchaseOrders,
  isLoading,
  onPOClick,
}) => {
  if (isLoading) {
    return (
      <div className="po-list-loading">
        <div className="loading-spinner">Loading purchase orders...</div>
      </div>
    );
  }

  if (purchaseOrders.length === 0) {
    return (
      <div className="po-list-empty">
        <p>No purchase orders found.</p>
      </div>
    );
  }

  const getStatusClass = (status: string) => {
    switch (status) {
      case 'draft':
        return 'status-draft';
      case 'approved':
        return 'status-approved';
      case 'sent':
        return 'status-sent';
      case 'partially_received':
        return 'status-partial';
      case 'received':
        return 'status-received';
      case 'cancelled':
        return 'status-cancelled';
      default:
        return '';
    }
  };

  return (
    <div className="po-list">
      <table className="po-table">
        <thead>
          <tr>
            <th>Order Number</th>
            <th>Supplier</th>
            <th>Status</th>
            <th>Total Amount</th>
            <th>Expected Delivery</th>
            <th>Created</th>
            <th>Items</th>
          </tr>
        </thead>
        <tbody>
          {purchaseOrders.map((po) => (
            <tr
              key={po.id}
              onClick={() => onPOClick?.(po)}
              className="po-row"
            >
              <td>{po.order_number}</td>
              <td>{po.supplier_id.substring(0, 8)}...</td>
              <td>
                <span className={`status-badge ${getStatusClass(po.status)}`}>
                  {po.status.replace('_', ' ').toUpperCase()}
                </span>
              </td>
              <td>
                {po.total_amount
                  ? `${po.currency} ${po.total_amount.toLocaleString()}`
                  : 'N/A'}
              </td>
              <td>
                {po.expected_delivery_date
                  ? new Date(po.expected_delivery_date).toLocaleDateString()
                  : '-'}
              </td>
              <td>{new Date(po.created_at).toLocaleDateString()}</td>
              <td>{po.items?.length || 0}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default PurchaseOrderList;
