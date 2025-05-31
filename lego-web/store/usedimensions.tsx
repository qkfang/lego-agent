import { ResizeObserver } from "@juggle/resize-observer";
import { useEffect, useRef, useState, type RefObject } from "react";

interface ChartDimensions {
  height: number;
  width: number;
  marginTop: number;
  marginRight: number;
  marginBottom: number;
  marginLeft: number;
  boundedHeight: number;
  boundedWidth: number;
}

const useDimensions = (ref: RefObject<HTMLDivElement | null>, initialDimensions?: any) => {
  //const ref = useRef<HTMLDivElement>(null);

  const [height, setHeight] = useState(initialDimensions?.height || 0);
  const [width, setWidth] = useState(initialDimensions?.width || 0);

  useEffect(() => {
    if (!ref.current) {
      return;
    }

    const resizeObserver = new ResizeObserver((entries) => {
      if (!Array.isArray(entries)) return;
      if (!entries.length) return;
      const entry = entries[0];
      if (width != entry.contentRect.width) setWidth(entry.contentRect.width);
      if (height != entry.contentRect.height)
        setHeight(entry.contentRect.height);
    });
    resizeObserver.observe(ref.current);

    return () => {
      if (!ref.current) return;
      resizeObserver.unobserve(ref.current);
    };
  }, []);

  const dimensions: ChartDimensions = {
    width: width || initialDimensions?.width || 0,
    height: height || initialDimensions?.height || 0,
    marginTop: initialDimensions?.marginTop || 0,
    marginRight: initialDimensions?.marginRight || 0,
    marginBottom: initialDimensions?.marginBottom || 0,
    marginLeft: initialDimensions?.marginLeft || 0,
    boundedHeight:
      (initialDimensions?.height || height) -
      (initialDimensions?.marginTop || 0) -
      (initialDimensions?.marginBottom || 0),
    boundedWidth:
      (initialDimensions?.width || width) -
      (initialDimensions?.marginLeft || 0) -
      (initialDimensions?.marginRight || 0),
  };

  return dimensions;
};

export default useDimensions;
