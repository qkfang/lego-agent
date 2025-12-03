import type { Route } from "./+types/home";
import Settings from "components/settings";
import Setting from "components/setting";
import {
  TbArticle,
  TbSettingsCog,
  TbViewfinder,
  TbImageInPicture,
  TbAirBalloon,
  TbId,
} from "react-icons/tb";
import { VscClearAll } from "react-icons/vsc";
import VoiceSettings from "components/voice/voicesettings";
import Actions from "components/actions";
import { version } from "store/version";
import Title from "components/title";
import { useEffect, useRef, useState } from "react";
import type { Update } from "store/voice/voice-client";
import { useUser } from "store/useuser";
import { useRealtime } from "components/voice/userealtime";
import { useEffortStore } from "store/effort";
import usePersistStore from "store/usepersiststore";
import styles from "./app.module.scss";
import AgentEditor from "components/voice/agenteditor";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { API_ENDPOINT } from "store/endpoint";

import VoiceTool from "components/voicetool";
import EffortList from "components/effortlist";
import Tool from "components/tool";
import { useOutputStore } from "store/output";
import { v4 as uuidv4 } from "uuid";
import Output from "components/output";
import {
  imageData,
  researchData,
  scenarioEffort,
  scenarioOutput,
  writerData,
  videoData,
} from "store/data";
import VideoImagePicker from "components/videoimagepicker";
import { HiOutlineVideoCamera } from "react-icons/hi2";
import { IoCameraOutline } from "react-icons/io5";
import FileImagePicker, {
  type FileInputHandle,
} from "components/fileimagepicker";
import { useLocation } from "react-router";
import clsx from "clsx";
import { BsMicMute, BsMic } from "react-icons/bs";
import { fetchCachedImage } from "store/images";

const queryClient = new QueryClient();

interface ImageFunctionCall {
  id: string;
  call_id: string;
  name: string;
  arguments: Record<string, any>;
  image?: string;
}

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Robotics Agents by Dad" },
    { name: "description", content: "Making Things Happen since 2023" },
  ];
}

