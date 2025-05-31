import os
import json
from azure.ai.projects.aio import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from semantic_kernel.connectors.mcp import MCPStdioPlugin
from semantic_kernel.agents.azure_ai.azure_ai_agent import AzureAIAgent, AzureAIAgentSettings

from opentelemetry._logs import set_logger_provider
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, ConsoleLogExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk.metrics.view import DropAggregation, View
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace import set_tracer_provider
import asyncio

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str="eastus2.api.azureml.ms;79b9afaa-2d77-4d1e-b902-98df2bd3b3d6;rg-agent100;mamimezf5xgqov-aiproject" # os.environ["PROJECT_CONNECTION_STRING"]
)

resource = Resource.create({ResourceAttributes.SERVICE_NAME: "telemetry-console-quickstart"})

def set_up_tracing():
    exporter = ConsoleSpanExporter()

    # Initialize a trace provider for the application. This is a factory for creating tracers.
    tracer_provider = TracerProvider(resource=resource)
    # Span processors are initialized with an exporter which is responsible
    # for sending the telemetry data to a particular backend.
    tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
    # Sets the global default tracer provider
    set_tracer_provider(tracer_provider)


async def run(prompt: str, lego_robot_mcp):
    set_up_tracing()
    await lego_robot_mcp.connect()
    agentdef = await project_client.agents.create_agent(
        model="gpt-4o" , #""os.environ["MODEL_DEPLOYMENT_NAME"],
        name="lego-api333",
        instructions="You are a helpful assistant. ",
    )
    # [END create_agent_with_azure_ai_search_tool]
    # print(f"Created agent, ID: {agentdef.id}")

    agent = AzureAIAgent(
        client=project_client,
        definition=agentdef,
        plugins=[lego_robot_mcp],  # Add the plugin to the agent
        
    )

    # Create thread for communication
    thread = None

    async for response in agent.invoke(
                        messages=prompt,
                        thread=thread,
                    ):
        print(f"# {response.name}: {response}")
        thread = response.thread
