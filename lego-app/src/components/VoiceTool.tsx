import { useEffect, useState } from "react";
import { HiMiniMicrophone, HiSpeakerWave } from "react-icons/hi2";
import './VoiceTool.scss';
import Avatar from "./avatar";

interface Props {
  onClick: () => void;
  callState: "idle" | "call";
  analyzer: AnalyserNode | null;
}

const VoiceTool: React.FC<Props> = ({ onClick, callState, analyzer }) => {
  const [talking, setTalking] = useState(false);

  useEffect(() => {
    if (callState === "call" && analyzer) {
      const bufferLength = analyzer.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      
      const checkTalking = () => {
        if (callState === "call" && analyzer) {
          requestAnimationFrame(checkTalking);
        }
        if (!analyzer) return;

        analyzer.getByteFrequencyData(dataArray);

        let sum = 0;
        for (let i = 0; i < bufferLength; i++) {
          sum += dataArray[i];
        }
        setTalking(sum > 0);
      };
      checkTalking();
    }
  }, [analyzer, callState]);

  return (
    <div className="voice-tool">
      {/* Digital Avatar Display */}
      <div className="avatar-wrapper">
        <Avatar 
          isActive={callState === "call"} 
          speaking={talking}
          analyzer={analyzer}
        />
      </div>
      
      {/* Microphone/Speaker Button */}
      <div
        className={callState === "call" ? "call" : "idle"}
        onClick={onClick}
      >
        {talking ? <HiSpeakerWave size={48} /> : <HiMiniMicrophone size={48} />}
      </div>
    </div>
  );
};

export default VoiceTool;
