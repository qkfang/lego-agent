const exampleAgentConfig =
{
  "id": "blog_post_writer",
  "name": "Researcher Agent",
  "type": "azure-agent",
  "description": "This agent is designed to act as a researcher, capable of performing online searches and providing structured  information based on user queries. It utilizes Bing Search to find accurate and relevant results, ensuring that  the information returned is concise and comprehensive. The agent is equipped to handle a variety of topics and can refine its search based on user feedback.",
  "options": {
    "agent_id": "asst_mJvd8QYU31U3lLrEHrmhMPAz"
  },
  "parameters": [
    {
      "name": "customer",
      "type": "string",
      "description": "The name of the customer the agent is assisting.",
      "required": true
    },
    {
      "name": "name",
      "type": "string",
      "description": "The name of the blog post.",
      "required": true
    },
    {
      "name": "description",
      "type": "string",
      "description": "A brief description of the blog post.",
      "required": true
    },
    {
      "name": "keywords",
      "type": "string",
      "description": "A list of keywords related to the blog post.",
      "required": true
    },
    {
      "name": "audience",
      "type": "string",
      "description": "The target audience for the blog post.",
      "required": true
    },
    {
      "name": "ideas",
      "type": "string",
      "description": "A list of ideas or topics to be covered in the blog post.",
      "required": true
    }
  ]
}

export interface AgentConfig {
  id: string;
  name: string;
  type: string;
  description: string;
  options: Record<string, any>;
  parameters: Array<{
    name: string;
    type: string;
    description: string;
    required: boolean;
  }>;
}