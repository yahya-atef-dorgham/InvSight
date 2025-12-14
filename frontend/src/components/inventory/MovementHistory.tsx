import React from 'react';
import { InventoryMovement } from '../../types/inventory_movement';
import './MovementHistory.css';

interface MovementHistoryProps {
  movements: InventoryMovement[];
  isLoading?: boolean;
}

const MovementHistory: React.FC<MovementHistoryProps> = ({ movements, isLoading }) => {
  if (isLoading) {
    return (
      <div className="movement-history-loading">
        <div className="loading-spinner">Loading movement history...</div>
      </div>
    );
  }

  if (movements.length === 0) {
    return (
      <div className="movement-history-empty">
        <p>No movement history found.</p>
      </div>
    );
  }

  const getMovementTypeLabel = (type: string) => {
    switch (type) {
      case 'inbound':
        return 'Inbound';
      case 'outbound':
        return 'Outbound';
      case 'transfer':
        return 'Transfer';
      default:
        return type;
    }
  };

  const getMovementTypeClass = (type: string) => {
    switch (type) {
      case 'inbound':
        return 'type-inbound';
      case 'outbound':
        return 'type-outbound';
      case 'transfer':
        return 'type-transfer';
      default:
        return '';
    }
  };

  return (
    <div className="movement-history">
      <table className="movement-table">
        <thead>
          <tr>
            <th>Date/Time</th>
            <th>Type</th>
            <th>Product</th>
            <th>From</th>
            <th>To</th>
            <th>Quantity</th>
            <th>Reference</th>
            <th>Performed By</th>
          </tr>
        </thead>
        <tbody>
          {movements.map((movement) => (
            <tr key={movement.id}>
              <td>{new Date(movement.performed_at).toLocaleString()}</td>
              <td>
                <span className={`movement-type-badge ${getMovementTypeClass(movement.movement_type)}`}>
                  {getMovementTypeLabel(movement.movement_type)}
                </span>
              </td>
              <td>{movement.product_id.substring(0, 8)}...</td>
              <td>{movement.source_warehouse_id ? movement.source_warehouse_id.substring(0, 8) + '...' : '-'}</td>
              <td>{movement.destination_warehouse_id ? movement.destination_warehouse_id.substring(0, 8) + '...' : '-'}</td>
              <td>{movement.quantity.toLocaleString()}</td>
              <td>{movement.reference_number || '-'}</td>
              <td>{movement.performed_by.substring(0, 8)}...</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default MovementHistory;
