import { useLocalStorage } from "store/uselocalstorage";
import { useMediaDevices } from "store/usemediadevice";
import { GrPowerReset } from "react-icons/gr";
import styles from "./voicesettings.module.scss";
import {
  defaultConfiguration,
  defaultEagerness,
  defaultVoices,
  type VoiceConfiguration,
} from "store/voice";

const VoiceSettings = () => {
  const { storedValue: settings, setValue: setSettings } =
    useLocalStorage<VoiceConfiguration>("voice-settings", defaultConfiguration);
  const { devices, error, isLoading } = useMediaDevices(true);

  return (
    <>
      <div className={styles.control}>
        <div className={styles.label}>Voice Input:</div>
        <select
          id="device"
          name="device"
          className={styles.mediaselect}
          value={settings.inputDeviceId}
          title="Select a device"
          onChange={(e) =>
            setSettings({ ...settings, inputDeviceId: e.target.value })
          }
        >
          {isLoading && <option>Loading...</option>}
          {error && <option>Error: {error}</option>}
          {devices
            .filter((device) => device.kind === "audioinput")
            .map((device) => {
              return (
                <option key={device.deviceId} value={device.deviceId}>
                  {device.label}
                </option>
              );
            })}
        </select>
      </div>
      <div className={styles.control}>
        <div
          className={styles.label}
          title={
            "The voice used for the model response for the session.\n\nOnce the voice is used in the session for the model's audio response, it can't be changed."
          }
        >
          Voice:
        </div>
        <select
          id="voice"
          name="voice"
          className={styles.mediaselect}
          value={settings.voice}
          title="Select a voice"
          onChange={(e) => setSettings({ ...settings, voice: e.target.value })}
        >
          {defaultVoices.map((voice) => {
            return (
              <option key={voice.value} value={voice.value}>
                {voice.name}
              </option>
            );
          })}
        </select>
      </div>
      <div className={styles.control}>
        <div
          className={styles.label}
          title={
            "The model used for the transcription of the audio.\n\nOnce the model is used in the session for the model's audio response, it can't be changed."
          }
        >
          Transcription Model:
        </div>
        <select
          id="transcription_model"
          name="transcription_model"
          className={styles.mediaselect}
          value={settings.transcriptionModel}
          title="Select a voice"
          onChange={(e) =>
            setSettings({ ...settings, transcriptionModel: e.target.value })
          }
        >
          <option key="gpt-4o-transcribe" value="gpt-4o-transcribe">
            gpt-4o-transcribe
          </option>
          <option key="gpt-4o-mini-transcribe" value="gpt-4o-mini-transcribe">
            gpt-4o-mini-transcribe
          </option>
          <option key="whisper-1" value="whisper-1">
            whisper-1
          </option>
        </select>
      </div>
      <div className={styles.control}>
        <div
          className={styles.label}
          title={
            'The eagerness of the model to respond. "low" will wait longer for the user to continue speaking, high will respond more quickly.\n "auto" is the default and is equivalent to "medium".'
          }
        >
          Detection Type:
        </div>
        <div className={styles.radioGroup}>
          <span>
            <input
              type="radio"
              id="server_vad"
              name="detection_type"
              value="server_vad"
              checked={settings.detectionType === "server_vad"}
              onChange={() =>
                setSettings({
                  ...settings,
                  detectionType: "server_vad",
                })
              }
            />
            <label htmlFor="server_vad">Server VAD</label>
          </span>
          <span>
            <input
              type="radio"
              id="semantic_vad"
              name="detection_type"
              value="semantic_vad"
              checked={settings.detectionType === "semantic_vad"}
              onChange={() =>
                setSettings({
                  ...settings,
                  detectionType: "semantic_vad",
                })
              }
            />
            <label htmlFor="semantic_vad">Semantic VAD</label>
          </span>
        </div>
      </div>
      {settings.detectionType === "semantic_vad" && (
        <div className={styles.control}>
          <div
            className={styles.label}
            title={
              'The eagerness of the model to respond. "low" will wait longer for the user to continue speaking, high will respond more quickly.\n "auto" is the default and is equivalent to "medium".'
            }
          >
            Eagerness:
          </div>
          <select
            id="eagerness"
            name="eagerness"
            className={styles.mediaselect}
            value={settings.eagerness}
            title="Select a voice"
            onChange={(e) =>
              setSettings({
                ...settings,
                eagerness: e.target.value as "low" | "medium" | "high" | "auto",
              })
            }
          >
            {defaultEagerness.map((voice) => {
              return (
                <option key={voice.value} value={voice.value}>
                  {voice.name}
                </option>
              );
            })}
          </select>
        </div>
      )}
      {settings.detectionType === "server_vad" && (
        <>
          <div className={styles.control}>
            <div className={styles.label}>
              Sensitivity Threshold (between 0 - 1):
            </div>
            <input
              id="threshold"
              name="threshold"
              type="number"
              title="Sensitivity Threshold"
              min={0}
              max={1}
              step={0.1}
              className={styles.textInput}
              value={settings.threshold}
              onChange={(e) =>
                setSettings({ ...settings, threshold: +e.target.value })
              }
            />
          </div>
          <div className={styles.control}>
            <div className={styles.label}>Silence Duration (in ms):</div>
            <input
              id="silence"
              name="chat"
              type="number"
              title="Silence Duration"
              min={0}
              max={3000}
              step={50}
              className={styles.textInput}
              value={settings.silenceDuration}
              onChange={(e) =>
                setSettings({ ...settings, silenceDuration: +e.target.value })
              }
            />
          </div>
          <div className={styles.control}>
            <div className={styles.label}>Prefix Padding (in ms):</div>
            <input
              id="prefix"
              name="chat"
              type="number"
              title="Prefix Padding"
              min={0}
              max={3000}
              step={50}
              className={styles.textInput}
              value={settings.prefixPadding}
              onChange={(e) =>
                setSettings({ ...settings, prefixPadding: +e.target.value })
              }
            />
          </div>{" "}
        </>
      )}
      <div className={styles.buttonContainer}>
        <button
          className={styles.resetButton}
          onClick={() => setSettings(defaultConfiguration)}
          title="Reset to default settings"
        >
          <GrPowerReset size={24} />
        </button>
      </div>
    </>
  );
};

export default VoiceSettings;
