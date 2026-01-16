// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

// Import required packages
const path = require('path');
const restify = require('restify');

// Import required bot services
const {
  CloudAdapter,
  ConfigurationServiceClientCredentialFactory,
  MemoryStorage,
  ConfigurationBotFrameworkAuthentication,
} = require('botbuilder');

const { Application, TurnState } = require('@microsoft/teams-ai');

// Load environment variables
require('dotenv').config({ path: path.join(__dirname, '../.env.local') });

// Create adapter
const credentialsFactory = new ConfigurationServiceClientCredentialFactory({
  MicrosoftAppId: process.env.BOT_ID,
  MicrosoftAppPassword: process.env.BOT_PASSWORD,
  MicrosoftAppType: 'MultiTenant',
});

const botFrameworkAuthentication = new ConfigurationBotFrameworkAuthentication(
  {},
  credentialsFactory
);

const adapter = new CloudAdapter(botFrameworkAuthentication);

// Error handler
adapter.onTurnError = async (context, error) => {
  console.error(`\n [onTurnError] unhandled error: ${error}`);
  console.error(error);

  // Send a trace activity
  await context.sendTraceActivity(
    'OnTurnError Trace',
    `${error}`,
    'https://www.botframework.com/schemas/error',
    'TurnError'
  );

  // Send a message to the user
  await context.sendActivity('The bot encountered an error or bug.');
};

// Create storage
const storage = new MemoryStorage();

// Create the Application with AI capabilities
const app = new Application({
  storage,
  adapter,
  botAppId: process.env.BOT_ID,
});

// Import and setup Foundry Agent integration
const { FoundryAgentService } = require('./foundryAgent');
const foundryService = new FoundryAgentService(
  process.env.FOUNDRY_CONNECTION || process.env.PROJECT_CONNECTION_STRING
);

// Listen for incoming messages
app.message('/', async (context, state) => {
  const userMessage = context.activity.text;
  
  if (!userMessage) {
    return;
  }

  console.log(`User message: ${userMessage}`);

  // Show typing indicator
  await context.sendActivity({ type: 'typing' });

  try {
    // Send message to Foundry Agent and get response
    const response = await foundryService.chat(userMessage, context.activity.from.id);
    
    await context.sendActivity(response);
  } catch (error) {
    console.error('Error calling Foundry Agent:', error);
    await context.sendActivity(
      'Sorry, I encountered an error while processing your request. Please try again.'
    );
  }
});

// Listen for incoming notifications
app.conversationUpdate('membersAdded', async (context, state) => {
  const membersAdded = context.activity.membersAdded || [];
  for (const member of membersAdded) {
    if (member.id !== context.activity.recipient.id) {
      await context.sendActivity(
        'Hello! I am the LEGO Copilot. I can help you control and interact with your LEGO robots. Just ask me anything!'
      );
    }
  }
});

// Create HTTP server
const server = restify.createServer();
server.use(restify.plugins.bodyParser());

// Listen for incoming requests
server.post('/api/messages', async (req, res) => {
  await adapter.process(req, res, async (context) => {
    await app.run(context);
  });
});

// Health check endpoint
server.get('/health', (req, res) => {
  res.send(200, { status: 'healthy' });
});

// Start server
const port = process.env.PORT || 3978;
server.listen(port, () => {
  console.log(`\n${server.name} listening to ${server.url}`);
  console.log('\nGet Bot Framework Emulator: https://aka.ms/botframework-emulator');
  console.log('\nTo test your bot, see: https://aka.ms/debug-with-bot-emulator');
});
