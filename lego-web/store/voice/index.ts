export interface VoiceConfiguration {
  inputDeviceId: string;
  detectionType: "semantic_vad" | "server_vad",
  transcriptionModel: string;
  threshold: number;
  silenceDuration: number;
  prefixPadding: number;
  eagerness: "low" | "medium" | "high" | "auto"
  voice: string;
}

export const defaultVoices = [
  { name: "Alloy", value: "alloy" },
  { name: "Ash", value: "ash" },
  { name: "Ballad", value: "ballad" },
  { name: "Coral", value: "coral" },
  { name: "Echo", value: "echo" },
  { name: "Sage", value: "sage" },
  { name: "Shimmer", value: "shimmer" },
  { name: "Verse", value: "verse" }
];

export const defaultEagerness = [
  { name: "Low", value: "low" },
  { name: "Medium", value: "medium" },
  { name: "High", value: "high" },
  { name: "Auto", value: "auto" }
];


export const defaultConfiguration: VoiceConfiguration = {
  inputDeviceId: "default",
  detectionType: "server_vad",
  transcriptionModel: "whisper-1",
  threshold: 0.8,
  silenceDuration: 500,
  prefixPadding: 300,
  eagerness: "auto",
  voice: "sage"
};

export class Player {
  private playbackNode: AudioWorkletNode | null = null;
  setAnalyzer: (analyzer: AnalyserNode) => void;

  constructor(setAnalyzer: (analyzer: AnalyserNode) => void) {
    this.setAnalyzer = setAnalyzer;
  }

  async init(sampleRate: number) {
    const audioContext = new AudioContext({ sampleRate });
    await audioContext.audioWorklet.addModule("playback-worklet.js");
    this.playbackNode = new AudioWorkletNode(audioContext, "playback-worklet");
    this.playbackNode.connect(audioContext.destination);
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;
    analyser.minDecibels = -90;
    analyser.maxDecibels = -10;
    analyser.smoothingTimeConstant = 0.85;
    this.playbackNode.connect(analyser);
    this.setAnalyzer(analyser);
  }

  play(buffer: Int16Array) {
    if (this.playbackNode) {
      this.playbackNode.port.postMessage(buffer);
    }
  }

  clear() {
    if (this.playbackNode) {
      this.playbackNode.port.postMessage(null);
    }
  }
}

export class Recorder {
  onDataAvailable: (buffer: ArrayBuffer) => void;
  private audioContext: AudioContext | null = null;
  private mediaStream: MediaStream | null = null;
  private mediaStreamSource: MediaStreamAudioSourceNode | null = null;
  private workletNode: AudioWorkletNode | null = null;
  private muted: boolean = true;

  public constructor(onDataAvailable: (buffer: ArrayBuffer) => void) {
    this.onDataAvailable = onDataAvailable;
  }

  async start(stream: MediaStream) {
    try {
      this.audioContext = new AudioContext({ sampleRate: 24000 });

      await this.audioContext.audioWorklet.addModule(
        "./audio-worklet-processor.js"
      );
      this.mediaStream = stream;
      this.mediaStreamSource = this.audioContext.createMediaStreamSource(
        this.mediaStream
      );
      this.workletNode = new AudioWorkletNode(
        this.audioContext,
        "audio-worklet-processor"
      );
      let buffer: Uint8Array[] = [];
      let bufferSize = 0;
      const targetSize = 4800;

      this.workletNode.port.onmessage = (event) => {
        if (this.muted) {
          return;
        }
        const data = new Uint8Array(event.data.buffer);
        buffer.push(data);
        bufferSize += data.byteLength;

        if (bufferSize >= targetSize) {
          const concatenatedBuffer = new Uint8Array(bufferSize);
          let offset = 0;
          for (const chunk of buffer) {
            concatenatedBuffer.set(chunk, offset);
            offset += chunk.byteLength;
          }
          this.onDataAvailable(concatenatedBuffer.buffer);
          buffer = [];
          bufferSize = 0;
        }
      };

      this.mediaStreamSource.connect(this.workletNode);
      this.workletNode.connect(this.audioContext.destination);
    } catch {
      this.stop();
    }
  }

  mute() {
    this.muted = true;
  }



  unmute() {
    this.muted = false;
  }

  stop() {
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop());
    }
    if (this.audioContext) {
      this.audioContext.close();
    }
  }
}
