import React from 'react';
import { AIInteraction } from '../../types/voice';
import './VoiceHistory.css';

interface VoiceHistoryProps {
  interactions: AIInteraction[];
  isLoading?: boolean;
}

const VoiceHistory: React.FC<VoiceHistoryProps> = ({ interactions, isLoading }) => {
  if (isLoading) {
    return (
      <div className="voice-history-loading">
        <div className="loading-spinner">Loading voice history...</div>
      </div>
    );
  }

  if (interactions.length === 0) {
    return (
      <div className="voice-history-empty">
        <p>No voice interactions yet.</p>
      </div>
    );
  }

  return (
    <div className="voice-history">
      <h3>Recent Interactions</h3>
      <div className="interactions-list">
        {interactions.map((interaction) => (
          <div key={interaction.id} className="interaction-item">
            <div className="interaction-header">
              <span className="interaction-type">
                {interaction.interaction_type === 'voice' ? '🎤' : '⌨️'}
              </span>
              <span className="interaction-date">
                {new Date(interaction.created_at).toLocaleString()}
              </span>
            </div>
            <div className="interaction-query">
              <strong>Q:</strong> {interaction.query_text}
            </div>
            <div className="interaction-response">
              <strong>A:</strong> {interaction.response_text}
            </div>
            {interaction.intent && (
              <div className="interaction-meta">
                Intent: {interaction.intent} | Confidence: {interaction.confidence_score?.toFixed(0) || 'N/A'}%
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default VoiceHistory;
