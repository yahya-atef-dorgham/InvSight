import React, { useEffect } from 'react';
import './VoiceResponse.css';

interface VoiceResponseProps {
  responseText: string;
  autoPlay?: boolean;
}

const VoiceResponse: React.FC<VoiceResponseProps> = ({ responseText, autoPlay = true }) => {
  useEffect(() => {
    if (autoPlay && responseText && 'speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(responseText);
      utterance.lang = 'en-US';
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      
      window.speechSynthesis.speak(utterance);
      
      return () => {
        window.speechSynthesis.cancel();
      };
    }
  }, [responseText, autoPlay]);

  const handlePlay = () => {
    if ('speechSynthesis' in window && responseText) {
      const utterance = new SpeechSynthesisUtterance(responseText);
      utterance.lang = 'en-US';
      window.speechSynthesis.speak(utterance);
    }
  };

  if (!responseText) {
    return null;
  }

  return (
    <div className="voice-response">
      <div className="response-content">
        <p className="response-text">{responseText}</p>
        {window.speechSynthesis && (
          <button onClick={handlePlay} className="play-button" title="Replay response">
            🔊
          </button>
        )}
      </div>
    </div>
  );
};

export default VoiceResponse;
