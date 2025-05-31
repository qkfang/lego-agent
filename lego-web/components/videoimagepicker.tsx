import { type FormEvent, use, useEffect, useRef, useState } from "react";
import { HiOutlineVideoCamera } from "react-icons/hi2";
import styles from "./videoimagepicker.module.scss";
import { GrClose } from "react-icons/gr";
import { readAndCacheVideoFrame } from "../store/images";
import { useMediaDevices } from "store/usemediadevice";
import { useLocalStorage } from "store/uselocalstorage";

type Props = {
  show: boolean;
  setShow: (show: boolean) => void;
  setCurrentImage: (image: string) => void;
};

const VideoImagePicker = ({ show, setShow, setCurrentImage }: Props) => {
  const [showCamera, setShowCamera] = useState<boolean>(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  const { devices, error, isLoading } = useMediaDevices(true);
  const { storedValue: selectedDevice, setValue: setSelectedDevice } =
    useLocalStorage<string>("selected-video-device", "default");

  useEffect(() => {
    if (!isLoading && devices.length > 0 && selectedDevice === "default") {
      // const videoDevices = devices.filter(
      //   (device) => device.kind === "videoinput"
      // );
      const videoDevices = devices;
      setSelectedDevice(videoDevices[0].deviceId);
      startVideo(videoDevices[0].deviceId);
    }
  }, [devices, isLoading]);

  const startVideo = async (deviceId: string) => {
    if (videoRef.current) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { deviceId: { exact: deviceId } },
        });
        videoRef.current.disablePictureInPicture = true;
        videoRef.current.srcObject = stream;
        setShowCamera(true);
      } catch {
        alert("Error accessing camera.");
        videoRef.current.srcObject = null;
        setShowCamera(false);
      }
    }
  };

  const stopVideo = () => {
    if (videoRef.current) {
      const stream = videoRef.current.srcObject as MediaStream;
      if (!stream) return;
      const tracks = stream.getTracks();
      tracks.forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }
  };

  const closeVideo = () => {
    stopVideo();
    setShow(false);
  };

  const handleVideoClick = () => {
    if (videoRef.current) {
      readAndCacheVideoFrame(videoRef.current!).then((data) => {
        if (!data) return;
        setCurrentImage(data);
        closeVideo();
      });
    }
  };

  useEffect(() => {
    if (show) {
      setShow(true);
      if (selectedDevice !== "default") {
        startVideo(selectedDevice);
      }
    } else {
      closeVideo()
    }
  }, [show]);

  return (
    <>
      {show && (
        <div className={styles.videooverlay}>
          <div className={styles.videoimagepicker}>
            <div className={styles.videobox}>
              <div className={styles.header}>
                <select
                  id="device"
                  name="device"
                  className={styles.mediaselect}
                  value={selectedDevice}
                  title="Select a device"
                  onChange={(e) => setSelectedDevice(e.target.value)}
                >
                  {isLoading && <option>Loading...</option>}
                  {error && <option>Error: {error}</option>}
                  {devices
                    .filter((device) => device.kind === "videoinput")
                    .map((device) => {
                      return (
                        <option key={device.deviceId} value={device.deviceId}>
                          {device.label}
                        </option>
                      );
                    })}
                </select>
                {showCamera && (
                  <div className="button" onClick={() => handleVideoClick()}>
                    <HiOutlineVideoCamera size={24} className="buttonIcon" />
                  </div>
                )}
                <button className="button" onClick={() => closeVideo()}>
                  <GrClose size={24} className="buttonIcon" />
                </button>
              </div>
              <div className={styles.video}>
                <video
                  ref={videoRef}
                  autoPlay={true}
                  className={styles.videoelement}
                  title="Click to take a picture"
                  onClick={() => handleVideoClick()}
                ></video>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default VideoImagePicker;
