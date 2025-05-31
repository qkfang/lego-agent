import React, { type ReactElement } from "react";
import Setting from "./setting";
import styles from "./settings.module.scss";

interface Props {
  children: ReactElement<typeof Setting> | Array<ReactElement<typeof Setting>>;
}

const Settings: React.FC<Props> = ({ children }) => {
  if (!children) {
    return null;
  }
  if (!Array.isArray(children)) {
    children = [children];
  }
  return (
    <div className={styles.settings}>
      {children.map((child) => {
        return child;
      })}
    </div>
  );
};

export default Settings;
