import os
import json
import asyncio
from pathlib import Path
from typing import Literal
from openai import AsyncAzureOpenAI
from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Response, WebSocket, WebSocketDisconnect
from openai.types.beta.realtime.session_update_event import SessionTool

from agent.decorators import function_agents, function_calls
from storage import get_storage_client
from connection import connections
from model import Update
from telemetry import init_tracing
from voice.common import get_default_configuration_data, convert_function_params, convert_mcp_function_params
from voice.session import RealtimeSession
from voice import router as voice_configuration_router
from agent import router as agent_router
from agent.common import get_custom_agents, create_thread, get_available_agents
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from agent.common import foundry_agents, custom_agents, get_custom_agents

# Stub for shared module - for compatibility while agent_framework is not fully integrated
class SharedStub:
    """Shared module stub for managing global state.
    
    Provides interface for MCP session, robot tools, and other shared resources.
    """
    foundryAgents = []
    mcprobot = None
    robotmcptools = None
    sessionrt = None
shared = SharedStub()
            
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

AZURE_VOICE_ENDPOINT = os.getenv("AZURE_VOICE_ENDPOINT") or ""
COSMOSDB_ENDPOINT = os.getenv("COSMOSDB_ENDPOINT", "fake_connection")
SUSTINEO_STORAGE = os.environ.get("SUSTINEO_STORAGE", "EMPTY")
LOCAL_TRACING_ENABLED = os.getenv("LOCAL_TRACING_ENABLED", "false").lower() == "true"

init_tracing(local_tracing=LOCAL_TRACING_ENABLED)

base_path = Path(__file__).parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Load agents from prompty files in directory
        await get_custom_agents()
        
        # Microsoft Agent Framework - agents are created on-demand
        # No need to pre-fetch agents from a service
        # Commented out temporarily due to agent-framework version mismatch
        # shared.foundryAgents = [agent async for agent in shared.project_client.agents.list(limit=100)]
        shared.foundryAgents = []
        
        # Setup MCP connection for robot tools in mock mode
        import platform
        if platform.system() == "Windows":
            mcp_path = "c:\\repo\\lego-agent\\lego-mcp\\build\\index.js"
        else:
            mcp_path = "/home/runner/work/lego-agent/lego-agent/lego-mcp/build/index.js"
        
        # Check if MCP build exists
        if not os.path.exists(mcp_path):
            print(f"Warning: MCP server not found at {mcp_path}. Robot tools will not be available.")
        else:
            print(f"Initializing MCP server from {mcp_path} with isMock=true")
            mcp_server_params = StdioServerParameters(
                command="node",
                args=[mcp_path],
                env={
                    "IS_MOCK": "true",
                    "DEFAULT_ROBOT_ID": "robot_b"
                },
            )
            
            async with stdio_client(mcp_server_params) as (read_stream, write_stream):
                from mcp.client.session import ClientSession
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    shared.mcprobot = session
                    tools_result = await session.list_tools()
                    mcp_tools = tools_result.tools if hasattr(tools_result, 'tools') else []
                    print(f"MCP tools initialized: {len(mcp_tools)} tools available")
                    # Store tools info for later use
                    shared.robotmcptools = mcp_tools
                
        yield
    finally:
        await connections.clear()


app = FastAPI(lifespan=lifespan, redirect_slashes=False)

app.include_router(voice_configuration_router, tags=["voice"])
app.include_router(agent_router, tags=["agents"])



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimpleMessage(BaseModel):
    name: str
    text: str


@app.get("/health")
async def health(response: Response):
    response.status_code = 200
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/images/{image_id}")
async def get_image(image_id: str):
    async with get_storage_client("sustineo") as container_client:
        # get the blob client for the image
        blob_client = container_client.get_blob_client(f"images/{image_id}")

        # check if the blob exists
        if not await blob_client.exists():
            return Response(status_code=404, content="Image not found")

        # return bytes as png image
        image_data = await blob_client.download_blob()
        image_bytes = await image_data.readall()
        return Response(content=image_bytes, media_type="image/jpg")


