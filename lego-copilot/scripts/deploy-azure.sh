#!/bin/bash

# Script to deploy LEGO Copilot to Azure App Service
# Usage: ./deploy-azure.sh <app-name> <resource-group>

set -e

# Configuration
APP_NAME=${1:-lego-copilot-bot}
RESOURCE_GROUP=${2:-lego-copilot-rg}
LOCATION=${3:-eastus}
APP_SERVICE_PLAN="${APP_NAME}-plan"

echo "=========================================="
echo "LEGO Copilot - Azure Deployment Script"
echo "=========================================="
echo ""
echo "App Name: $APP_NAME"
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo ""

# Check if logged in to Azure
echo "Checking Azure login status..."
az account show > /dev/null 2>&1 || {
    echo "Not logged in to Azure. Please run 'az login' first."
    exit 1
}

echo "✓ Azure login verified"
echo ""

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "Error: .env.local file not found"
    echo "Please create .env.local with your configuration"
    exit 1
fi

# Load environment variables
source .env.local

# Verify required variables
if [ -z "$BOT_ID" ] || [ -z "$BOT_PASSWORD" ] || [ -z "$FOUNDRY_CONNECTION" ]; then
    echo "Error: Required environment variables not set in .env.local"
    echo "Required: BOT_ID, BOT_PASSWORD, FOUNDRY_CONNECTION"
    exit 1
fi

echo "✓ Environment variables verified"
echo ""

# Create resource group
echo "Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION > /dev/null
echo "✓ Resource group created/verified"

# Create App Service plan
echo "Creating App Service plan..."
az appservice plan create \
    --name $APP_SERVICE_PLAN \
    --resource-group $RESOURCE_GROUP \
    --sku B1 \
    --is-linux \
    > /dev/null
echo "✓ App Service plan created/verified"

# Create Web App
echo "Creating Web App..."
az webapp create \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --name $APP_NAME \
    --runtime "NODE:18-lts" \
    > /dev/null
echo "✓ Web App created/verified"

# Configure app settings
echo "Configuring app settings..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
        BOT_ID="$BOT_ID" \
        BOT_PASSWORD="$BOT_PASSWORD" \
        FOUNDRY_CONNECTION="$FOUNDRY_CONNECTION" \
        PORT=8080 \
    > /dev/null
echo "✓ App settings configured"

# Create deployment package
echo "Creating deployment package..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."
zip -r deploy.zip . -x "node_modules/*" -x ".env.local" -x ".git/*" -x "*.zip" -x "scripts/*" > /dev/null
echo "✓ Deployment package created"

# Deploy code
echo "Deploying code to Azure..."
az webapp deploy \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --src-path deploy.zip \
    --type zip \
    > /dev/null
echo "✓ Code deployed"

# Clean up
rm deploy.zip

# Get app URL
APP_URL="https://${APP_NAME}.azurewebsites.net"
MESSAGING_ENDPOINT="${APP_URL}/api/messages"

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "App URL: $APP_URL"
echo "Health Check: ${APP_URL}/health"
echo "Messaging Endpoint: $MESSAGING_ENDPOINT"
echo ""
echo "Next Steps:"
echo "1. Update your bot's messaging endpoint in Azure Portal:"
echo "   $MESSAGING_ENDPOINT"
echo "2. Wait a few moments for the app to start"
echo "3. Test the health endpoint: curl ${APP_URL}/health"
echo "4. Test your bot in Teams"
echo ""
