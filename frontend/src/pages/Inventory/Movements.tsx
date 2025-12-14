import React, { useState } from 'react';
import { useMovements } from '../../hooks/useMovements';
import MovementForm from '../../components/inventory/MovementForm';
import MovementHistory from '../../components/inventory/MovementHistory';
import { useToast } from '../../components/common/Toast';
import './Movements.css';

const Movements: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const { data: movements, isLoading } = useMovements({ limit: 100 });
  const { showToast } = useToast();

  const handleFormSuccess = () => {
    setShowForm(false);
    showToast('Movement created successfully. Inventory updated in real-time.', 'success');
  };

  return (
    <div className="movements-page">
      <div className="page-header">
        <h1>Inventory Movements</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="toggle-form-button"
        >
          {showForm ? 'Hide Form' : 'Create Movement'}
        </button>
      </div>

      {showForm && (
        <div className="form-section">
          <h2>Create New Movement</h2>
          <MovementForm onSuccess={handleFormSuccess} />
        </div>
      )}

      <div className="history-section">
        <h2>Movement History</h2>
        <MovementHistory movements={movements || []} isLoading={isLoading} />
      </div>
    </div>
  );
};

export default Movements;
