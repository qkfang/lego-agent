import { use, useEffect, useRef, useState } from "react";
import { WS_ENDPOINT } from "store/endpoint";
import { useLocalStorage } from "store/uselocalstorage";
import type { User } from "store/useuser";
import { defaultConfiguration, type VoiceConfiguration } from "store/voice";
import type { SettingsUpdate, Update } from "store/voice/voice-client";
import { VoiceClient } from "store/voice/voice-client";

export const useRealtime = (
  user: User,
  handleMessage: (serverEvent: Update) => Promise<void>
) => {
  const { storedValue: settings } = useLocalStorage<VoiceConfiguration>(
    "voice-settings",
    defaultConfiguration
  );

  const [callState, setCallState] = useState<"idle" | "call">("idle");
  const [analyzer, setAnalyzer] = useState<AnalyserNode | null>(null);
  const [muted, setMuted] = useState(true);
  const voiceRef = useRef<VoiceClient | null>(null);

  const startRealtime = async () => {
    if (voiceRef.current) {
      await voiceRef.current.stop();
      voiceRef.current = null;
    }

    if (!voiceRef.current) {
      const endpoint = WS_ENDPOINT.endsWith("/")
        ? WS_ENDPOINT.slice(0, -1)
        : WS_ENDPOINT;

      voiceRef.current = new VoiceClient(
        `${endpoint}/api/voice/${user.key}`,
        handleMessage,
        setAnalyzer
      );

      await voiceRef.current.start(settings.inputDeviceId);
      const currentDate = new Date();

      const values: SettingsUpdate = {
        id: user.key,
        type: "settings",
        settings: {
          user: user!.name,
          date: currentDate.toLocaleDateString(),
          time: currentDate.toLocaleTimeString(),
          detection_type: settings.detectionType,
          transcription_model: settings.transcriptionModel,
          threshold: settings.threshold,
          silence_duration: settings.silenceDuration,
          prefix_padding: settings.prefixPadding,
          eagerness: settings.eagerness,
          voice: settings.voice,
        },
      };

      console.log("Sending settings", values);

      await voiceRef.current.send(values);
      await voiceRef.current.sendCreateResponse();
      setCallState("call");
    }
  };

  const stopRealtime = async () => {
    if (voiceRef.current) {
      await voiceRef.current.stop();
      voiceRef.current = null;
      setCallState("idle");
    }
  };

  const toggleRealtime = async () => {
    if (callState === "idle") {
      await startRealtime();
    }
    if (callState === "call") {
      await stopRealtime();
    }
  };

  const sendRealtime = async (update: Update) => {
    if (voiceRef.current) {
      await voiceRef.current.send(update);
    }
  };

   useEffect(() => {
    if (voiceRef.current) {
      if (muted) {
        console.log("muting");
        voiceRef.current.mute_microphone();
      } else {
        console.log("unmuting");
        voiceRef.current.unmute_microphone();
      }
    }
  }, [muted]);

  return {
    startRealtime,
    stopRealtime,
    toggleRealtime,
    sendRealtime,
    muted,
    setMuted,
    analyzer,
    callState,
  };
};
