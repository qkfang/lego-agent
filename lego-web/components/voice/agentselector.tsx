import type { AgentConfig } from "store/agents";
import styles from "./agentselector.module.scss";
import type { Configuration } from "store/voice/configuration";
import {
  useEffect,
  useState,
  type Dispatch,
  type SetStateAction,
} from "react";

type Props = {
  agents: AgentConfig[];
  configuration: Configuration;
  setSelectedAgents: Dispatch<SetStateAction<string[]>>;
};

interface AgentSelection {
  id: string;
  name: string;
  description: string;
  selected: boolean;
}

const AgentSelector = ({ agents, configuration, setSelectedAgents }: Props) => {
  const [agentSelections, setAgentSelections] = useState<AgentSelection[]>([]);
  useEffect(() => {
    const selections = agents.map((agent) => ({
      id: agent.id,
      name: agent.name,
      description: agent.description,
      selected: configuration.tools.some((tool) => tool.id === agent.id),
    }));
    setSelectedAgents(
      selections.filter((agent) => agent.selected).map((agent) => agent.id)
    );
    setAgentSelections(selections);
  }, [agents, configuration]);

  const changeAgent = (
    target: EventTarget & HTMLInputElement,
    agentId: string
  ): void => {
    const { id, checked } = target;
    setAgentSelections((prevSelections) =>
      prevSelections.map((agent) =>
        agent.id === agentId ? { ...agent, selected: checked } : agent
      )
    );

    setSelectedAgents((prev) => {
      if (checked) {
        return [...prev, agentId];
      }
      return prev.filter((agent) => agent !== agentId);
    });

    console.log("Agent selected:", id, checked, agentId);
  };

  return (
    <fieldset className={styles.fieldset}>
      <legend>Available Agents</legend>
      {agentSelections.map((agent) => (
        <div key={agent.id}>
          <input
            type="checkbox"
            id={agent.id}
            name={agent.id}
            radioGroup="agents"
            onChange={(e) => changeAgent(e.target, agent.id)}
            checked={agent.selected}
          />
          <label
            className={styles.label}
            htmlFor={agent.id}
            title={agent.description}
          >
            {agent.name}
          </label>
        </div>
      ))}
    </fieldset>
  );
};

export default AgentSelector;
