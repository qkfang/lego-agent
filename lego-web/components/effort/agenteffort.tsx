import styles from "./agenteffort.module.scss";
import type { AgentUpdate } from "store/voice/voice-client";

type Props = {
  agent: AgentUpdate;
};
const AgentEffort = ({ agent }: Props) => {

  return (
    <div className={styles.agent}>
      <div title={`${agent.call_id} - ${agent.id}`} className={styles.title}>
        <span className={styles.agentName}>{agent.name}</span>
      </div>
      <div className={styles.title}>{agent.status}</div>
      {agent.information && typeof agent.information === "string" && (
        <div className={styles.status} title={agent.information}>
          {agent.information}
        </div>
      )}
      {agent.information && typeof agent.information === "object" && (
        <div className={styles.status} title={agent.information["message"]}>
          {agent.information["code"]}
        </div>
      )}
      {agent.content &&
        agent.content.type === "tool_calls" &&
        agent.content.content.map((call: any, index: number) => (
          <div className={styles.status} key={index}>
            <span>Executed</span>
            <span className={styles.tool}>{call.type}</span>
            <span>tool...</span>
          </div>
        ))}
    </div>
  );
};

export default AgentEffort;
