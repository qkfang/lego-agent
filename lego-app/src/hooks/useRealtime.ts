import { useRef, useState } from "react";

const WS_ENDPOINT = 'ws://localhost:8000';

interface User {
  key: string;
  name: string;
}

export interface Update {
  id: string;
  type: string;
  role?: string;
  content?: string;
  [key: string]: any;
}

export default function useRealtime(
  user: User,
  handleMessage: (serverEvent: Update) => Promise<void>
) {
  const [callState, setCallState] = useState<"idle" | "call">("idle");
  const [analyzer, setAnalyzer] = useState<AnalyserNode | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);

  const startRealtime = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      const audioContext = new AudioContext();
      audioContextRef.current = audioContext;
      
      const source = audioContext.createMediaStreamSource(stream);
      const analyzerNode = audioContext.createAnalyser();
      analyzerNode.fftSize = 2048;
      source.connect(analyzerNode);
      setAnalyzer(analyzerNode);

      const endpoint = WS_ENDPOINT.endsWith("/") ? WS_ENDPOINT.slice(0, -1) : WS_ENDPOINT;
      const ws = new WebSocket(`${endpoint}/api/voice/${user.key}`);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        const currentDate = new Date();
        
        ws.send(JSON.stringify({
          id: user.key,
          type: "settings",
          settings: {
            user: user.name,
            date: currentDate.toLocaleDateString(),
            time: currentDate.toLocaleTimeString(),
            detection_type: "server_vad",
            transcription_model: "whisper-1",
            threshold: 0.5,
            silence_duration: 500,
            prefix_padding: 300,
            eagerness: "medium",
            voice: "sage",
          },
        }));

        ws.send(JSON.stringify({
          type: "response.create",
        }));

        setCallState("call");
      };

      ws.onmessage = async (event) => {
        try {
          const data = JSON.parse(event.data);
          await handleMessage(data);
        } catch (err) {
          console.error('Error handling message:', err);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        stopRealtime();
      };

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm',
      });

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0 && ws.readyState === WebSocket.OPEN) {
          const reader = new FileReader();
          reader.onload = () => {
            const base64 = (reader.result as string).split(',')[1];
            ws.send(JSON.stringify({
              type: 'input_audio_buffer.append',
              audio: base64,
            }));
          };
          reader.readAsDataURL(event.data);
        }
      };

      mediaRecorder.start(100);
      
    } catch (err) {
      console.error('Error starting realtime:', err);
      alert('Unable to access microphone. Please check permissions.');
    }
  };

  const stopRealtime = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
      mediaStreamRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    setAnalyzer(null);
    setCallState("idle");
  };

  const toggleRealtime = async () => {
    if (callState === "idle") {
      await startRealtime();
    } else {
      stopRealtime();
    }
  };

  const sendRealtime = async (update: Update) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      if (update.type === "message") {
        wsRef.current.send(JSON.stringify({
          type: 'conversation.item.create',
          item: {
            type: 'message',
            role: 'user',
            content: [{
              type: 'input_text',
              text: update.content,
            }],
          },
        }));
        wsRef.current.send(JSON.stringify({
          type: 'response.create',
        }));
      } else {
        wsRef.current.send(JSON.stringify(update));
      }
    }
  };

  return {
    toggleRealtime,
    sendRealtime,
    analyzer,
    callState,
  };
}
