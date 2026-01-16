// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

const { AIProjectClient } = require('@azure/ai-projects');
const { DefaultAzureCredential } = require('@azure/identity');

/**
 * Service for interacting with Azure AI Foundry Agents
 */
class FoundryAgentService {
  constructor(connectionString) {
    if (!connectionString) {
      throw new Error('Foundry connection string is required');
    }

    this.connectionString = connectionString;
    this.credential = new DefaultAzureCredential();
    this.projectClient = null;
    this.agentId = null;
    this.threads = new Map(); // Store thread IDs per user
  }

  /**
   * Initialize the Foundry Agent client
   */
  async initialize() {
    if (!this.projectClient) {
      this.projectClient = AIProjectClient.fromConnectionString(
        this.connectionString,
        this.credential
      );

      // Get the LEGO orchestrator agent
      const agents = await this.projectClient.agents.listAgents({ limit: 100 });
      // Note: Checking for both spellings to handle existing agent name typo in azureagents.py
      const orchestrator = agents.data.find((agent) =>
        agent.name.includes('lego-orchestrator') || agent.name.includes('lego-ochestrator')
      );

      if (orchestrator) {
        this.agentId = orchestrator.id;
        console.log(`Found orchestrator agent: ${orchestrator.name} (${this.agentId})`);
      } else {
        // Fallback: use the first lego- agent found
        const legoAgent = agents.data.find((agent) => agent.name.startsWith('lego-'));
        if (legoAgent) {
          this.agentId = legoAgent.id;
          console.log(`Using fallback agent: ${legoAgent.name} (${this.agentId})`);
        } else {
          console.warn('No LEGO agents found in Foundry');
        }
      }
    }
  }

  /**
   * Get or create a thread for a user
   */
  async getThread(userId) {
    if (!this.threads.has(userId)) {
      await this.initialize();
      const thread = await this.projectClient.agents.createThread();
      this.threads.set(userId, thread.id);
      console.log(`Created new thread for user ${userId}: ${thread.id}`);
    }
    return this.threads.get(userId);
  }

  /**
   * Send a message to the Foundry Agent and get a response
   */
  async chat(message, userId = 'default') {
    try {
      await this.initialize();

      if (!this.agentId) {
        return 'No LEGO agent is currently available. Please ensure the Foundry agents are deployed.';
      }

      // Get or create thread for this user
      const threadId = await this.getThread(userId);

      // Create message in thread
      await this.projectClient.agents.createMessage(threadId, {
        role: 'user',
        content: message,
      });

      // Run the agent
      const run = await this.projectClient.agents.createRun(threadId, {
        assistantId: this.agentId,
      });

      // Wait for completion with timeout
      let runStatus = run;
      let attempts = 0;
      const maxAttempts = 60; // 60 seconds timeout

      while (
        runStatus.status === 'queued' ||
        runStatus.status === 'in_progress' ||
        runStatus.status === 'requires_action'
      ) {
        if (attempts >= maxAttempts) {
          return 'The agent is taking longer than expected. Please try again.';
        }

        await new Promise((resolve) => setTimeout(resolve, 1000));
        runStatus = await this.projectClient.agents.getRun(threadId, run.id);
        attempts++;
      }

      if (runStatus.status === 'failed') {
        console.error('Agent run failed:', runStatus.lastError);
        return 'Sorry, the agent encountered an error. Please try again.';
      }

      if (runStatus.status === 'cancelled' || runStatus.status === 'expired') {
        return 'The request was cancelled or expired. Please try again.';
      }

      // Get the latest messages
      const messages = await this.projectClient.agents.listMessages(threadId, {
        order: 'desc',
        limit: 1,
      });

      if (messages.data.length > 0) {
        const lastMessage = messages.data[0];
        if (lastMessage.role === 'assistant') {
          // Extract text content from the message
          const textContent = lastMessage.content
            .filter((c) => c.type === 'text')
            .map((c) => c.text.value)
            .join('\n');
          return textContent || 'No response from agent.';
        }
      }

      return 'No response received from the agent.';
    } catch (error) {
      console.error('Error in Foundry Agent chat:', error);
      throw error;
    }
  }

  /**
   * Clear thread for a user (useful for starting fresh conversation)
   */
  clearThread(userId) {
    this.threads.delete(userId);
  }

  /**
   * Cleanup resources
   */
  async dispose() {
    this.threads.clear();
    if (this.projectClient) {
      // Cleanup if needed
      this.projectClient = null;
    }
  }
}

module.exports = { FoundryAgentService };
