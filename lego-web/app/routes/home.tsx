import MicIcon from '../../components/micicon';
import styles from './home.module.scss';

export default function Landing() {
  return (
    <div className={styles.landing}>
      <div className={styles.root}>
        <div className={styles.container}>
          <h1>What can we<br />start working on?</h1>
          <p>Talk through your ideas and let's make them reality.</p>
        </div>
        <a href="/app">
          <div className={styles.micContainer}>
            <MicIcon 
              className={styles.micIcon}
              role="button"
              aria-label="Start recording"
              tabIndex={0}
            />
          </div>
        </a>
      </div>
    </div>
  );
}
