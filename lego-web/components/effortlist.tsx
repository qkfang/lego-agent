import React, { useEffect } from "react";
import styles from "./effortlist.module.scss";
import clsx from "clsx";
import { useEffortStore } from "store/effort";
import usePersistStore from "store/usepersiststore";
import AgentMessage from "./effort/agentmessage";
import AgentFunction from "./effort/agentfunction";
import AgentEffort from "./effort/agenteffort";
import type { Update } from "store/voice/voice-client";

const EffortList = () => {
  const ref = React.useRef<HTMLDivElement>(null);
  const effort = usePersistStore(useEffortStore, (state) => state);

  const scrollEffort = () => {
    setTimeout(() => {
      if (ref.current) {
        ref.current.scrollTo({
          top: ref.current.scrollHeight,
          behavior: "smooth",
        });
      }
    }, 10);
  };

  const getContent = (effort: Update) => {
    switch (effort.type) {
      case "message":
        return <AgentMessage message={effort} />;
      case "function":
        return <AgentFunction func={effort} />;
      case "agent":
        return <AgentEffort agent={effort} />;
      default:
        return <div className={styles.nothing}>Nothing</div>;
    }
  };

  useEffect(() => {
    scrollEffort();
  }, [effort?.efforts.length]);

  return (
    <div className={clsx(styles.effortlist, styles.scrollbarHide)} ref={ref}>
      {effort?.efforts.map((item, index) => {
        return <div key={index}>{getContent(item)}</div>;
      })}
    </div>
  );
};

export default EffortList;
