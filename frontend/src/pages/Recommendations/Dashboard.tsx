import React, { useState } from 'react';
import { useRecommendations } from '../../hooks/useRecommendations';
import { useCreateRecommendation } from '../../hooks/useRecommendations';
import { useProducts } from '../../hooks/useProducts';
import { useWarehouses } from '../../hooks/useWarehouses';
import RecommendationsList from '../../components/recommendations/RecommendationsList';
import RecommendationDetail from '../../components/recommendations/RecommendationDetail';
import { Recommendation } from '../../types/recommendation';
import { useToast } from '../../components/common/Toast';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  const [selectedRecommendation, setSelectedRecommendation] = useState<Recommendation | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('active');
  const [urgencyFilter, setUrgencyFilter] = useState<boolean>(false);
  
  const { data: recommendations, isLoading } = useRecommendations({
    status: statusFilter as any,
    urgency_min: urgencyFilter ? 50 : undefined,
  });
  
  const createRecommendation = useCreateRecommendation();
  const { showToast } = useToast();
  const { data: products } = useProducts();
  const { data: warehouses } = useWarehouses(true);

  const handleCreateRecommendation = async () => {
    if (!products || products.length === 0 || !warehouses || warehouses.length === 0) {
      showToast('Please ensure products and warehouses exist first', 'warning');
      return;
    }

    // Create a sample recommendation (in production, this would be triggered by system)
    try {
      await createRecommendation.mutateAsync({
        recommendation_type: 'reorder_quantity',
        product_id: products[0].id,
        warehouse_id: warehouses[0].id,
      });
      showToast('Recommendation generated successfully', 'success');
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || 'Failed to generate recommendation',
        'error'
      );
    }
  };

  return (
    <div className="recommendations-dashboard">
      <div className="dashboard-header">
        <h1>AI Recommendations</h1>
        <div className="header-actions">
          <button onClick={handleCreateRecommendation} className="generate-button">
            Generate Recommendation
          </button>
        </div>
      </div>

      <div className="dashboard-filters">
        <div className="filter-group">
          <label htmlFor="status-filter">Status:</label>
          <select
            id="status-filter"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="active">Active</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="superseded">Superseded</option>
          </select>
        </div>

        <div className="filter-group">
          <label>
            <input
              type="checkbox"
              checked={urgencyFilter}
              onChange={(e) => setUrgencyFilter(e.target.checked)}
            />
            High Urgency Only
          </label>
        </div>
      </div>

      {selectedRecommendation ? (
        <div className="detail-view">
          <RecommendationDetail
            recommendation={selectedRecommendation}
            onClose={() => setSelectedRecommendation(null)}
          />
        </div>
      ) : (
        <RecommendationsList
          recommendations={recommendations || []}
          isLoading={isLoading}
          onRecommendationClick={setSelectedRecommendation}
        />
      )}
    </div>
  );
};

export default Dashboard;
