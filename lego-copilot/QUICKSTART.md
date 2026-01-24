# LEGO Copilot - Quick Start Guide

Get your LEGO Copilot running in Microsoft Teams in 5 steps.

## 🚀 5-Minute Quick Start

### 1. Install Dependencies
```bash
cd lego-copilot
npm install
```

### 2. Set Up Environment
```bash
# Copy the sample environment file
cp .env.local.sample .env.local

# Edit .env.local and add your credentials
# Required: BOT_ID, BOT_PASSWORD, FOUNDRY_CONNECTION, TEAMS_APP_ID
```

### 3. Start the Bot
```bash
npm run dev
```

### 4. Expose Local Bot (for testing)
```bash
# In a new terminal
npm install -g ngrok
ngrok http 3978

# Copy the HTTPS URL and update your bot's messaging endpoint in Azure Portal
```

### 5. Install in Teams

**Option A: Quick Test (without icons)**
- For quick testing, you can skip creating icons and directly test using Bot Framework Emulator

**Option B: Full Teams Install**
1. Add icon files to `appPackage/` (see appPackage/ICONS-README.md)
2. Run: `./scripts/package-teams-app.sh` (or `.ps1` on Windows)
3. Upload `lego-copilot-teams-app.zip` to Teams

## 🧪 Test Your Bot

Send these messages in Teams:
- "Hello" - Should get a welcome message
- "What can you do?" - Should describe capabilities
- "Move the robot forward" - Should interact with Foundry agent

## 📋 Prerequisites Checklist

Before starting, ensure you have:
- [ ] Node.js 18+ installed
- [ ] Azure Bot registration (BOT_ID and BOT_PASSWORD)
- [ ] Azure AI Foundry connection string
- [ ] LEGO agents deployed in Foundry (run `lego-api/azureagents.py`)
- [ ] Microsoft Teams account

## 🔑 Getting Credentials

### Bot ID and Password
1. Go to [Azure Portal](https://portal.azure.com)
2. Microsoft Entra ID → App registrations → New registration
3. Copy the Application ID (BOT_ID)
4. Certificates & secrets → New client secret → Copy value (BOT_PASSWORD)

### Foundry Connection
- Get from your Azure AI Foundry project settings
- Format: `<endpoint>;<subscription-id>;<resource-group>;<project-name>`

### Teams App ID
- Generate a new GUID:
  - Online: https://guidgenerator.com/
  - PowerShell: `[guid]::NewGuid()`
  - Node: `node -e "console.log(require('crypto').randomUUID())"`

## 🐛 Common Issues

**Bot not responding?**
- Check that `npm run dev` is running
- Verify messaging endpoint is correct
- Check bot logs for errors

**"No LEGO agent available"?**
- Run `cd lego-api && python azureagents.py` to deploy agents
- Verify FOUNDRY_CONNECTION is correct

**Can't upload to Teams?**
- Make sure icon files exist in appPackage/
- Check manifest.json has valid GUID values
- Verify zip file structure

## 📚 Next Steps

- Read full [README.md](README.md) for detailed documentation
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Test with various robot commands

## 💡 Sample Commands

Try these with your bot:
- "Show me the robot's current position"
- "Turn left 45 degrees"
- "Open the gripper"
- "What objects do you see?"
- "Move to the red object"

---

**Need Help?** Check the full README.md or DEPLOYMENT.md guides.
