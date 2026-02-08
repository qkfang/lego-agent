import React, { useEffect, useRef, useState } from "react";
import "../styles/Avatar.scss";

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
    <div className="avatar-container">
      <canvas ref={canvasRef} style={{ display: "none" }} />
      
      {/* Mario-themed Avatar */}
      <div className={`avatar ${speaking ? "speaking" : ""}`}>
        <div 
          className="avatar-face"
          style={{
            transform: `scale(${1 + amplitude * 0.15})`,
          }}
        >
          {/* Mario's Hat */}
          <div className="hat">
            <div className="hat-brim"></div>
            <div className="hat-top">
              <span className="m-logo">M</span>
            </div>
          </div>
          
          {/* Face */}
          <div className="face">
            {/* Eyes */}
            <div className="eyes">
              <div className="eye"></div>
              <div className="eye"></div>
            </div>
            
            {/* Nose */}
            <div className="nose"></div>
            
            {/* Mustache */}
            <div className="mustache">
              <div className="mustache-left"></div>
              <div className="mustache-right"></div>
            </div>
            
            {/* Mouth */}
            <div 
              className={`mouth ${speaking ? "mouth-open" : ""}`}
              style={{
                transform: speaking ? `scaleY(${1 + amplitude * 0.8})` : 'scaleY(1)',
              }}
            ></div>
          </div>
        </div>
      </div>
      
      {!isActive && (
        <div className="placeholder">
          <div className="start-icon">🎮</div>
          <p>Start conversation to see Mario</p>
        </div>
      )}
    </div>
  );
};

export default Avatar;
