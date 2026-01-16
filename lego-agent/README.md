# Azure Content Understanding Video Agent (agent-cu)

A video analysis agent using Azure Content Understanding service and Microsoft Agent Framework.

## Overview

This agent can:
- Consume videos via URL
- Transcribe video content
- Analyze and explain what happened in the video
- Extract key frames and segments
- Provide detailed summaries

## Setup

### Prerequisites

- Python 3.8+
- Azure subscription
- Azure AI Foundry project
- Azure Content Understanding service

### Environment Variables

Create a `.env` file with the following variables:

```env
PROJECT_CONNECTION_STRING=<your-azure-ai-projects-connection-string>
CONTENT_UNDERSTANDING_ENDPOINT=<your-content-understanding-endpoint>
CONTENT_UNDERSTANDING_KEY=<your-content-understanding-api-key>
```

### Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Example

```python
import asyncio
from agent_cu import ContentUnderstandingVideoAgent

async def main():
    agent = ContentUnderstandingVideoAgent()
    await agent.init()
    
    video_url = "https://example.com/video.mp4"
    query = "What happened in this video?"
    
    result = await agent.execute(query, video_url)
    print(result)
    
    await agent.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Analyzing a Video

```python
# Analyze a video and get transcript
result = await agent.analyze_video_from_url("https://example.com/video.mp4")

print("Transcript:", result["transcript"])
print("Summary:", result["summary"])
print("Segments:", len(result["segments"]))
print("Key Frames:", len(result["key_frames"]))
```

## Deployment

See the `bicep` directory in the repository root for Azure infrastructure deployment templates.

## Features

- **Video Transcription**: Automatically generates transcripts from video content
- **Segment Detection**: Identifies logical segments in the video
- **Key Frame Extraction**: Extracts important frames from the video
- **Content Analysis**: Provides detailed analysis of video content
- **Microsoft Agent Framework**: Built on Microsoft Agent Framework for integration with other agents

## Architecture

The agent uses:
- Azure AI Projects for agent orchestration
- Azure Content Understanding service for video analysis
- Microsoft Agent Framework (Semantic Kernel) for agent capabilities
- Async/await patterns for efficient processing
