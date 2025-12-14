import React from 'react';
import { Recommendation } from '../../types/recommendation';
import { useRecommendationExplanation } from '../../hooks/useRecommendations';
import './RecommendationDetail.css';

interface RecommendationDetailProps {
  recommendation: Recommendation;
  onClose?: () => void;
}

const RecommendationDetail: React.FC<RecommendationDetailProps> = ({
  recommendation,
  onClose,
}) => {
  const { data: explanation, isLoading } = useRecommendationExplanation(recommendation.id);

  return (
    <div className="recommendation-detail">
      <div className="detail-header">
        <h2>Recommendation Details</h2>
        {onClose && (
          <button onClick={onClose} className="close-button">
            ×
          </button>
        )}
      </div>

      <div className="detail-content">
        <div className="detail-section">
          <h3>Recommendation</h3>
          <div className="detail-grid">
            <div className="detail-item">
              <span className="detail-label">Type:</span>
              <span className="detail-value">
                {recommendation.recommendation_type.replace('_', ' ').toUpperCase()}
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Status:</span>
              <span className={`detail-value status-${recommendation.status}`}>
                {recommendation.status}
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Recommended Value:</span>
              <span className="detail-value">
                {recommendation.recommended_value?.toLocaleString() || 'N/A'}
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Current Value:</span>
              <span className="detail-value">
                {recommendation.current_value?.toLocaleString() || 'N/A'}
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Urgency Score:</span>
              <span className="detail-value urgency-high">
                {recommendation.urgency_score?.toFixed(0) || 'N/A'}
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Confidence Score:</span>
              <span className="detail-value">
                {recommendation.confidence_score?.toFixed(0) || 'N/A'}%
              </span>
            </div>
          </div>
        </div>

        {recommendation.explanation && (
          <div className="detail-section">
            <h3>Explanation</h3>
            <p className="explanation-text">{recommendation.explanation}</p>
          </div>
        )}

        {explanation && explanation.explanation_json && (
          <div className="detail-section">
            <h3>Detailed Analysis</h3>
            <div className="analysis-content">
              <pre>{JSON.stringify(explanation.explanation_json, null, 2)}</pre>
            </div>
          </div>
        )}

        {isLoading && (
          <div className="loading">Loading detailed explanation...</div>
        )}
      </div>
    </div>
  );
};

export default RecommendationDetail;
