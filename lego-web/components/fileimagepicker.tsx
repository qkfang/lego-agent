import { useImperativeHandle, useRef } from "react";
import { readAndCacheFile } from "../store/images";
import React from "react";

export interface FileInputHandle {
  activateFileInput: () => void;
}

export type FileInputProps = {
  setCurrentImage: (image: string) => void;
};

const FileImagePicker = React.forwardRef<FileInputHandle, FileInputProps>(
  ({ setCurrentImage }: FileInputProps, ref) => {
    useImperativeHandle(ref, () => ({
      activateFileInput: () => {
        if (fileInput.current) {
          fileInput.current.click();
        }
      },
    }));
    /** refs */
    const fileInput = useRef<HTMLInputElement>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (!e.target.files) return;
      if (e.target.files.length === 0) return;
      const file = e.target.files?.[0];
      if (!file) {
        return;
      }
      readAndCacheFile(file).then((data) => {
        if (!data) return;
        setCurrentImage(data);
        e.target.value = "";
      });
    };

    return (
      <input
        title={"File Image Input"}
        type="file"
        className="hidden"
        accept="image/*"
        ref={fileInput}
        onChange={handleFileChange}
      />
    );
  }
);

export default FileImagePicker;
