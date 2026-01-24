# Azure Setup Guide for LEGO Robot Agent

This guide explains how to set up Azure authentication and configure access to Azure resources under the `rg-legobot` resource group.

## Prerequisites

1. Azure CLI installed
2. Access to Azure subscription with the `rg-legobot` resource group
3. Python 3.10 or higher
4. Node.js 18+ (for MCP server)

## Step 1: Install Azure CLI

If you haven't already installed Azure CLI:

**Windows:**
```powershell
winget install Microsoft.AzureCLI
```

**macOS:**
```bash
brew install azure-cli
```

**Linux:**
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

For other installation methods, see: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

## Step 2: Authenticate with Azure

Run the following command to log in to Azure:

```bash
az login
```

This will open a browser window where you can authenticate with your Azure credentials.

After successful login, verify your account:

```bash
az account show
```

If you have multiple subscriptions, set the correct one:

```bash
# List all subscriptions
az account list --output table

# Set the subscription containing rg-legobot
az account set --subscription <subscription-id-or-name>
```

## Step 3: Verify Resource Group Access

Verify you have access to the `rg-legobot` resource group:

```bash
az group show --name rg-legobot
```

If this command fails, you may need to request access from your Azure administrator.

List resources in the resource group:

```bash
az resource list --resource-group rg-legobot --output table
```

## Step 4: Get Azure OpenAI Configuration

Find your Azure OpenAI resource:

```bash
az cognitiveservices account list --resource-group rg-legobot --output table
```

Get the endpoint:

```bash
az cognitiveservices account show \
  --name <your-openai-resource-name> \
  --resource-group rg-legobot \
  --query "properties.endpoint" \
  --output tsv
```

List available deployments:

```bash
az cognitiveservices account deployment list \
  --name <your-openai-resource-name> \
  --resource-group rg-legobot \
  --output table
```

## Step 5: Get Azure AI Foundry Project Configuration

Find your Azure AI Foundry project (Azure ML workspace):

```bash
az ml workspace list --resource-group rg-legobot --output table
```

Get the project connection string:

```bash
az ml workspace show \
  --name <your-project-name> \
  --resource-group rg-legobot \
  --query "discovery_url" \
  --output tsv
```

## Step 6: Configure Environment Variables

Create a `.env` file in the `lego-robot-agent` directory:

```bash
cd lego-robot-agent
cp .env.example .env
```

Edit the `.env` file with the values obtained from the previous steps:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2025-01-01-preview

# Azure AI Foundry Project Configuration
AZURE_AI_PROJECT_ENDPOINT=<your-project-discovery-url>
PROJECT_CONNECTION_STRING=<your-project-discovery-url>

# Azure Storage Configuration (optional)
SUSTINEO_STORAGE=https://your-storage-account.blob.core.windows.net/
```

## Step 7: Install Dependencies

Install the lego-robot-agent package with all dependencies:

```bash
cd lego-robot-agent
pip install -e . --pre
```

## Step 8: Start the MCP Server

The MCP server provides robot control capabilities. Start it in a separate terminal:

```bash
cd lego-mcp
npm install
npm run build
npm start
```

## Step 9: Run the Test

Now you can run the test script:

```bash
cd lego-robot-agent/src/tests
python test1_action.py
```

## Troubleshooting

### "Please run 'az login' to setup account"

**Solution:** Run `az login` to authenticate with Azure.

### "Failed to retrieve Azure token"

**Solution:** 
1. Ensure you're logged in: `az login`
2. Verify your subscription is set correctly: `az account show`
3. Check you have the correct permissions for the resource group

### "ServiceInitializationError: Please provide either api_key, ad_token or ad_token_provider"

**Solution:** 
1. Ensure Azure CLI is authenticated: `az login`
2. Verify your `.env` file has correct Azure OpenAI endpoint
3. Check that you have access to the Azure OpenAI resource

### "Cannot connect to MCP server"

**Solution:**
1. Ensure the MCP server is running in a separate terminal
2. Verify the path to the MCP server in the test script matches your installation
3. Check that Node.js is installed and the MCP server built successfully

### "Access to resource denied"

**Solution:**
1. Verify you have the correct role assignments in Azure
2. Contact your Azure administrator to grant access to the resource group
3. Ensure you're using the correct subscription

## Required Azure Permissions

To run the tests successfully, you need the following permissions in the `rg-legobot` resource group:

- **Cognitive Services User** (for Azure OpenAI)
- **Reader** (to list and view resources)
- **Azure ML Data Scientist** (for Azure AI Foundry/ML workspace)
- **Storage Blob Data Contributor** (if using blob storage)

## Additional Resources

- [Azure CLI Documentation](https://docs.microsoft.com/en-us/cli/azure/)
- [Azure OpenAI Service Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/machine-learning/)
- [Azure RBAC Documentation](https://docs.microsoft.com/en-us/azure/role-based-access-control/)
