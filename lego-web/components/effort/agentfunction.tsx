import styles from "./agentfunction.module.scss";
import type { FunctionUpdate } from "store/voice/voice-client";

type Props = {
  func: FunctionUpdate;
};
const AgentFunction = ({ func }: Props) => {
  return (
    <div className={styles.function}>
      <div className={styles.functionCall}>
        <span>executing</span>&nbsp;
        <span className={styles.functionName}>{func.name}</span>
      </div>
    </div>
  );
};

export default AgentFunction;
