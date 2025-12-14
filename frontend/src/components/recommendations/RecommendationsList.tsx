import React from 'react';
import { Recommendation } from '../../types/recommendation';
import RecommendationDetail from './RecommendationDetail';
import './RecommendationsList.css';

interface RecommendationsListProps {
  recommendations: Recommendation[];
  isLoading?: boolean;
  onRecommendationClick?: (recommendation: Recommendation) => void;
}

const RecommendationsList: React.FC<RecommendationsListProps> = ({
  recommendations,
  isLoading,
  onRecommendationClick,
}) => {
  if (isLoading) {
    return (
      <div className="recommendations-loading">
        <div className="loading-spinner">Loading recommendations...</div>
      </div>
    );
  }

  if (recommendations.length === 0) {
    return (
      <div className="recommendations-empty">
        <p>No recommendations available.</p>
      </div>
    );
  }

  const getUrgencyClass = (urgency: number | null) => {
    if (!urgency) return 'urgency-low';
    if (urgency >= 75) return 'urgency-high';
    if (urgency >= 50) return 'urgency-medium';
    return 'urgency-low';
  };

  const getStatusClass = (status: string) => {
    switch (status) {
      case 'approved':
        return 'status-approved';
      case 'rejected':
        return 'status-rejected';
      case 'superseded':
        return 'status-superseded';
      default:
        return 'status-active';
    }
  };

  return (
    <div className="recommendations-list">
      {recommendations.map((recommendation) => (
        <div
          key={recommendation.id}
          className={`recommendation-card ${getUrgencyClass(recommendation.urgency_score)}`}
          onClick={() => onRecommendationClick?.(recommendation)}
        >
          <div className="recommendation-header">
            <div className="recommendation-type">
              {recommendation.recommendation_type.replace('_', ' ').toUpperCase()}
            </div>
            <div className={`recommendation-status ${getStatusClass(recommendation.status)}`}>
              {recommendation.status}
            </div>
          </div>
          
          <div className="recommendation-content">
            <div className="recommendation-values">
              <div className="value-item">
                <span className="value-label">Recommended:</span>
                <span className="value-number">
                  {recommendation.recommended_value?.toLocaleString() || 'N/A'}
                </span>
              </div>
              <div className="value-item">
                <span className="value-label">Current:</span>
                <span className="value-number">
                  {recommendation.current_value?.toLocaleString() || 'N/A'}
                </span>
              </div>
            </div>
            
            {recommendation.explanation && (
              <div className="recommendation-explanation">
                {recommendation.explanation}
              </div>
            )}
            
            <div className="recommendation-scores">
              <div className="score-item">
                <span className="score-label">Urgency:</span>
                <span className={`score-value ${getUrgencyClass(recommendation.urgency_score)}`}>
                  {recommendation.urgency_score?.toFixed(0) || 'N/A'}
                </span>
              </div>
              <div className="score-item">
                <span className="score-label">Confidence:</span>
                <span className="score-value">
                  {recommendation.confidence_score?.toFixed(0) || 'N/A'}%
                </span>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default RecommendationsList;
