# LEGO Agent Features

This repository is a modular AI agent platform for robotics, BLE, camera, and web integration. Below are the key features:

## 🧩 Modular Architecture

- **lego-api**: Python-based API for agent orchestration, Azure integration, and telemetry.
- **lego-mcp**: Node.js server for robot control, supporting live, test, and mock modes.
- **lego-ble**: BLE communication utilities for hardware interaction.
- **lego-cam**: Camera client for image and video capture.
- **lego-web**: React web interface for agent management, output visualization, and voice interaction.

## 🤖 Robot Control

- Move, turn, beep, and control robot arm via API ([lego-mcp/src/index.ts](lego-mcp/src/index.ts)).
- Supports simulation and live hardware modes.

## 🗣️ Voice & Agent Management

- Voice agent configuration editor ([lego-web/components/voice/agenteditor.tsx](lego-web/components/voice/agenteditor.tsx)).
- Agent selection, creation, and management via web UI.
- Real-time effort and output tracking ([lego-web/components/effortlist.tsx](lego-web/components/effortlist.tsx), [lego-web/components/output.tsx](lego-web/components/output.tsx)).

## 📡 BLE & Camera Integration

- BLE protocol support for robot communication ([lego-ble/cobs.py](lego-ble/cobs.py), [lego-ble/crc.py](lego-ble/crc.py)).
- Camera client for image/video streaming ([lego-cam/client.py](lego-cam/client.py)).

## 🌐 Web Frontend

- Interactive dashboard for agent workflows and outputs.
- Markdown and emoji rendering for agent messages ([lego-web/components/output/textoutput.tsx](lego-web/components/output/textoutput.tsx)).
- File/image picker and output modal display.

## 🧪 Testing & Extensibility

- Unit tests for agent actions and workflows.
- Easily extendable with new agents, tools, and UI components.

---

See [README.md](README.md) for getting started.