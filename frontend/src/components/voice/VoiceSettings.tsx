import React, { useState } from 'react';
import './VoiceSettings.css';

interface VoiceSettingsProps {
  onSettingsChange?: (settings: VoiceSettingsData) => void;
}

export interface VoiceSettingsData {
  language: string;
  speed: number;
  voice: string;
  autoPlay: boolean;
}

const VoiceSettings: React.FC<VoiceSettingsProps> = ({ onSettingsChange }) => {
  const [settings, setSettings] = useState<VoiceSettingsData>({
    language: 'en-US',
    speed: 1.0,
    voice: 'default',
    autoPlay: true,
  });

  const handleChange = (key: keyof VoiceSettingsData, value: any) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);
    onSettingsChange?.(newSettings);
  };

  return (
    <div className="voice-settings">
      <h3>Voice Settings</h3>
      
      <div className="settings-group">
        <label htmlFor="language">Language:</label>
        <select
          id="language"
          value={settings.language}
          onChange={(e) => handleChange('language', e.target.value)}
        >
          <option value="en-US">English (US)</option>
          <option value="en-GB">English (UK)</option>
          <option value="es-ES">Spanish</option>
          <option value="fr-FR">French</option>
        </select>
      </div>

      <div className="settings-group">
        <label htmlFor="speed">Speech Speed:</label>
        <input
          id="speed"
          type="range"
          min="0.5"
          max="2.0"
          step="0.1"
          value={settings.speed}
          onChange={(e) => handleChange('speed', parseFloat(e.target.value))}
        />
        <span>{settings.speed.toFixed(1)}x</span>
      </div>

      <div className="settings-group">
        <label>
          <input
            type="checkbox"
            checked={settings.autoPlay}
            onChange={(e) => handleChange('autoPlay', e.target.checked)}
          />
          Auto-play responses
        </label>
      </div>
    </div>
  );
};

export default VoiceSettings;
