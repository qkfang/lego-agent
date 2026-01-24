"""
Azure Content Understanding Video Agent
This agent uses Azure Content Understanding service to analyze videos.
"""

import os
import json
import asyncio
import aiohttp
from typing import Optional, Dict, Any
from azure.identity import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from semantic_kernel.agents.azure_ai.azure_ai_agent import AzureAIAgent
from dotenv import load_dotenv

load_dotenv()


class ContentUnderstandingVideoAgent:
    """
    Video agent that uses Azure Content Understanding service to analyze videos.
    It can transcribe videos and explain what happened in them.
    """

    def __init__(self):
        self.project_client = None
        self.agent = None
        self.content_understanding_endpoint = os.environ.get("CONTENT_UNDERSTANDING_ENDPOINT")
        self.content_understanding_key = os.environ.get("CONTENT_UNDERSTANDING_KEY")
        self.credential = DefaultAzureCredential()
        
    async def init(self):
        """Initialize the agent with Azure AI Projects"""
        endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", os.environ.get("PROJECT_CONNECTION_STRING", ""))
        if not endpoint:
            raise ValueError("AZURE_AI_PROJECT_ENDPOINT environment variable is required")
            
        self.project_client = AIProjectClient(
            endpoint=endpoint,
            credential=self.credential,
        )
        
        # Get or create the agent
        agents_list = [agent async for agent in self.project_client.agents.list(limit=100)]
        existing_agent = None
        
        for agent in agents_list:
            if agent.name == "agent-cu":
                existing_agent = agent
                break
        
        if existing_agent:
            self.agent = AzureAIAgent(
                service=self.project_client.agents,
                id=existing_agent.id
            )
        else:
            # Create new agent
            created_agent = await self.project_client.agents.create(
                name="agent-cu",
                definition=PromptAgentDefinition(
                    model="gpt-4o",
                    temperature=0.2,
                    instructions="""
You are a video analysis assistant using Azure Content Understanding service.
You can analyze videos from URLs, transcribe them, and explain what happened in the video.
You provide detailed descriptions of video content, including:
- Full transcript of spoken content
- Key events and actions in the video
- Visual descriptions
- Summary of the video content
"""
                )
            )
            self.agent = AzureAIAgent(
                service=self.project_client.agents,
                id=created_agent.id
            )
    
    async def analyze_video_from_url(self, video_url: str) -> Dict[str, Any]:
        """
        Analyze a video from a URL using Azure Content Understanding service.
        
        Args:
            video_url: URL of the video to analyze
            
        Returns:
            Dictionary containing transcript, summary, and analysis results
        """
        if not self.content_understanding_endpoint:
            raise ValueError("CONTENT_UNDERSTANDING_ENDPOINT environment variable is required")
        if not self.content_understanding_key:
            raise ValueError("CONTENT_UNDERSTANDING_KEY environment variable is required")
        
        # Prepare the analyzer request
        analyzer_request = {
            "inputFormat": "url",
            "input": {
                "url": video_url
            },
            "analyzer": "video-default",
            "configuration": {
                "features": {
                    "transcript": True,
                    "keyFrames": True,
                    "segments": True
                }
            }
        }
        
        # Submit the analysis job
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": self.content_understanding_key
        }
        
        async with aiohttp.ClientSession() as session:
            # Submit the job
            submit_url = f"{self.content_understanding_endpoint}/contentunderstanding/analyzers:analyze?api-version=2025-11-01-preview"
            
            async with session.post(submit_url, headers=headers, json=analyzer_request) as response:
                if response.status != 202:
                    error_text = await response.text()
                    raise Exception(f"Failed to submit analysis job: {response.status} - {error_text}")
                
                # Get the operation location from the response headers
                operation_location = response.headers.get("Operation-Location")
                if not operation_location:
                    raise Exception("No Operation-Location header in response")
            
            # Poll for results
            max_attempts = 60  # 5 minutes with 5-second intervals
            attempt = 0
            
            while attempt < max_attempts:
                await asyncio.sleep(5)
                
                async with session.get(operation_location, headers=headers) as result_response:
                    if result_response.status != 200:
                        error_text = await result_response.text()
                        raise Exception(f"Failed to get analysis results: {result_response.status} - {error_text}")
                    
                    result = await result_response.json()
                    status = result.get("status")
                    
                    if status == "succeeded":
                        return self._parse_analysis_results(result)
                    elif status == "failed":
                        error_message = result.get("error", {}).get("message", "Unknown error")
                        raise Exception(f"Analysis failed: {error_message}")
                    
                    # Status is running or not started, continue polling
                    attempt += 1
            
            raise Exception("Analysis timed out after 5 minutes")
    
    def _parse_analysis_results(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the analysis results from Content Understanding service"""
        parsed = {
            "status": "success",
            "transcript": "",
            "segments": [],
            "key_frames": [],
            "summary": ""
        }
        
        # Extract transcript
        if "result" in result and "transcript" in result["result"]:
            transcript_data = result["result"]["transcript"]
            if isinstance(transcript_data, str):
                parsed["transcript"] = transcript_data
            elif isinstance(transcript_data, dict) and "text" in transcript_data:
                parsed["transcript"] = transcript_data["text"]
        
        # Extract segments
        if "result" in result and "segments" in result["result"]:
            parsed["segments"] = result["result"]["segments"]
        
        # Extract key frames
        if "result" in result and "keyFrames" in result["result"]:
            parsed["key_frames"] = result["result"]["keyFrames"]
        
        # Create summary
        summary_parts = []
        if parsed["transcript"]:
            summary_parts.append(f"Transcript: {parsed['transcript'][:500]}...")
        if parsed["segments"]:
            summary_parts.append(f"Found {len(parsed['segments'])} video segments")
        if parsed["key_frames"]:
            summary_parts.append(f"Extracted {len(parsed['key_frames'])} key frames")
        
        parsed["summary"] = " | ".join(summary_parts)
        
        return parsed
    
    async def execute(self, query: str, video_url: Optional[str] = None) -> str:
        """
        Execute a query against the video agent.
        
        Args:
            query: The user's question or request
            video_url: Optional video URL to analyze
            
        Returns:
            The agent's response
        """
        if not self.agent:
            await self.init()
        
        if video_url:
            # Analyze the video first
            try:
                analysis = await self.analyze_video_from_url(video_url)
                
                # Format the analysis for the agent to process
                context = f"""
Video Analysis Results:

Transcript:
{analysis['transcript']}

Summary: {analysis['summary']}

Number of segments: {len(analysis['segments'])}
Number of key frames: {len(analysis['key_frames'])}

User Query: {query}
"""
                # Create a thread and run the agent
                thread = await self.project_client.agents.create_thread()
                
                # Add message to thread with video analysis context
                await self.project_client.agents.create_message(
                    thread_id=thread.id,
                    role="user",
                    content=context
                )
                
                # Run the agent
                run = await self.project_client.agents.create_run(
                    thread_id=thread.id,
                    assistant_id=self.agent.id
                )
                
                # Wait for completion
                while run.status in ["queued", "in_progress", "requires_action"]:
                    await asyncio.sleep(1)
                    run = await self.project_client.agents.get_run(
                        thread_id=thread.id,
                        run_id=run.id
                    )
                
                if run.status == "completed":
                    # Get the agent's response
                    messages = await self.project_client.agents.list_messages(
                        thread_id=thread.id
                    )
                    
                    # Get the last assistant message
                    for message in messages.data:
                        if message.role == "assistant":
                            # Extract text content from the message
                            if message.content:
                                for content_item in message.content:
                                    if hasattr(content_item, 'text') and hasattr(content_item.text, 'value'):
                                        return content_item.text.value
                            break
                    
                    return "Agent completed but no response was generated."
                else:
                    return f"Agent run failed with status: {run.status}"
                    
            except Exception as e:
                return f"Error analyzing video: {str(e)}"
        else:
            return "Please provide a video URL to analyze."
    
    async def close(self):
        """Clean up resources"""
        if self.project_client:
            await self.project_client.close()


async def main():
    """Example usage of the Content Understanding Video Agent"""
    agent = ContentUnderstandingVideoAgent()
    await agent.init()
    
    # Example video URL (replace with actual video URL)
    video_url = "https://example.com/sample-video.mp4"
    
    query = "What happened in this video? Provide a detailed summary."
    
    try:
        result = await agent.execute(query, video_url)
        print("Analysis Result:")
        print(result)
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