export default function Home() {
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const flags = "tools,debug";
    // queryParams
    //   .get("flags")
    //   ?.split(",")
    //   .map((i) => i.toLocaleLowerCase().trim()) || [];

  const { user, error } = useUser();
  const [showCapture, setShowCapture] = useState(false);
  const [imageFunctionCall, setImageFunctionCall] =
    useState<ImageFunctionCall>();
  const filePickerRef = useRef<FileInputHandle>(null);

  useEffect(() => {
    if (error) {
      console.error("Error fetching user data:", error);
    }
  }, [error]);

  const effort = usePersistStore(useEffortStore, (state) => state);
  const output = usePersistStore(useOutputStore, (state) => state);

  const addOutput = async (
    parent: string,
    agent: string,
    call_id: string,
    content: Array<Record<string, any>>
  ) => {
    console.log("Adding output", parent, agent, call_id, content);
    for (const item of content) {
      if (item.type === "text") {
        output?.addOutput(parent, agent, {
          id: uuidv4(),
          title: agent,
          value: 1,
          data: {
            id: uuidv4(),
            type: "text",
            value: item.value,
            annotations: item.annotations,
          },
          children: [],
        });
      } else if (item.type === "image") {
        output?.addOutput(parent, agent, {
          id: uuidv4(),
          title: agent,
          value: 1,
          data: {
            id: uuidv4(),
            type: "image",
            description: item.description,
            image_url: item.image_url,
            size: item.size,
            quality: item.quality,
          },
          children: [],
        });
      } else if (item.type === "prompt") {
        // console.log("Adding user input to output", item.value);
        await sendRealtime({
          id: uuidv4(),
          type: "message",
          role: "user",
          content: item.value,
        });
      }
    }
  };

  const handleServerMessage = async (serverEvent: Update): Promise<void> => {
    console.log(serverEvent);
    switch (serverEvent.type) {
      case "message":
        if (serverEvent.content) {
          effort?.addEffort(serverEvent);
          // setShowCapture(true);
         
        }
        break;
      case "function":
        if (serverEvent.arguments?.kind) {
          setImageFunctionCall({
            id: serverEvent.id,
            call_id: serverEvent.call_id,
            name: serverEvent.name,
            arguments: serverEvent.arguments,
          });
          if (serverEvent.arguments.kind === "FILE") {
            sendRealtime({
              id: serverEvent.id,
              type: "function_completion",
              call_id: serverEvent.call_id,
              output: `This is a message from the function call that it is in progress. Let the user know that they can upload a file and it will be processed by the agent.`,
            });

            filePickerRef.current?.activateFileInput();
          } else {
            sendRealtime({
              id: serverEvent.id,
              type: "function_completion",
              call_id: serverEvent.call_id,
              output: `This is a message from the function call that it is in progress. Let the user know to click on the camera to take a picture.`,
            });
            setShowCapture(true);
          }
        } else {
          // check for client side agents
          sendRealtime({
            id: serverEvent.id,
            type: "function_completion",
            call_id: serverEvent.call_id,
            output: `This is a message from the function call that it is in progress. 
            You can ignore it and continue the conversation until the function call is completed.`,
          });

          effort?.addEffort(serverEvent);

          // check for `image_url` in the arguments
          if (serverEvent.arguments?.image_url) {
            console.log("Image URL found in arguments", serverEvent.arguments);
            const images = output?.getAllImages();
            // if there's only one image, set the image_url to the first image
            if (images && images.length > 0) {
              serverEvent.arguments.image_url = `${API_ENDPOINT}/${
                images[images.length - 1].image_url
              }`;
            }
          }

          const api = `${API_ENDPOINT}/api/agent/${user.key}`;
          console.log("Sending function call to agent", api, serverEvent);
          // execute agent
          fetch(api, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              call_id: serverEvent.call_id,
              id: serverEvent.id,
              name: serverEvent.name,
              arguments: serverEvent.arguments,
            }),
          });
        }
        break;
      case "agent":
        effort?.addEffort(serverEvent);
        if (serverEvent.status.toLowerCase().includes("failed")) {
          await sendRealtime({
            id: serverEvent.id,
            type: "function_completion",
            call_id: serverEvent.call_id,
            output: `The ${serverEvent.name} has failed. Please let the user know there may be issues with this agent in the service and are happy to help in any other way available to you.`,
          });
          break;
        }
        if (serverEvent.output && serverEvent.content) {
          addOutput(
            serverEvent.name.toLowerCase().replaceAll(" ", "_"),
            serverEvent.name,
            serverEvent.call_id,
            serverEvent.content?.content
          );
        }
        break;
    }
  };

  const { toggleRealtime, analyzer, sendRealtime, muted, setMuted, callState } =
    useRealtime(user, handleServerMessage);

  const handleVoice = async () => {
    if (callState === "idle") {
      console.log("Starting voice call");
      setMuted(true);
    } else if (callState === "call") {
      const response = confirm(
        "Are you sure you want to end the voice call? You will not be able to send messages until you start a new call."
      );
      if (response) {
        console.log("Ending voice call");
      } else {
        console.log("Not ending voice call");
        return;
      }
    }
    toggleRealtime();
  };

  const setCurrentImage = (image: string) => {
    if (!imageFunctionCall) {
      console.log("No image function call to set image for");
      return;
    }
    

    const setImage = (img: string) => {
      const args = {
        ...imageFunctionCall.arguments,
        image: img,
      };

      sendRealtime({
        id: imageFunctionCall.id,
        type: "function_completion",
        call_id: imageFunctionCall.call_id,
        output: `This is a message from the function call that it is in progress. 
        You can ignore it and continue the conversation until the function call is completed.`,
      });

      const api = `${API_ENDPOINT}/api/agent/${user.key}`;
      console.log(
        "Sending function call to agent",
        api,
        imageFunctionCall
      );
      // execute agent
      fetch(api, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          call_id: imageFunctionCall.call_id,
          id: imageFunctionCall.id,
          name: imageFunctionCall.name,
          arguments: args,
        }),
      });
    };

    fetchCachedImage(image, setImage);
  };

  const handleLiveStreamClick = () => {
    const img = document.getElementById("live-stream") as HTMLImageElement | null;
    if (!img) return;
    const canvas = document.createElement("canvas");
    canvas.width = img.naturalWidth || img.width;
    canvas.height = img.naturalHeight || img.height;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    const base64Image = canvas.toDataURL("image/png");
    // You can now use base64Image as needed, e.g., save or display it
    // console.log("Base64 Image:", base64Image);
  };

  // const [inputValue, setInputValue] = useState("grab red object and return to base.");
  const [inputValue, setInputValue] = useState("");

  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      addOutput(
        "user_input",
        "User Input",
        "",
        [
          {
            type: "prompt",
            value: e.currentTarget.value,
          }
        ]
      );
      setInputValue(""); // Clear input after sending
    }
  };

  const [showLiveStreamModal, setShowLiveStreamModal] = useState(false);

  return (
    <QueryClientProvider client={queryClient}>
      <main className={styles.home}>
        <Title
          text="Robotics Agents"
          subtitle="by Dad"
          version={version}
          user={user}
        />
        <div className={styles.scratch}>
          <div className={styles.output}>
            {output && output.output && output.output.children.length > 0 && (
              <Output data={output.output} />
            )}
          </div>
          <div className={styles.effort}>
          <img
            id="live-stream"
            src="http://192.168.0.50:5000/video_feed"
            alt="Live Stream"
            style={{ 
              width: '300px', 
              height: '200px', 
              margin:'5px', 
              border: '3px solid #FFD500', 
              borderRadius: '8px',
              boxShadow: '0 4px 15px rgba(0, 85, 191, 0.4)',
              transition: 'all 0.3s ease',
              cursor: 'pointer'
            }}
            crossOrigin="anonymous"
            onClick={() => setShowLiveStreamModal(true)}
            onMouseEnter={(e) => {
              e.currentTarget.style.border = '3px solid #2196F3';
              e.currentTarget.style.boxShadow = '0 6px 20px rgba(255, 213, 0, 0.6)';
              e.currentTarget.style.transform = 'scale(1.02)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.border = '3px solid #FFD500';
              e.currentTarget.style.boxShadow = '0 4px 15px rgba(0, 85, 191, 0.4)';
              e.currentTarget.style.transform = 'scale(1)';
            }}
          />
          {showLiveStreamModal && (
  <div
    style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100vw',
      height: '100vh',
      background: 'rgba(0,0,0,0.85)',
      zIndex: 200,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    }}
    onClick={() => setShowLiveStreamModal(false)}
  >
    <img
      src="http://192.168.0.50:5000/video_feed"
      alt="Live Stream Fullscreen"
      style={{
        maxWidth: '90vw',
        maxHeight: '90vh',
        border: '4px solid #FFD500',
        borderRadius: '8px',
        boxShadow: '0 0 40px rgba(0, 85, 191, 0.8)',
        background: '#222',
      }}
      crossOrigin="anonymous"
      onClick={e => e.stopPropagation()}
    />
    <button
      style={{
        position: 'absolute',
        top: 24,
        right: 32,
        fontSize: 42,
        fontWeight: 'bold',
        color: '#FFD500',
        background: 'linear-gradient(135deg, rgba(217, 44, 44, 0.9), rgba(255, 140, 0, 0.9))',
        border: '3px solid #FFD500',
        borderRadius: '50%',
        width: '56px',
        height: '56px',
        cursor: 'pointer',
        zIndex: 10000,
        transition: 'all 0.3s ease',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: '0 4px 15px rgba(255, 213, 0, 0.5)',
      }}
      onClick={() => setShowLiveStreamModal(false)}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = 'linear-gradient(135deg, rgba(0, 85, 191, 0.9), rgba(155, 95, 184, 0.9))';
        e.currentTarget.style.transform = 'scale(1.1) rotate(90deg)';
        e.currentTarget.style.boxShadow = '0 6px 20px rgba(33, 150, 243, 0.7)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = 'linear-gradient(135deg, rgba(217, 44, 44, 0.9), rgba(255, 140, 0, 0.9))';
        e.currentTarget.style.transform = 'scale(1) rotate(0deg)';
        e.currentTarget.style.boxShadow = '0 4px 15px rgba(255, 213, 0, 0.5)';
      }}
      aria-label="Close Fullscreen"
    >
      ×
    </button>
  </div>
)}
            <EffortList />
            <input
              type="text"
              placeholder={"Send a message"}
              className={styles.textInput}
              onKeyDown={handleInputKeyDown}
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
            />
            <VoiceTool
              onClick={handleVoice}
              callState={callState}
              analyzer={analyzer}
            />
          </div>
        </div>
        <div className={styles.tools}>
          {flags.includes("debug") ? (
            <Actions>
              <Tool
                icon={<VscClearAll size={18} title={"Reset"} />}
                onClick={() => {
                  effort?.clearEfforts();
                  output?.reset();
                }}
                title={"Reset"}
              />
              <Tool
                icon={<TbId size={18} title={"Image Edit"} />}
                onClick={() => {
                  console.log("Image edit clicked");
                }}
                title={"Image Edit"}
              />
              <Tool
                icon={<TbAirBalloon size={18} title={"Reset Event Scenario"} />}
                onClick={() => {
                  output?.reset();
                  output?.addRoot(scenarioOutput);
                  effort?.clearEfforts();
                  effort?.addEffortList(scenarioEffort);
                }}
                title={"Reset Event Scenario"}
              />
              <Tool
                icon={<IoCameraOutline size={18} title={"Capture Image"} />}
                onClick={() => {
                  filePickerRef.current?.activateFileInput();
                }}
                title={"Capture Image"}
              />
              <Tool
                icon={
                  <HiOutlineVideoCamera size={18} title={"Capture Image 2"} />
                }
                onClick={() => {
                  setShowCapture((prev) => !prev);
                }}
                title={"Capture Image 2"}
              />

              <Tool
                icon={<TbImageInPicture size={18} title={"Add Image"} />}
                onClick={() => {
                  output?.addOutput("gpt-image-1_agent", "GPT Image Agent", {
                    id: uuidv4(),
                    title: "GPT Image Agent",
                    value: 1,
                    data: imageData,
                    children: [],
                  });
                }}
                title={"Add Image"}
              />
              <Tool
                icon={<TbArticle size={18} title={"Add Article"} />}
                onClick={() => {
                  output?.addOutput(
                    "content_writer_agent",
                    "Content Writer Agent",
                    {
                      id: uuidv4(),
                      title: "Content Writer Agent",
                      value: 1,
                      data: writerData,
                      children: [],
                    }
                  );
                }}
                title={"Add Article"}
              />
              <Tool
                icon={<TbViewfinder size={18} title={"Add Research"} />}
                onClick={() => {
                  output?.addOutput("research_agent", "Research Agent", {
                    id: uuidv4(),
                    title: "Research Agent",
                    value: 1,
                    data: researchData,
                    children: [],
                  });
                }}
                title={"Add Research"}
              />
            </Actions>
          ) : (
            <></>
          )}

          {flags.includes("tools") ? (
            <Settings>
              <Setting
                id={"voice-agent-settings"}
                icon={<TbArticle size={18} />}
                className={styles.editor}
              >
                <AgentEditor />
              </Setting>
              <Setting
                id={"voice-settings"}
                icon={<TbSettingsCog size={18} />}
                className={styles.voice}
              >
                <VoiceSettings />
              </Setting>
            </Settings>
          ) : (
            <></>
          )}
        </div>
      </main>
      <VideoImagePicker
        show={showCapture}
        setShow={setShowCapture}
        setCurrentImage={setCurrentImage}
      />
      <FileImagePicker
        ref={filePickerRef}
        setCurrentImage={setCurrentImage}
      />
      {callState === "call" && (
        <div
          className={clsx(
            styles.mutebutton,
            muted ? styles.muted : styles.unmuted
          )}
          onClick={() => setMuted((muted) => !muted)}
        >
          {muted ? <BsMicMute size={24} /> : <BsMic size={24} />}
        </div>
      )}
    </QueryClientProvider>
  );
}
