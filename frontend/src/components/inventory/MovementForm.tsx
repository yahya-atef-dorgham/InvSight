import React, { useState, useEffect } from 'react';
import { useCreateMovement } from '../../hooks/useMovements';
import { useProducts } from '../../hooks/useProducts';
import { useWarehouses } from '../../hooks/useWarehouses';
import { MovementType, MovementCreate } from '../../types/inventory_movement';
import { useToast } from '../common/Toast';
import './MovementForm.css';

interface MovementFormProps {
  onSuccess?: () => void;
}

const MovementForm: React.FC<MovementFormProps> = ({ onSuccess }) => {
  const [movementType, setMovementType] = useState<MovementType>('inbound');
  const [productId, setProductId] = useState('');
  const [sourceWarehouseId, setSourceWarehouseId] = useState('');
  const [destinationWarehouseId, setDestinationWarehouseId] = useState('');
  const [quantity, setQuantity] = useState('');
  const [referenceNumber, setReferenceNumber] = useState('');
  const [notes, setNotes] = useState('');
  
  const { data: products } = useProducts();
  const { data: warehouses } = useWarehouses(true);
  const createMovement = useCreateMovement();
  const { showToast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!productId || !quantity || parseFloat(quantity) <= 0) {
      showToast('Please fill in all required fields with valid values', 'error');
      return;
    }

    if (movementType === 'inbound' && !destinationWarehouseId) {
      showToast('Destination warehouse is required for inbound movements', 'error');
      return;
    }

    if (movementType === 'outbound' && !sourceWarehouseId) {
      showToast('Source warehouse is required for outbound movements', 'error');
      return;
    }

    if (movementType === 'transfer' && (!sourceWarehouseId || !destinationWarehouseId)) {
      showToast('Both source and destination warehouses are required for transfers', 'error');
      return;
    }

    const movementData: MovementCreate = {
      movement_type: movementType,
      product_id: productId,
      quantity: parseFloat(quantity),
      reference_number: referenceNumber || null,
      notes: notes || null,
    };

    if (movementType !== 'inbound') {
      movementData.source_warehouse_id = sourceWarehouseId || null;
    }

    if (movementType !== 'outbound') {
      movementData.destination_warehouse_id = destinationWarehouseId || null;
    }

    try {
      await createMovement.mutateAsync(movementData);
      showToast('Movement created successfully', 'success');
      
      // Reset form
      setProductId('');
      setSourceWarehouseId('');
      setDestinationWarehouseId('');
      setQuantity('');
      setReferenceNumber('');
      setNotes('');
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || 'Failed to create movement',
        'error'
      );
    }
  };

  // Reset warehouse selections when movement type changes
  useEffect(() => {
    setSourceWarehouseId('');
    setDestinationWarehouseId('');
  }, [movementType]);

  return (
    <form onSubmit={handleSubmit} className="movement-form">
      <div className="form-group">
        <label htmlFor="movement_type">Movement Type *</label>
        <select
          id="movement_type"
          value={movementType}
          onChange={(e) => setMovementType(e.target.value as MovementType)}
          required
        >
          <option value="inbound">Inbound (Receiving)</option>
          <option value="outbound">Outbound (Shipping)</option>
          <option value="transfer">Transfer (Between Warehouses)</option>
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="product_id">Product *</label>
        <select
          id="product_id"
          value={productId}
          onChange={(e) => setProductId(e.target.value)}
          required
        >
          <option value="">Select a product</option>
          {products?.map((product) => (
            <option key={product.id} value={product.id}>
              {product.sku} - {product.name}
            </option>
          ))}
        </select>
      </div>

      {movementType !== 'inbound' && (
        <div className="form-group">
          <label htmlFor="source_warehouse_id">Source Warehouse *</label>
          <select
            id="source_warehouse_id"
            value={sourceWarehouseId}
            onChange={(e) => setSourceWarehouseId(e.target.value)}
            required
          >
            <option value="">Select source warehouse</option>
            {warehouses?.map((warehouse) => (
              <option key={warehouse.id} value={warehouse.id}>
                {warehouse.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {movementType !== 'outbound' && (
        <div className="form-group">
          <label htmlFor="destination_warehouse_id">Destination Warehouse *</label>
          <select
            id="destination_warehouse_id"
            value={destinationWarehouseId}
            onChange={(e) => setDestinationWarehouseId(e.target.value)}
            required
          >
            <option value="">Select destination warehouse</option>
            {warehouses?.map((warehouse) => (
              <option key={warehouse.id} value={warehouse.id}>
                {warehouse.name}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="form-group">
        <label htmlFor="quantity">Quantity *</label>
        <input
          id="quantity"
          type="number"
          step="0.001"
          min="0.001"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          required
          placeholder="Enter quantity"
        />
      </div>

      <div className="form-group">
        <label htmlFor="reference_number">Reference Number</label>
        <input
          id="reference_number"
          type="text"
          value={referenceNumber}
          onChange={(e) => setReferenceNumber(e.target.value)}
          placeholder="e.g., PO-12345, Shipment-001"
        />
      </div>

      <div className="form-group">
        <label htmlFor="notes">Notes</label>
        <textarea
          id="notes"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={3}
          placeholder="Additional notes about this movement"
        />
      </div>

      <button
        type="submit"
        disabled={createMovement.isPending}
        className="submit-button"
      >
        {createMovement.isPending ? 'Creating...' : 'Create Movement'}
      </button>
    </form>
  );
};

export default MovementForm;
