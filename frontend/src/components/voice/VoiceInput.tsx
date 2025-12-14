import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useVoiceQuery } from '../../hooks/useVoice';
import { useToast } from '../common/Toast';
import './VoiceInput.css';

interface VoiceInputProps {
  onResponse?: (response: string) => void;
}

const VoiceInput: React.FC<VoiceInputProps> = ({ onResponse }) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const voiceQuery = useVoiceQuery();
  const { showToast } = useToast();

  const handleQuery = useCallback(async (queryText: string) => {
    if (!queryText.trim()) return;

    setIsProcessing(true);
    setTranscript(queryText);

    try {
      const response = await voiceQuery.mutateAsync({
        query_text: queryText,
        interaction_type: 'voice',
        language: 'en-US',
      });

      if (onResponse) {
        onResponse(response.response_text);
      }

      // Speak response using Web Speech API
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(response.response_text);
        utterance.lang = 'en-US';
        window.speechSynthesis.speak(utterance);
      }

      setTranscript('');
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || 'Failed to process voice query',
        'error'
      );
    } finally {
      setIsProcessing(false);
    }
  }, [voiceQuery, onResponse, showToast]);

  useEffect(() => {
    // Check if Web Speech API is supported
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    
    if (SpeechRecognition) {
      setIsSupported(true);
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      let finalTranscript = '';

      recognition.onstart = () => {
        setIsListening(true);
        setTranscript('');
        finalTranscript = '';
      };

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        let interimTranscript = '';
        let final = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript_text = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            final += transcript_text;
          } else {
            interimTranscript += transcript_text;
          }
        }
        
        if (final) {
          finalTranscript = final;
        }
        
        setTranscript(interimTranscript || finalTranscript);
      };

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        showToast('Speech recognition error. Please try typing your query.', 'error');
      };

      recognition.onend = () => {
        setIsListening(false);
        const queryText = finalTranscript.trim();
        if (queryText) {
          handleQuery(queryText);
        }
      };

      recognitionRef.current = recognition;
    } else {
      setIsSupported(false);
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [handleQuery, showToast]);

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      try {
        recognitionRef.current.start();
      } catch (error) {
        console.error('Failed to start recognition:', error);
        showToast('Failed to start voice recognition', 'error');
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  };

  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (transcript.trim()) {
      handleQuery(transcript);
    }
  };

  if (!isSupported) {
    return (
      <div className="voice-input">
        <form onSubmit={handleTextSubmit} className="voice-form">
          <input
            type="text"
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            placeholder="Type your query (Voice not supported in this browser)"
            className="voice-input-field"
            disabled={isProcessing}
          />
          <button type="submit" disabled={isProcessing || !transcript.trim()}>
            {isProcessing ? 'Processing...' : 'Send'}
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="voice-input">
      <div className="voice-controls">
        <button
          type="button"
          onClick={isListening ? stopListening : startListening}
          disabled={isProcessing}
          className={`voice-button ${isListening ? 'listening' : ''}`}
        >
          {isListening ? '🛑 Stop' : '🎤 Start Voice'}
        </button>
        {isListening && (
          <span className="listening-indicator">Listening...</span>
        )}
      </div>

      {transcript && (
        <div className="transcript-display">
          <p className="transcript-label">You said:</p>
          <p className="transcript-text">{transcript}</p>
        </div>
      )}

      {isProcessing && (
        <div className="processing-indicator">Processing your query...</div>
      )}

      {/* Text input fallback */}
      <form onSubmit={handleTextSubmit} className="voice-form">
        <input
          type="text"
          value={transcript}
          onChange={(e) => setTranscript(e.target.value)}
          placeholder="Or type your query here"
          className="voice-input-field"
          disabled={isProcessing || isListening}
        />
        <button type="submit" disabled={isProcessing || !transcript.trim()}>
          {isProcessing ? 'Processing...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default VoiceInput;
