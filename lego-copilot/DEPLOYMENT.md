# LEGO Copilot Deployment Guide

This guide provides step-by-step instructions for deploying the LEGO Copilot to Microsoft Teams.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Azure Bot Registration](#azure-bot-registration)
3. [Local Development Setup](#local-development-setup)
4. [Production Deployment](#production-deployment)
5. [Teams App Installation](#teams-app-installation)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting, ensure you have:

- ✅ Azure subscription with appropriate permissions
- ✅ Node.js 18+ installed
- ✅ Microsoft Teams account
- ✅ Azure AI Foundry project with LEGO agents deployed
- ✅ Git (for cloning repository)

## Azure Bot Registration

### Step 1: Create App Registration

1. Navigate to [Azure Portal](https://portal.azure.com)
2. Go to **Microsoft Entra ID** → **App registrations**
3. Click **+ New registration**
4. Fill in the details:
   - Name: `LEGO Copilot`
   - Supported account types: **Accounts in any organizational directory (Any Microsoft Entra ID tenant - Multitenant)**
   - Redirect URI: Leave blank
5. Click **Register**
6. **Copy the Application (client) ID** - This is your `BOT_ID`

### Step 2: Create Client Secret

1. In your app registration, go to **Certificates & secrets**
2. Click **+ New client secret**
3. Description: `LEGO Copilot Secret`
4. Expires: Choose appropriate duration (e.g., 24 months)
5. Click **Add**
6. **Copy the secret Value immediately** - This is your `BOT_PASSWORD`
   - ⚠️ **Important**: You cannot view the secret value again after leaving this page

### Step 3: Create Bot Channels Registration

1. In Azure Portal, search for **Azure Bot**
2. Click **+ Create**
3. Fill in the details:
   - Bot handle: `lego-copilot` (must be globally unique)
   - Subscription: Select your subscription
   - Resource group: Create new or use existing
   - Pricing tier: F0 (Free) or S1 (Standard)
   - Microsoft App ID: **Use existing app registration**
   - App ID: Paste your `BOT_ID` from Step 1
4. Click **Review + create** → **Create**

### Step 4: Configure Messaging Endpoint

After the bot is created:

1. Go to your Bot resource
2. Navigate to **Configuration** → **Settings**
3. Set **Messaging endpoint**:
   - For local testing: `https://your-ngrok-url.ngrok.io/api/messages`
   - For production: `https://your-app-name.azurewebsites.net/api/messages`
4. Click **Apply**

### Step 5: Add Microsoft Teams Channel

1. In your Bot resource, go to **Channels**
2. Click on **Microsoft Teams** icon
3. Click **Apply**
4. Accept the terms of service

## Local Development Setup

### Step 1: Install Dependencies

```bash
cd lego-copilot
npm install
```

### Step 2: Configure Environment

Create `.env.local` file:

```bash
cp .env.local.sample .env.local
```

Edit `.env.local` with your values:

```env
BOT_ID=your-application-client-id
BOT_PASSWORD=your-client-secret-value
FOUNDRY_CONNECTION=your-foundry-connection-string
TEAMS_APP_ID=12345678-1234-1234-1234-123456789abc  # Generate new GUID
PORT=3978
```

To generate a TEAMS_APP_ID:
- Online: Use https://guidgenerator.com/
- PowerShell: `[guid]::NewGuid()`
- Node.js: `node -e "console.log(require('crypto').randomUUID())"`

### Step 3: Start Local Server

```bash
npm run dev
```

You should see:
```
restify listening to http://[::]:3978
```

### Step 4: Setup ngrok for Local Testing

Install ngrok:
```bash
npm install -g ngrok
```

Start ngrok tunnel:
```bash
ngrok http 3978
```

Copy the HTTPS forwarding URL (e.g., `https://abc123.ngrok.io`)

Update your bot's messaging endpoint in Azure Portal to:
```
https://abc123.ngrok.io/api/messages
```

## Production Deployment

### Option A: Deploy to Azure App Service

#### Using Azure CLI

```bash
# Login
az login

# Create resource group
az group create --name lego-copilot-rg --location eastus

# Create App Service plan
az appservice plan create \
  --name lego-copilot-plan \
  --resource-group lego-copilot-rg \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --resource-group lego-copilot-rg \
  --plan lego-copilot-plan \
  --name lego-copilot-bot \
  --runtime "NODE:18-lts"

# Configure app settings
az webapp config appsettings set \
  --resource-group lego-copilot-rg \
  --name lego-copilot-bot \
  --settings \
    BOT_ID="your-bot-id" \
    BOT_PASSWORD="your-bot-password" \
    FOUNDRY_CONNECTION="your-connection-string" \
    PORT=8080

# Deploy code
cd lego-copilot
zip -r deploy.zip . -x "node_modules/*" -x ".env.local" -x ".git/*"
az webapp deploy \
  --resource-group lego-copilot-rg \
  --name lego-copilot-bot \
  --src-path deploy.zip \
  --type zip
```

#### Update Bot Messaging Endpoint

Update your bot's messaging endpoint to:
```
https://lego-copilot-bot.azurewebsites.net/api/messages
```

### Option B: Deploy Using Docker

```bash
# Build image
docker build -t lego-copilot .

# Test locally
docker run -p 3978:3978 --env-file .env.local lego-copilot

# Push to Azure Container Registry
az acr login --name <your-acr>
docker tag lego-copilot <your-acr>.azurecr.io/lego-copilot:latest
docker push <your-acr>.azurecr.io/lego-copilot:latest

# Deploy to Azure Container Instances
az container create \
  --resource-group lego-copilot-rg \
  --name lego-copilot \
  --image <your-acr>.azurecr.io/lego-copilot:latest \
  --dns-name-label lego-copilot \
  --ports 3978 \
  --environment-variables \
    BOT_ID="your-bot-id" \
    BOT_PASSWORD="your-bot-password" \
    FOUNDRY_CONNECTION="your-connection-string" \
    PORT=3978
```

## Teams App Installation

### Step 1: Prepare App Icons

Add two icon files to `appPackage/`:
- `color.png` - 192x192 pixels, color icon
- `outline.png` - 32x32 pixels, transparent outline

### Step 2: Update Manifest

Edit `appPackage/manifest.json`:

Replace placeholder tokens:
```json
"id": "12345678-1234-1234-1234-123456789abc",  // Your TEAMS_APP_ID
"botId": "your-application-client-id"           // Your BOT_ID
```

### Step 3: Package the App

**Using Scripts:**

Linux/Mac:
```bash
./scripts/package-teams-app.sh
```

Windows:
```powershell
.\scripts\package-teams-app.ps1
```

**Manual Method:**
```bash
cd appPackage
zip -r ../lego-copilot-teams-app.zip manifest.json color.png outline.png
```

### Step 4: Upload to Teams

1. Open **Microsoft Teams**
2. Click **Apps** in the left sidebar
3. Click **Manage your apps** (bottom left)
4. Click **Upload an app** → **Upload a custom app**
5. Select `lego-copilot-teams-app.zip`
6. Click **Add** to install

### Step 5: Start Chatting

1. Find **LEGO Copilot** in your Teams apps
2. Click **Add** to start a personal chat
3. Type a message to test: "Hello, what can you do?"

## Verification

### Test Bot Response

Send these test messages:

1. **Basic greeting**: "Hello"
   - Expected: Welcome message

2. **Robot command**: "Move the robot forward"
   - Expected: Response from Foundry agent

3. **Status query**: "What's the robot status?"
   - Expected: Agent response with status information

### Check Logs

**Local development:**
- Check console output for errors
- Look for "User message:" entries

**Azure App Service:**
```bash
az webapp log tail --resource-group lego-copilot-rg --name lego-copilot-bot
```

### Test Health Endpoint

```bash
curl https://your-bot-url/health
```

Expected response:
```json
{"status":"healthy"}
```

## Troubleshooting

### Bot Doesn't Respond in Teams

**Check:**
1. Bot service is running (local or Azure)
2. Messaging endpoint is correct and accessible
3. BOT_ID and BOT_PASSWORD are correct
4. Teams channel is enabled in Azure Bot

**Debug:**
```bash
# Test messaging endpoint
curl -X POST https://your-endpoint/api/messages \
  -H "Content-Type: application/json" \
  -d '{"type":"message","text":"test"}'
```

### "No LEGO agent is currently available"

**Solution:**
1. Verify FOUNDRY_CONNECTION is correct
2. Deploy LEGO agents using `lego-api/azureagents.py`:
   ```bash
   cd lego-api
   python azureagents.py
   ```
3. Check agent exists in Azure AI Foundry portal
4. Verify Azure credentials have access

### Authentication Errors

**Common causes:**
- Wrong BOT_PASSWORD
- Expired client secret
- Missing Azure permissions

**Solution:**
1. Generate new client secret in Azure Portal
2. Update BOT_PASSWORD in configuration
3. Restart bot service

### Teams Upload Failed

**Error: "Manifest parsing failed"**
- Check JSON syntax in manifest.json
- Validate GUID format for id and botId

**Error: "Icons not found"**
- Ensure color.png and outline.png exist
- Check file dimensions (192x192 and 32x32)

**Error: "Package validation failed"**
- Verify zip contains manifest.json in root
- Remove extra directories from zip

### Bot Service Won't Start

**Check:**
```bash
# Verify Node.js version
node --version  # Should be 18+

# Check dependencies
npm install

# Check environment
cat .env.local  # Verify all variables set
```

**Common issues:**
- Missing dependencies: Run `npm install`
- Port already in use: Change PORT in .env.local
- Missing .env.local: Copy from .env.local.sample

## Next Steps

After successful deployment:

1. **Test with multiple users** to verify thread isolation
2. **Configure additional bot capabilities** (file upload, adaptive cards)
3. **Monitor usage** in Azure Portal
4. **Set up Application Insights** for telemetry
5. **Add more LEGO agents** for advanced features

## Support

For help:
- Check main repository issues
- Review Azure Bot Service documentation
- Test with Bot Framework Emulator for detailed debugging

---

**Security Note**: Never commit `.env.local` or expose credentials in logs. Use Azure Key Vault for production secrets.
