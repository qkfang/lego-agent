//import { Player, Recorder } from "./voice";
import { Player, Recorder } from ".";
import { WebSocketClient } from "./websocket-client";

export interface ConsoleUpdate {
  id: string;
  type: "console";
  payload: object;
}

export interface MessageUpdate {
  id: string;
  type: "message"
  role: "user" | "assistant";
  content: string;
}
export interface FunctionUpdate {
  id: string;
  type: "function";
  call_id: string;
  name: string;
  arguments: Record<string, any>;
}

export interface FunctionCompletionUpdate {
  id: string;
  type: "function_completion";
  call_id: string;
  output: string;
}

export interface AudioUpdate {
  id: string;
  type: "audio";
  content: string;
}

export interface Content {
  type: "text" | "image" | "video" | "tool_calls";
  content: Array<Record<string, any>>;
}

export interface AgentUpdate {
  id: string;
  type: "agent";
  call_id: string;
  name: string;
  status: string;
  information?: string;
  content?: Content;
  output?: boolean;
}

export interface InterruptUpdate {
  id: string;
  type: "interrupt";
}

export interface SettingsUpdate {
  id: string;
  type: "settings";
  settings: Record<string, any>;
}

export interface ErrorUpdate {
  id: string;
  type: "error";
  message: string;
  error: string;
}

export type Update =
  | MessageUpdate
  | FunctionUpdate
  | AgentUpdate
  | AudioUpdate
  | ConsoleUpdate
  | InterruptUpdate
  | FunctionCompletionUpdate
  | SettingsUpdate
  | ErrorUpdate;


export class VoiceClient {
  //private updateQueue: Update[] = [];
  //private started: boolean = false;
  url: string | URL;
  socket: WebSocketClient<Update, Update> | null;
  player: Player | null;
  recorder: Recorder | null;
  handleServerMessage: (update: Update) => Promise<void>;
  setAnalyzer: (analyzer: AnalyserNode) => void;

  constructor(
    url: string | URL,
    handleServerMessage: (update: Update) => Promise<void>,
    setAnalyzer: (analyzer: AnalyserNode) => void
  ) {
    this.url = url;
    this.handleServerMessage = handleServerMessage;
    this.setAnalyzer = setAnalyzer;
    this.socket = null;
    this.player = null;
    this.recorder = null;
  }

  async start(deviceId: string | null = null) {
    console.log("Starting voice client", this.url);
    this.socket = new WebSocketClient<Update, Update>(this.url);

    this.player = new Player(this.setAnalyzer);

    await this.player.init(24000);

    this.recorder = new Recorder((buffer: any) => {
      const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)));
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket!.send({ id: "audio", type: "audio", content: base64 });
      }
    });

    let audio: object = {
      sampleRate: 24000,
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true,
    };

    if (deviceId) {
      console.log("Using device:", deviceId);
      audio = { ...audio, deviceId: { exact: deviceId } };
    }

    console.log(audio);
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: audio,
    });

    this.recorder.start(stream);
    this.startResponseListener();
  }

  async startResponseListener() {
    if (!this.socket) {
      return;
    }

    try {
      for await (const serverEvent of this.socket) {

        if (serverEvent.type === "audio") {
          // handle audio case internally
          const buffer = Uint8Array.from(atob(serverEvent.content), (c) =>
            c.charCodeAt(0)
          ).buffer;
          this.player!.play(new Int16Array(buffer));
        } else if (serverEvent.type === "interrupt") {
          // handle interrupt case internally
          this.player!.clear();
        } else {
          // add to update queue
          //this.updateQueue.push(serverEvent);
          this.handleServerMessage(serverEvent);
        }
      }
    } catch (error) {
      if (this.socket) {
        console.error("Response iteration error:", error);
      }
    }
  }

    

  async stop() {
    if (this.socket) {
      this.player?.clear();
      this.recorder?.stop();
      await this.socket.close();
    }
  }

  async send(update: Update) {
    if (this.socket) {
      this.socket.send(update);
    }
  }

  mute_microphone() {
    if (this.recorder) {
      this.recorder.mute();
    }
  }
  unmute_microphone() {
    if (this.recorder) {
      this.recorder.unmute();
    }
  }

  async sendUserMessage(message: string) {
    this.send({ id: "message", type: "message", role: "user", content: message });
  }

  async sendCreateResponse() {
    this.send({ id: "interrupt", type: "interrupt" });
  }
}

export default VoiceClient;
