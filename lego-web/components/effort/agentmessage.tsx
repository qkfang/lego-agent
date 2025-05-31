import type { MessageUpdate } from "store/voice/voice-client";
import styles from "./agentmessage.module.scss";
import clsx from "clsx";
import { useRemark } from "react-remark";
import remarkGemoji from "remark-gemoji";
import { useEffect } from "react";

type Props = {
  message: MessageUpdate;
};
const AgentMessage = ({ message }: Props) => {
  const [reactContent, setMarkdownSource] = useRemark({
      //@ts-expect-error - allowDangerousHtml is not in the types
      remarkPlugins: [remarkGemoji],
      remarkToRehypeOptions: { allowDangerousHtml: true },
      rehypeReactOptions: {},
    });
  
    useEffect(() => {
      setMarkdownSource(message.content);
    }, [message, setMarkdownSource]);
  return (
    <div
      className={clsx(
        styles.message,
        message.role === "user" ? styles.user : styles.assistant
      )}
    >
      {reactContent}
    </div>
  );
};

export default AgentMessage;
