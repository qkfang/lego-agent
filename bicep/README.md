# Azure Infrastructure Deployment for Video Agent

This directory contains Bicep templates for deploying the Azure infrastructure required for the Content Understanding Video Agent.

## Resources Deployed

- **Azure AI Foundry Hub (v2)**: AI orchestration hub
- **Azure AI Foundry Project**: Project workspace for the video agent
- **Azure Content Understanding Service**: Service for video analysis
- **Azure OpenAI Service**: GPT-4o model for agent intelligence
- **Storage Account**: Storage for Foundry hub
- **Key Vault**: Secure storage for secrets
- **Application Insights**: Monitoring and telemetry

## Prerequisites

- Azure CLI installed (`az`)
- Azure subscription with appropriate permissions
- Contributor or Owner role on the subscription or resource group

## Deployment Steps

### 1. Login to Azure

```bash
az login
```

### 2. Set your subscription

```bash
az account set --subscription "<your-subscription-id>"
```

### 3. Create a resource group

```bash
az group create --name lego-agent-rg --location eastus
```

### 4. Deploy the Bicep template

```bash
az deployment group create \
  --resource-group lego-agent-rg \
  --template-file main.bicep \
  --parameters main.parameters.json
```

Or with inline parameters:

```bash
az deployment group create \
  --resource-group lego-agent-rg \
  --template-file main.bicep \
  --parameters foundryHubName=my-foundry-hub \
               foundryProjectName=my-video-project \
               contentUnderstandingName=my-content-understanding \
               location=eastus
```

### 5. Get deployment outputs

```bash
az deployment group show \
  --resource-group lego-agent-rg \
  --name main \
  --query properties.outputs
```

## Configuration

### Parameters

Edit `main.parameters.json` to customize the deployment:

- `foundryHubName`: Name for the Azure AI Foundry hub
- `foundryProjectName`: Name for the Foundry project
- `contentUnderstandingName`: Name for the Content Understanding service
- `location`: Azure region (default: eastus)
- `contentUnderstandingSku`: SKU for Content Understanding (S0 or F0)

### Supported Regions

Content Understanding is available in limited regions. Check the latest availability:
- East US
- West Europe
- Other regions as they become available

## Post-Deployment

After deployment, you'll need to:

1. Get the connection string for the Foundry project:
   ```bash
   az ml workspace show --name <foundryProjectName> --resource-group lego-agent-rg
   ```

2. Get the Content Understanding endpoint and key:
   ```bash
   az cognitiveservices account show --name <contentUnderstandingName> --resource-group lego-agent-rg
   az cognitiveservices account keys list --name <contentUnderstandingName> --resource-group lego-agent-rg
   ```

3. Set environment variables in your `.env` file:
   ```env
   PROJECT_CONNECTION_STRING=<from-step-1>
   CONTENT_UNDERSTANDING_ENDPOINT=<from-step-2>
   CONTENT_UNDERSTANDING_KEY=<from-step-2>
   ```

## Architecture

```
┌─────────────────────────────────────────────────┐
│         Azure AI Foundry Hub (v2)               │
│  ┌───────────────────────────────────────────┐  │
│  │   Azure AI Foundry Project                │  │
│  │                                           │  │
│  │   - Video Agent (agent-cu)                │  │
│  │   - GPT-4o Model                          │  │
│  └───────────────────────────────────────────┘  │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │   Supporting Services                     │  │
│  │   - Storage Account                       │  │
│  │   - Key Vault                             │  │
│  │   - Application Insights                  │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                      │
                      │ Uses
                      ▼
┌─────────────────────────────────────────────────┐
│   Azure Content Understanding Service           │
│   - Video Analysis                              │
│   - Transcription                               │
│   - Key Frame Extraction                        │
│   - Segment Detection                           │
└─────────────────────────────────────────────────┘
```

## Cleanup

To delete all resources:

```bash
az group delete --name lego-agent-rg --yes --no-wait
```

## Troubleshooting

### Deployment fails with "ResourceNotFound"
- Ensure you're using a supported region for Content Understanding
- Check that all required resource providers are registered

### Access denied errors
- Verify you have sufficient permissions on the subscription
- Ensure your account has Contributor or Owner role

### Content Understanding not available
- Check service availability in your region
- Verify your subscription has access to preview features

## Additional Resources

- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-foundry/)
- [Azure Content Understanding Documentation](https://learn.microsoft.com/azure/ai-services/content-understanding/)
- [Bicep Documentation](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)
