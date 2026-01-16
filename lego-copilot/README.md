# LEGO Copilot for Microsoft Teams

A Microsoft Teams bot that integrates with Azure AI Foundry Agents to provide an intelligent interface for controlling and interacting with LEGO robots.

## 🤖 Overview

The LEGO Copilot is a conversational AI assistant that can be deployed to Microsoft Teams. It connects to the Azure AI Foundry Agent service (specifically the LEGO orchestrator agent) to enable natural language robot control and interaction.

## ✨ Features

- **Natural Language Interface**: Chat with your LEGO robot using simple commands
- **Teams Integration**: Works seamlessly in Microsoft Teams (personal, team, and group chats)
- **Azure AI Foundry**: Leverages powerful AI agents for intelligent robot control
- **Real-time Communication**: Instant responses and robot status updates
- **Multi-user Support**: Each user gets their own conversation thread

## 📋 Prerequisites

Before you begin, ensure you have:

- **Node.js 18+** installed
- **Microsoft Teams** account
- **Azure subscription** with:
  - Azure AI Foundry project (with LEGO agents deployed)
  - Bot Channels Registration or Microsoft Entra App Registration
- **Teams App ID** (generate a new GUID)

## 🛠️ Setup Instructions

### 1. Clone and Install

```bash
cd lego-copilot
npm install
```

### 2. Configure Environment Variables

Copy the sample environment file and fill in your credentials:

```bash
cp .env.local.sample .env.local
```

Edit `.env.local` with your values:

```env
# Bot Configuration
BOT_ID=your-bot-app-id
BOT_PASSWORD=your-bot-app-password

# Azure AI Foundry Connection
FOUNDRY_CONNECTION=your-foundry-connection-string
# OR
PROJECT_CONNECTION_STRING=your-project-connection-string

# Teams App ID (generate new GUID)
TEAMS_APP_ID=12345678-1234-1234-1234-123456789abc

# Server Port
PORT=3978
```

### 3. Create Bot Registration in Azure

You need to register your bot with Azure Bot Service:

#### Option A: Using Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Create a new **Microsoft Entra App Registration**:
   - Navigate to Microsoft Entra ID → App registrations → New registration
   - Name: "LEGO Copilot"
   - Supported account types: Multi-tenant
   - Note the Application (client) ID - this is your `BOT_ID`
3. Create a client secret:
   - Go to Certificates & secrets → New client secret
   - Copy the secret value - this is your `BOT_PASSWORD`
4. Create a **Bot Channels Registration**:
   - Search for "Bot Channels Registration" in Azure Portal
   - Create new bot
   - Use the App ID from step 2
   - Messaging endpoint: `https://your-domain.com/api/messages`
5. Add Microsoft Teams channel:
   - In your bot resource, go to Channels
   - Add Microsoft Teams channel

#### Option B: Using Azure CLI

```bash
# Create app registration
az ad app create --display-name "LEGO Copilot"

# Create bot
az bot create --resource-group <your-rg> --name lego-copilot --kind bot --endpoint https://your-domain.com/api/messages

# Add Teams channel
az bot msteams create --resource-group <your-rg> --name lego-copilot
```

### 4. Configure Teams App Manifest

Update the placeholder values in `appPackage/manifest.json`:

- Replace `${{TEAMS_APP_ID}}` with your generated GUID
- Replace `${{BOT_ID}}` with your Bot App ID

Or use the provided script (see Deployment Scripts section).

### 5. Add Bot Icons

Add two icon files to the `appPackage` directory:

- `color.png` - 192x192 color icon
- `outline.png` - 32x32 outline icon

You can create simple placeholder icons or design custom ones for your bot.

## 🏃‍♂️ Running the Bot

### Development Mode (with auto-reload)

```bash
npm run dev
```

### Production Mode

```bash
npm start
```

The bot will start on port 3978 (or the PORT specified in .env.local).

## 📦 Deploying to Microsoft Teams

### Local Testing with ngrok

For local development and testing:

