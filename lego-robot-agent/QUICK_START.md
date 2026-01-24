# Quick Start Guide

Follow these steps to run `test1_action.py` and access Azure resources in the `rg-legobot` resource group.

## Prerequisites Check

1. **Python 3.10+**: `python --version`
2. **Node.js 18+**: `node --version`
3. **Azure CLI**: `az --version`

## 5-Minute Setup

### Step 1: Authenticate with Azure
```bash
az login
```

A browser window will open. Sign in with your Azure credentials.

### Step 2: Verify Access to Resource Group
```bash
az group show --name rg-legobot
```

If this fails, contact your Azure admin for access.

### Step 3: Get Azure Configuration

**Get OpenAI Endpoint:**
```bash
az cognitiveservices account list --resource-group rg-legobot --output table
```

**Get AI Foundry Project:**
```bash
az ml workspace list --resource-group rg-legobot --output table
az ml workspace show --name <project-name> --resource-group rg-legobot
```

### Step 4: Configure Environment
```bash
cd lego-robot-agent
cp .env.example .env
# Edit .env with your values from Step 3
```

### Step 5: Install Dependencies
```bash
pip install -e . --pre
```

### Step 6: Build MCP Server
```bash
cd ../lego-mcp
npm install
npm run build
cd ../lego-robot-agent
```

### Step 7: Run Test
```bash
cd src/tests
python test1_action.py
```

## Expected Output

✅ **Success** - Agent initializes and responds to "hi. 1+1 = ?"

❌ **Failure** - Check error message and see troubleshooting below

## Common Issues

### "Please run 'az login'"
→ Run `az login` and try again

### "MCP server not found"
→ Build the MCP server: `cd lego-mcp && npm install && npm run build`

### "ServiceInitializationError"
→ Check your `.env` file has correct Azure OpenAI endpoint

### "Access Denied"
→ Contact Azure admin for permissions in `rg-legobot` resource group

## Need More Help?

- **Detailed Setup**: See `AZURE_SETUP.md`
- **Overview**: See `TEST_SETUP_SUMMARY.md`
- **README**: See `README.md`

## What's Next?

Once the test runs successfully, you can:
1. Try other test scripts (test4, test5, test6)
2. Modify the agent prompt in test1_action.py
3. Explore the agent framework in `src/lego_robot_agent/`

Happy coding! 🤖
