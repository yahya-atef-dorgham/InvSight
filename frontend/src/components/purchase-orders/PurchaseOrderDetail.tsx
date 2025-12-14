import React, { useState } from 'react';
import { PurchaseOrder } from '../../types/purchase_order';
import { useApprovePurchaseOrder, useReceivePurchaseOrder } from '../../hooks/usePurchaseOrders';
import { useToast } from '../common/Toast';
import './PurchaseOrderDetail.css';

interface PurchaseOrderDetailProps {
  purchaseOrder: PurchaseOrder;
  onClose?: () => void;
}

const PurchaseOrderDetail: React.FC<PurchaseOrderDetailProps> = ({
  purchaseOrder,
  onClose,
}) => {
  const [showReceiveForm, setShowReceiveForm] = useState(false);
  const [receivedItems, setReceivedItems] = useState<Record<string, number>>({});
  
  const approvePO = useApprovePurchaseOrder();
  const receivePO = useReceivePurchaseOrder();
  const { showToast } = useToast();

  const handleApprove = async () => {
    try {
      await approvePO.mutateAsync(purchaseOrder.id);
      showToast('Purchase order approved successfully', 'success');
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || 'Failed to approve purchase order',
        'error'
      );
    }
  };

  const handleReceive = async () => {
    try {
      await receivePO.mutateAsync({
        id: purchaseOrder.id,
        received_items: receivedItems,
      });
      showToast('Purchase order items received and inventory updated', 'success');
      setShowReceiveForm(false);
      setReceivedItems({});
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || 'Failed to receive purchase order',
        'error'
      );
    }
  };

  const canApprove = purchaseOrder.status === 'draft';
  const canReceive = purchaseOrder.status === 'sent' || purchaseOrder.status === 'partially_received';

  return (
    <div className="po-detail">
      <div className="detail-header">
        <h2>Purchase Order: {purchaseOrder.order_number}</h2>
        {onClose && (
          <button onClick={onClose} className="close-button">
            ×
          </button>
        )}
      </div>

      <div className="detail-content">
        <div className="detail-section">
          <h3>Order Information</h3>
          <div className="detail-grid">
            <div className="detail-item">
              <span className="detail-label">Status:</span>
              <span className={`detail-value status-${purchaseOrder.status}`}>
                {purchaseOrder.status.replace('_', ' ').toUpperCase()}
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Total Amount:</span>
              <span className="detail-value">
                {purchaseOrder.total_amount
                  ? `${purchaseOrder.currency} ${purchaseOrder.total_amount.toLocaleString()}`
                  : 'N/A'}
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Expected Delivery:</span>
              <span className="detail-value">
                {purchaseOrder.expected_delivery_date
                  ? new Date(purchaseOrder.expected_delivery_date).toLocaleDateString()
                  : '-'}
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Created:</span>
              <span className="detail-value">
                {new Date(purchaseOrder.created_at).toLocaleString()}
              </span>
            </div>
          </div>
        </div>

        <div className="detail-section">
          <h3>Items</h3>
          <table className="items-table">
            <thead>
              <tr>
                <th>Product</th>
                <th>Warehouse</th>
                <th>Quantity</th>
                <th>Unit Cost</th>
                <th>Total Cost</th>
                <th>Received</th>
              </tr>
            </thead>
            <tbody>
              {purchaseOrder.items?.map((item) => (
                <tr key={item.id}>
                  <td>{item.product_id.substring(0, 8)}...</td>
                  <td>{item.warehouse_id ? item.warehouse_id.substring(0, 8) + '...' : '-'}</td>
                  <td>{item.quantity.toLocaleString()}</td>
                  <td>{item.unit_cost.toLocaleString()}</td>
                  <td>{item.total_cost.toLocaleString()}</td>
                  <td>
                    {showReceiveForm && canReceive ? (
                      <input
                        type="number"
                        min="0"
                        max={item.quantity}
                        step="0.001"
                        value={receivedItems[item.id] || 0}
                        onChange={(e) =>
                          setReceivedItems({
                            ...receivedItems,
                            [item.id]: parseFloat(e.target.value) || 0,
                          })
                        }
                        className="receive-input"
                      />
                    ) : (
                      `${item.received_quantity.toLocaleString()} / ${item.quantity.toLocaleString()}`
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {purchaseOrder.notes && (
          <div className="detail-section">
            <h3>Notes</h3>
            <p className="notes-text">{purchaseOrder.notes}</p>
          </div>
        )}

        <div className="detail-actions">
          {canApprove && (
            <button
              onClick={handleApprove}
              disabled={approvePO.isPending}
              className="action-button approve-button"
            >
              {approvePO.isPending ? 'Approving...' : 'Approve Purchase Order'}
            </button>
          )}

          {canReceive && !showReceiveForm && (
            <button
              onClick={() => setShowReceiveForm(true)}
              className="action-button receive-button"
            >
              Receive Items
            </button>
          )}

          {showReceiveForm && (
            <div className="receive-form">
              <button
                onClick={handleReceive}
                disabled={receivePO.isPending}
                className="action-button receive-button"
              >
                {receivePO.isPending ? 'Receiving...' : 'Confirm Receive'}
              </button>
              <button
                onClick={() => {
                  setShowReceiveForm(false);
                  setReceivedItems({});
                }}
                className="action-button cancel-button"
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PurchaseOrderDetail;