1. Install [ngrok](https://ngrok.com/):
   ```bash
   npm install -g ngrok
   ```

2. Start your bot:
   ```bash
   npm run dev
   ```

3. In a new terminal, start ngrok:
   ```bash
   ngrok http 3978
   ```

4. Copy the HTTPS forwarding URL (e.g., `https://abc123.ngrok.io`)

5. Update your bot's messaging endpoint in Azure Portal:
   - Go to your Bot Channels Registration
   - Update Messaging endpoint to: `https://abc123.ngrok.io/api/messages`

6. Create and upload the Teams app package (see below)

### Create Teams App Package

1. **Manual Method**:
   - Zip the contents of the `appPackage` folder:
     ```bash
     cd appPackage
     zip -r ../lego-copilot.zip manifest.json color.png outline.png
     cd ..
     ```

2. **Using Scripts** (if provided):
   ```bash
   npm run package
   ```

### Upload to Teams

1. Open Microsoft Teams
2. Click on **Apps** in the left sidebar
3. Click **Manage your apps** → **Upload an app**
4. Select **Upload a custom app**
5. Choose the `lego-copilot.zip` file
6. Click **Add** to install the bot

The bot will now appear in your Teams apps and you can start chatting!

## 🚀 Deployment to Azure

For production deployment:

### 1. Deploy to Azure App Service

```bash
# Login to Azure
az login

# Create resource group (if needed)
az group create --name lego-copilot-rg --location eastus

# Create App Service plan
az appservice plan create --name lego-copilot-plan --resource-group lego-copilot-rg --sku B1 --is-linux

# Create Web App
az webapp create --resource-group lego-copilot-rg --plan lego-copilot-plan --name lego-copilot-bot --runtime "NODE:18-lts"

# Configure app settings
az webapp config appsettings set --resource-group lego-copilot-rg --name lego-copilot-bot --settings \
  BOT_ID="your-bot-id" \
  BOT_PASSWORD="your-bot-password" \
  FOUNDRY_CONNECTION="your-connection-string" \
  PORT=8080

# Deploy code
cd lego-copilot
zip -r deploy.zip . -x "node_modules/*" -x ".env.local"
az webapp deploy --resource-group lego-copilot-rg --name lego-copilot-bot --src-path deploy.zip --type zip
```

### 2. Update Bot Messaging Endpoint

Update your bot's messaging endpoint to point to your Azure Web App:

```
https://lego-copilot-bot.azurewebsites.net/api/messages
```

### 3. Alternative: Deploy Using Docker

```bash
# Build Docker image
docker build -t lego-copilot .

# Run locally
docker run -p 3978:3978 --env-file .env.local lego-copilot

# Push to Azure Container Registry
az acr login --name <your-acr>
docker tag lego-copilot <your-acr>.azurecr.io/lego-copilot:latest
docker push <your-acr>.azurecr.io/lego-copilot:latest

# Deploy to Azure Container Instances or Azure App Service
```

## 🧪 Testing the Bot

### Using Bot Framework Emulator

1. Download [Bot Framework Emulator](https://github.com/microsoft/BotFramework-Emulator)
2. Open the emulator
3. Click "Open Bot"
4. Enter bot URL: `http://localhost:3978/api/messages`
5. Enter your Bot ID and Password
6. Start chatting!

### Sample Conversations

Try these commands with your LEGO Copilot:

- "Move the robot forward 10 centimeters"
- "Turn left 90 degrees"
- "What's the current status of the robot?"
- "Open the gripper"
- "Show me what the robot sees"
- "Navigate to the red object"

## 📁 Project Structure

```
lego-copilot/
├── src/
│   ├── index.js              # Main bot application
│   └── foundryAgent.js       # Azure AI Foundry integration
├── appPackage/
│   ├── manifest.json         # Teams app manifest
│   ├── color.png             # 192x192 color icon
│   └── outline.png           # 32x32 outline icon
├── package.json              # Node.js dependencies
├── .env.local.sample         # Environment template
└── README.md                 # This file
```

## 🔧 Configuration

### Bot Capabilities

The bot supports:
- Personal chats
- Team channels
- Group chats

### Foundry Agent Selection

The bot automatically looks for agents in this order:
1. `lego-orchestrator` or `lego-ochestrator` (primary)
2. Any agent starting with `lego-` (fallback)

### Conversation Threading

Each user gets a separate conversation thread with the Foundry agent, ensuring isolated and personalized interactions.

## 🔍 Troubleshooting

### Bot Not Responding

1. Check that the bot service is running (`npm start`)
2. Verify environment variables are set correctly
3. Ensure messaging endpoint is accessible (check ngrok for local testing)
4. Check bot logs for errors

### Connection to Foundry Agent Failed

1. Verify `FOUNDRY_CONNECTION` or `PROJECT_CONNECTION_STRING` is correct
2. Ensure LEGO agents are deployed in Azure AI Foundry
3. Check Azure credentials have proper permissions
4. Review logs for authentication errors

### Teams Upload Failed

1. Ensure all required files are in the app package
2. Verify manifest.json has no syntax errors
3. Check that TEAMS_APP_ID is a valid GUID
4. Ensure BOT_ID matches your Azure bot registration

### Common Errors

**"No LEGO agent is currently available"**
- Deploy the LEGO agents to your Azure AI Foundry project
- Run the `azureagents.py` script in `lego-api` directory

**"The bot encountered an error"**
- Check bot logs for specific error messages
- Verify all environment variables are set
- Ensure Azure services are accessible

## 📚 Additional Resources

- [Microsoft Teams Bot Documentation](https://docs.microsoft.com/microsoftteams/platform/bots/what-are-bots)
- [Azure Bot Service](https://docs.microsoft.com/azure/bot-service/)
- [Azure AI Foundry](https://docs.microsoft.com/azure/ai-services/agents/)
- [Teams AI Library](https://github.com/microsoft/teams-ai)

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows existing style
- Environment variables are documented
- README is updated for new features

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

For issues and questions:
- Check the main LEGO Agent repository issues
- Review Azure Bot Service documentation
- Check Teams platform status

---

**Note**: Ensure you have proper permissions and subscriptions before deploying to Azure services.
