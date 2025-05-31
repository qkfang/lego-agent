import React from "react";
import styles from "./tool.module.scss";
import clsx from "clsx";

interface Props {
  icon: React.ReactNode;
  onClick: () => void;
  title?: string;
  className?: string;
}

const Tool: React.FC<Props> = ({ icon, onClick, title, className }) => {
  const style = className ? clsx(styles.button, className) : styles.button;
  return (
    <div className={style} onClick={onClick} title={title}>
      {icon}
    </div>
  );
};



export default Tool;
