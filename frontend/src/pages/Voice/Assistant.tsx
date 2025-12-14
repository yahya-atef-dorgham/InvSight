import React, { useState } from 'react';
import { useInteractionHistory } from '../../hooks/useVoice';
import VoiceInput from '../../components/voice/VoiceInput';
import VoiceResponse from '../../components/voice/VoiceResponse';
import VoiceHistory from '../../components/voice/VoiceHistory';
import VoiceSettings, { VoiceSettingsData } from '../../components/voice/VoiceSettings';
import { useToast } from '../../components/common/Toast';
import './Assistant.css';

const Assistant: React.FC = () => {
  const [response, setResponse] = useState('');
  const [settings, setSettings] = useState<VoiceSettingsData>({
    language: 'en-US',
    speed: 1.0,
    voice: 'default',
    autoPlay: true,
  });
  
  const { data: interactions } = useInteractionHistory({ limit: 20 });

  const handleResponse = (responseText: string) => {
    setResponse(responseText);
  };

  return (
    <div className="voice-assistant-page">
      <div className="page-header">
        <h1>Voice Assistant</h1>
      </div>

      <div className="assistant-content">
        <div className="assistant-main">
          <div className="voice-section">
            <VoiceInput onResponse={handleResponse} />
            {response && (
              <VoiceResponse responseText={response} autoPlay={settings.autoPlay} />
            )}
          </div>

          <div className="settings-section">
            <VoiceSettings onSettingsChange={setSettings} />
          </div>
        </div>

        <div className="history-section">
          <VoiceHistory interactions={interactions || []} />
        </div>
      </div>
    </div>
  );
};

export default Assistant;
