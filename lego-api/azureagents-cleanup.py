import os
import json
from dotenv import load_dotenv

load_dotenv()

"""
Azure AI Foundry Agent Cleanup Script

Note: With Microsoft Agent Framework, agents are created on-demand and are 
not persisted in a service. This cleanup script is no longer needed for the 
new framework.

If you need to clean up old Azure AI Foundry agents, you can use the Azure 
AI Foundry portal or the azure-ai-projects SDK directly.

The Microsoft Agent Framework uses Azure OpenAI directly without the need 
for pre-registered agents. Agents are created in-memory when needed and 
don't require cleanup.
"""

print("Microsoft Agent Framework Migration Notice:")
print("=" * 50)
print("Agents are now created on-demand and don't persist in a service.")
print("This cleanup script is no longer needed for the new framework.")
print("")
print("If you need to clean up old Azure AI Foundry agents, use:")
print("  - Azure AI Foundry portal")
print("  - azure-ai-projects SDK (pip install azure-ai-projects)")
print("=" * 50)
