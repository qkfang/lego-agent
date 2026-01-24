"""
Simple Azure AI Projects Agent Example

This example demonstrates how to create and use an agent with the Azure AI Projects SDK.
Based on: https://github.com/MicrosoftDocs/azure-docs-sdk-python/blob/main/docs-ref-services/preview/ai-projects-readme.md

Prerequisites:
- pip install --pre azure-ai-projects azure-identity openai
- Set environment variables:
  - AZURE_AI_PROJECT_ENDPOINT: Your AI Foundry project endpoint
  - AZURE_AI_MODEL_DEPLOYMENT_NAME: The deployment name of your AI model
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity import DefaultAzureCredential


def create_simple_agent():
    """Create and interact with a simple agent."""
    
    # Get configuration from environment variables
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "https://legobot-foundry.services.ai.azure.com/api/projects/legobot-project")
    model_deployment_name = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o")
    
    if not endpoint:
        raise ValueError("AZURE_AI_PROJECT_ENDPOINT environment variable is required")
    
    # Create the AI Project client with DefaultAzureCredential
    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):
        # Get the OpenAI client for agent operations
        with project_client.get_openai_client() as openai_client:
            
            # Create an agent
            # agent = project_client.agents.create_version(
            #     agent_name="SimpleAssistant",
            #     definition=PromptAgentDefinition(
            #         model=model_deployment_name,
            #         instructions="You are a helpful assistant that answers general questions concisely.",
            #     ),
            # )

            agent = project_client.agents.get("SimpleAssistant")
            print(f"Agent created (id: {agent.id}, name: {agent.name}")
            
            try:
                # Create a conversation with an initial user message
                conversation = openai_client.conversations.create(
                    items=[
                        {"type": "message", "role": "user", "content": "What is the capital of France?"}
                    ],
                )
                print(f"Created conversation (id: {conversation.id})")
                
                # Get a response from the agent
                response = openai_client.responses.create(
                    conversation=conversation.id,
                    extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
                    input="",
                )
                print(f"Response: {response.output_text}")
                
                # Add a follow-up question to the conversation
                openai_client.conversations.items.create(
                    conversation_id=conversation.id,
                    items=[
                        {"type": "message", "role": "user", "content": "What is its population?"}
                    ],
                )
                print("Added follow-up question to conversation")
                
                # Get another response
                response = openai_client.responses.create(
                    conversation=conversation.id,
                    extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
                    input="",
                )
                print(f"Response: {response.output_text}")
                
                # Clean up the conversation
                openai_client.conversations.delete(conversation_id=conversation.id)
                print("Conversation deleted")
                
            finally:
                # Clean up the agent
                # project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
                print("Agent deleted")


def simple_responses_example():
    """Simple example using responses API without creating an agent."""
    
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "https://legobot-foundry.services.ai.azure.com/api/projects/legobot-project")
    model_deployment_name = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o")
    
    if not endpoint:
        raise ValueError("AZURE_AI_PROJECT_ENDPOINT environment variable is required")
    
    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):
        with project_client.get_openai_client() as openai_client:
            # Simple single-turn response
            response = openai_client.responses.create(
                model=model_deployment_name,
                input="What is the size of France in square miles?",
            )
            print(f"Response: {response.output_text}")
            
            # Multi-turn conversation using previous_response_id
            response = openai_client.responses.create(
                model=model_deployment_name,
                input="And what is its capital city?",
                previous_response_id=response.id,
            )
            print(f"Follow-up response: {response.output_text}")


if __name__ == "__main__":
    print("=" * 50)
    print("Azure AI Projects - Simple Responses Example")
    print("=" * 50)
    simple_responses_example()
    
    print("\n" + "=" * 50)
    print("Azure AI Projects - Agent Example")
    print("=" * 50)
    create_simple_agent()
