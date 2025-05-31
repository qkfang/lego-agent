import React, { type ReactElement } from "react";
import Tool from "./tool";
import styles from "./actions.module.scss";
import type VoiceTool from "./voicetool";

interface Props {
  children: ReactElement<typeof Tool | typeof VoiceTool> | Array<ReactElement<typeof Tool | typeof VoiceTool>>;
}

const Actions: React.FC<Props> = ({ children }) => {
  if (!children) {
    return null;
  }
  if (!Array.isArray(children)) {
    children = [children];
  }
  return (
    <div className={styles.actions}>
      {children.map((child) => {
        return child;
      })}
    </div>
  );
};

export default Actions;
