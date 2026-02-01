# LEGO Robot Mobile App

A funky mobile web app for controlling LEGO robots with voice commands! 🎵 Everything is Awesome!

## Features

- 🎤 Voice command recognition
- ⌨️ Text input for commands
- 🎨 LEGO Movie themed UI
- 📱 Mobile-optimized interface
- 🔊 Real-time audio visualization

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your mobile browser and navigate to `http://localhost:5174`

## Prerequisites

- Node.js 18+ 
- lego-api backend running (default: `http://localhost:8000`)

## Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit the `.env` file to configure your backend endpoint:

```
VITE_WS_ENDPOINT=ws://localhost:8000
```

## Usage

1. Tap the microphone button to start voice control
2. Speak your command naturally
3. Or use the text input to type commands
4. Watch your LEGO robot come to life!

## API Connection

The app connects to the same backend as lego-web:
- WebSocket: `ws://localhost:8000/api/voice/{user_key}`
- REST API: `http://localhost:8000/api/agent/{user_key}`
