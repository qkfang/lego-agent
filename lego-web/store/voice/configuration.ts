import { API_ENDPOINT } from "store/endpoint";

export const defaultVoiceDocument = `---
id: your-unique-id
name: Your Display Name
description: A brief description of the configuration.
---
Your Markdown content goes here (using {{customer}} for customer name).
`

export interface Configuration {
  id: string;
  name: string;
  default: boolean;
  content: string;
  tools: Array<{
    id: string;
    name: string;
    type: string;
    description: string;
    parameters: Array<{
      name: string;
      type: string;
      description: string;
      required: boolean;
    }>;
  }>;
}

export interface ConfigurationAction {
  id: string;
  action: string;
  error?: string;
}

export class VoiceConfiguration {
  endpoint: string;

  constructor() {
    this.endpoint = API_ENDPOINT;
  }

  async fetchConfigurations(): Promise<Configuration[]> {
    const response = await fetch(`${this.endpoint}/api/configuration/`);
    if (!response.ok) {
      throw new Error("Failed to fetch configurations");
    }
    const configurations = await response.json();
    return configurations;
  }

  async fetchConfiguration(id: string): Promise<Configuration> {
    const response = await fetch(`${this.endpoint}/api/configuration/${id}`);
    if (!response.ok) {
      throw new Error("Failed to fetch configuration");
    }
    return await response.json();
  }

  async createConfiguration(configuration: Configuration): Promise<Configuration> {
    console.log("Creating configuration", configuration);
    const response = await fetch(`${this.endpoint}/api/configuration/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        "content": configuration.content,
      }),
    });
    if (!response.ok) {
      throw new Error("Failed to create configuration");
    }
    const c =  await response.json();
    console.log("Created configuration", c);
    return c;
  }

  async updateConfiguration(configuration: Configuration): Promise<Configuration> {
    const response = await fetch(`${this.endpoint}/api/configuration/${configuration.id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(configuration),
    });
    if (!response.ok) {
      throw new Error("Failed to update configuration");
    }

    const c = await response.json();
    console.log("Updated configuration", c);
    return c;
  }

  async deleteConfiguration(id: string): Promise<ConfigurationAction> {
    const response = await fetch(`${this.endpoint}/api/configuration/${id}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      throw new Error("Failed to delete configuration");
    }
    return await response.json();
  }

  async setDefaultConfiguration(id: string): Promise<ConfigurationAction> {
    const response = await fetch(`${this.endpoint}/api/configuration/default/${id}`, {
      method: "PUT",
    });
    if (!response.ok) {
      throw new Error("Failed to set default configuration");
    }
    return await response.json();
  }
}