@app.websocket("/api/voice/{id}")
async def voice_endpoint(id: str, websocket: WebSocket):

    connection = await connections.connect(id, websocket)

    try:
        # Use DefaultAzureCredential for managed identity authentication
        azure_credential = DefaultAzureCredential()
        
        async def token_provider():
            token = await azure_credential.get_token("https://cognitiveservices.azure.com/.default")
            return token.token
        
        client = AsyncAzureOpenAI(
            azure_endpoint=AZURE_VOICE_ENDPOINT,
            azure_ad_token_provider=token_provider,
            api_version="2025-04-01-preview",
        )
        async with client.beta.realtime.connect(
            model="gpt-realtime", extra_query={"debug": "elvis"}
        ) as realtime_client:

            # get current username and receive any parameters
            user_message = await connection.receive_json()

            if user_message["type"] != "settings":
                await connection.send_browser_update(
                    Update.exception(
                        id=id,
                        error="Invalid message type",
                        content="Expected SettingsUpdate, got {settings.type}",
                    )
                )

                await connection.close()
                return

            settings = user_message["settings"]

            print(
                "Starting voice session with settings:\n",
                json.dumps(settings, indent=2),
            )

            # create voice system message
            args = {
                "customer": settings["user"] if "user" in settings else "unnamed user"
            }
            if "date" in settings:
                args["date"] = settings["date"]
            if "time" in settings:
                args["time"] = settings["time"]

            prompt_settings = await get_default_configuration_data(**args)
            if prompt_settings is None:
                await connection.send_browser_update(
                    Update.exception(
                        id=id,
                        error="No default configuration found.",
                        content="Please contact support.",
                    )
                )
                await connection.close()
                return

            # Add tools from custom_agents to prompt_settings.tools
            cagent = await get_custom_agents()
            for agent in custom_agents:
                if hasattr(agent, "tools") and agent.tools:
                    prompt_settings.tools.extend(agent.tools)

            for agent_id, agent in function_agents.items():
                stool = SessionTool(
                        type="function",
                        name=agent.name,
                        description=agent.description,
                        parameters=convert_function_params(agent.parameters),
                    )
                prompt_settings.tools.append(stool)

            for tool in prompt_settings.tools:
                print(f"ToolName: {tool.name}")

            # create a new thread in the foundry
            thread_id = await create_thread()

            global session
            session = RealtimeSession(
                realtime=realtime_client,
                client=connection,
                thread_id=thread_id,
            )
            shared.sessionrt = session  # set the session in api.agent

            detection_type: Literal["semantic_vad", "server_vad"] = (
                settings["detection_type"]
                if "detection_type" in settings
                else "server_vad"
            )

            eagerness: Literal["low", "medium", "high", "auto"] = (
                settings["eagerness"] if "eagerness" in settings else "auto"
            )

            await session.update_realtime_session(
                instructions=prompt_settings.system_message,
                detection_type=detection_type,
                transcription_model=(
                    settings["transcription_model"]
                    if "transcription_model" in settings
                    else "whisper-1"
                ),
                threshold=settings["threshold"] if "threshold" in settings else 0.8,
                silence_duration_ms=(
                    settings["silence_duration"]
                    if "silence_duration_ms" in settings
                    else 500
                ),
                prefix_padding_ms=(
                    settings["prefix_padding"]
                    if "prefix_padding_ms" in settings
                    else 300
                ),
                eagerness=eagerness,
                voice=settings["voice"] if "voice" in settings else "sage",
                tools=prompt_settings.tools,
            )

            tasks = [
                asyncio.create_task(session.receive_realtime()),
                asyncio.create_task(session.receive_client()),
            ]
            await asyncio.gather(*tasks)

    except WebSocketDisconnect as e:
        connections.remove(id)
        print("Voice Socket Disconnected", e)


FastAPIInstrumentor.instrument_app(app, exclude_spans=["send", "receive"])
