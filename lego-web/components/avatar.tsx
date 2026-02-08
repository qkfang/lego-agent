import React, { useEffect, useRef, useState } from "react";
import styles from "./avatar.module.scss";

interface Props {
  isActive: boolean;
  speaking: boolean;
  analyzer: AnalyserNode | null;
}

const Avatar: React.FC<Props> = ({ isActive, speaking, analyzer }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [amplitude, setAmplitude] = useState(0);

  useEffect(() => {
    if (isActive && analyzer && canvasRef.current) {
      const canvas = canvasRef.current;
      const context = canvas.getContext("2d");
      const bufferLength = analyzer.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);

      if (context) {
        const draw = () => {
          if (!isActive || !analyzer) return;
          requestAnimationFrame(draw);

          analyzer.getByteFrequencyData(dataArray);

          // Calculate average amplitude
          let sum = 0;
          for (let i = 0; i < bufferLength; i++) {
            sum += dataArray[i];
          }
          const avg = sum / bufferLength;
          setAmplitude(avg / 255);
        };
        draw();
      }
    }
  }, [isActive, analyzer]);

  return (
    <div className={styles.avatarContainer}>
      <canvas ref={canvasRef} style={{ display: "none" }} />
      
      {/* Mario-themed Avatar */}
      <div className={`${styles.avatar} ${speaking ? styles.speaking : ""}`}>
        <div 
          className={styles.avatarFace}
          style={{
            transform: `scale(${1 + amplitude * 0.15})`,
          }}
        >
          {/* Mario's Hat */}
          <div className={styles.hat}>
            <div className={styles.hatBrim}></div>
            <div className={styles.hatTop}>
              <span className={styles.mLogo}>M</span>
            </div>
          </div>
          
          {/* Face */}
          <div className={styles.face}>
            {/* Eyes */}
            <div className={styles.eyes}>
              <div className={styles.eye}></div>
              <div className={styles.eye}></div>
            </div>
            
            {/* Nose */}
            <div className={styles.nose}></div>
            
            {/* Mustache */}
            <div className={styles.mustache}>
              <div className={styles.mustacheLeft}></div>
              <div className={styles.mustacheRight}></div>
            </div>
            
            {/* Mouth */}
            <div 
              className={`${styles.mouth} ${speaking ? styles.mouthOpen : ""}`}
              style={{
                transform: speaking ? `scaleY(${1 + amplitude * 0.8})` : 'scaleY(1)',
              }}
            ></div>
          </div>
        </div>
      </div>
      
      {!isActive && (
        <div className={styles.placeholder}>
          <div className={styles.startIcon}>🎮</div>
          <p>Start conversation to see Mario</p>
        </div>
      )}
    </div>
  );
};

export default Avatar;
