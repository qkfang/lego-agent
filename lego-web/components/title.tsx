import React from "react";
import styles from "./title.module.scss";
import { type User } from "store/useuser";
import { TbUser } from "react-icons/tb";

type Props = {
  text: string;
  subtitle?: string;
  version: string;
  user?: User;
};

const Title: React.FC<Props> = ({ text, subtitle, version, user }: Props) => {
  const renderAnimatedText = (text: string) => {
    return text.split('').map((char, index) => (
      <span 
        key={index} 
        className={styles.animatedChar}
        style={{ animationDelay: `${index * 0.1}s` }}
      >
        {char === ' ' ? '\u00A0' : char}
      </span>
    ));
  };

  return (
    <div className={styles.container}>
      <div className={styles.logo}>
        <div className={styles.title}>
          <span className={styles.maintitle} title={version}>
            {renderAnimatedText(text)}
          </span>
          {subtitle && <span className={styles.subtitle}>{subtitle}</span>}
        </div>
      </div>
      <div className={styles.grow} />
      {user && (
        <div className={styles.user}>
          <div>
            <div className={styles.name}>{user.name}</div>
          </div>
          {user.avatar && (
            <img alt={user.name} className={styles.avatar} src={user.avatar} />
          )}
          {!user.avatar && (
            <div className={styles.userIcon}>
              <TbUser size={32} />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Title;
