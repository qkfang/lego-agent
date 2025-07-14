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
from util.storage import get_storage_client
from connection import connections
from model import Update
from telemetry import init_tracing
from voice.common import get_default_configuration_data, convert_function_params, convert_mcp_function_params
from voice.session import RealtimeSession
from voice import router as voice_configuration_router
from agent import router as agent_router
from agent.common import get_custom_agents, create_foundry_thread
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from semantic_kernel.connectors.mcp import MCPStdioPlugin
from agent.common import foundry_agents, custom_agents, get_foundry_agents, get_custom_agents
import shared
            
from dotenv import load_dotenv

load_dotenv()

AZURE_VOICE_ENDPOINT = os.getenv("AZURE_VOICE_ENDPOINT") or ""
AZURE_VOICE_KEY = os.getenv("AZURE_VOICE_KEY", "fake_key")
COSMOSDB_CONNECTION = os.getenv("COSMOSDB_CONNECTION", "fake_connection")
SUSTINEO_STORAGE = os.environ.get("SUSTINEO_STORAGE", "EMPTY")
LOCAL_TRACING_ENABLED = os.getenv("LOCAL_TRACING_ENABLED", "false").lower() == "true"

init_tracing(local_tracing=LOCAL_TRACING_ENABLED)

base_path = Path(__file__).parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Load agents from prompty files in directory
        await get_custom_agents()
        shared.foundryAgents = (await shared.project_client.agents.list_agents(limit=100)).data
        
        async with (
            MCPStdioPlugin(
                name="robotmcp",
                description="Robot MCP Agents and run query, call this plugin.",
                command="node",
                args= ["D:\\gh-repo\\lego-agent\\lego-mcp\\build\\index.js"],
                env={
                    "PROJECT_CONNECTION_STRING": "",
                    "DEFAULT_ROBOT_ID": "robot_b"
                },
            ) as lego_robot_mcp
        ):
            shared.mcprobot = lego_robot_mcp  # set the value in api.agent
            shared.mcprobottools = await lego_robot_mcp.session.list_tools()
                
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
        client = AsyncAzureOpenAI(
            azure_endpoint=AZURE_VOICE_ENDPOINT,
            api_key=AZURE_VOICE_KEY,
            api_version="2025-04-01-preview",
        )
        async with client.beta.realtime.connect(
            model="gpt-4o-realtime-preview", extra_query={"debug": "elvis"}
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
            thread_id = await create_foundry_thread()

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
