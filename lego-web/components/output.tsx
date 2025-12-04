import * as d3 from "d3";
import styles from "./output.module.scss";
import { useRef, useState } from "react";
import useDimensions from "store/usedimensions";
import { type OutputNode, type Data, Dimensions } from "store/output";
import TextOutput from "./output/textoutput";
import { API_ENDPOINT } from "store/endpoint";
import OutputDisplay, { type OuptutDisplayHandle } from "./output/outputdisplay";

import VideoImagePicker from "components/videoimagepicker";

type Props = {
  data: OutputNode;
};

const Output: React.FC<Props> = ({ data }: Props) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const outputDisplayRef = useRef<OuptutDisplayHandle>(null);
  const dms = useDimensions(chartRef, {
    marginBottom: 100,
  });

  const [showCapture, setShowCapture] = useState(true);
  const treemap = (data: OutputNode) =>
    d3
      .treemap<OutputNode>()
      .tile(d3.treemapBinary)
      .size([dms.boundedWidth, dms.boundedHeight])
      .paddingOuter(16)
      .paddingTop(48)
      .paddingInner(16)
      .round(true)(
      d3
        .hierarchy<OutputNode>(data)
        .sum((d) => d.value)
        .sort((a, b) => (b.value || 0) - (a.value || 0))
    );

  const root = Array.from(d3.group(treemap(data), (d) => d.height).values())[1];
  
  const generateContent = (
    id: string,
    title: string,
    data: Data,
    d: Dimensions,
    fill: string
  ) => {
    const width = d.x1 - d.x0;
    const height = d.y1 - d.y0;
    const x = d.x0;
    const y = d.y0;

    if (data.type === "text") {
      return (
        <>
          <rect
            id={id + "_rect"}
            width={d.x1 - d.x0}
            height={d.y1 - d.y0}
            fill={fill}
            rx={8}
            ry={8}
          />
          <clipPath id={`clip-${id}`}>
            <rect
              width={Math.max(d.x1 - d.x0 - 5, 1)}
              height={Math.max(d.y1 - d.y0 - 5, 1)}
              rx={8}
              ry={8}
            />
          </clipPath>
          <g clipPath={`url(#clip-${id})`}>
            <foreignObject
              x={10}
              y={0}
              width={Math.max(width - 12, 1)}
              height={height}
              clipPath={`clip-${id}`}
            >
              <TextOutput text={data} />
            </foreignObject>
          </g>
        </>
      );
    } else if (data.type === "video") {
      return (
        <>
           {/* <VideoImagePicker
              show={showCapture}
              setShow={setShowCapture}
            /> */}
        </>
      )} else if (data.type === "image") {
      const url = data.image_url.startsWith("http")
        ? data.image_url
        : `${API_ENDPOINT}/${data.image_url}`;
      // Fit image to container, keep aspect ratio, center
      return (
        <>
          <clipPath id={`clip-${id}`}>
            <rect
              width={Math.max(d.x1 - d.x0, 1)}
              height={Math.max(d.y1 - d.y0, 1)}
              rx={8}
              ry={8}
            />
          </clipPath>
          <g clipPath={`url(#clip-${id})`}>
            <image
              x={0}
              y={0}
              width={width}
              height={height}
              href={url}
              preserveAspectRatio="xMidYMid meet"
            />
          </g>
        </>
      );
    } else {
      return (
        <rect
          id={id + "_rect"}
          width={d.x1 - d.x0}
          height={d.y1 - d.y0}
          fill={"#FFFFFF"}
          rx={8}
          ry={8}
          opacity={0.5}
        />
      );
    }
  };

  return (
    <>
      <div className={styles.container} ref={chartRef}>
        <svg width={dms.width} height={dms.height} className={styles.treemap}>
          <g
            transform={`translate(${[dms.marginLeft, dms.marginTop].join(
              ","
            )})`}
            height={dms.boundedHeight}
            width={dms.boundedWidth}
          >
            {root.map((d, i) => (
              <g key={i}>
                <g key={d.data.id} transform={`translate(${d.x0},${d.y0})`}>
                  <title>{d.data.title}</title>
                  <rect
                    id={`rect-${d.data.id}`}
                    width={d.x1 - d.x0}
                    height={d.y1 - d.y0}
                    fill={"#1A1617AA"}
                    rx={8}
                    ry={8}
                    opacity={0.75}
                  />
                  <clipPath id={`clip-${d.data.id}`}>
                    <rect
                      width={Math.max(d.x1 - d.x0 - 4, 1)}
                      height={Math.max(d.y1 - d.y0 - 4, 1)}
                      rx={8}
                      ry={8}
                      opacity={0.5}
                    />
                  </clipPath>
                  <text
                    clipPath={`url(#clip-${d.data.id})`}
                    style={{ fontSize: "1em", fill: "white" }}
                  >
                    <tspan dx={18} y={30}>
                      {d.data.title}
                    </tspan>
                  </text>
                </g>
                {d.children &&
                  d.children.map((child, j) => {
                    // Create a gradient of colorful backgrounds using LEGO colors
                    const colors = [
                      { r: 173, g: 216, b: 230 }, // Light blue
                      { r: 255, g: 228, b: 181 }, // Light peach
                      { r: 221, g: 160, b: 221 }, // Light plum
                      { r: 144, g: 238, b: 144 }, // Light green
                      { r: 255, g: 218, b: 185 }, // Light coral
                      { r: 176, g: 224, b: 230 }, // Powder blue
                      { r: 255, g: 239, b: 213 }, // Papaya whip
                      { r: 230, g: 230, b: 250 }, // Lavender
                    ];
                    const color = colors[j % colors.length];
                    const fillColor = `rgba(${color.r}, ${color.g}, ${color.b}, 0.85)`;
                    return (
                      <g
                        key={child.data.id}
                        transform={`translate(${child.x0},${child.y0})`}
                        onClick={() => {
                          if (child.data.data) {
                            outputDisplayRef.current?.activateOutputDisplay(child.data.data);
                          }
                          console.log(d.data);
                        }}
                        className={styles.item}
                      >
                        {child.data.data ? (
                          generateContent(
                            child.data.id,
                            child.data.title,
                            child.data.data,
                            new Dimensions(child.x0, child.y0, child.x1, child.y1),
                            fillColor
                          )
                        ) : (
                          <rect
                            id={child.id + "_rect"}
                            width={child.x1 - child.x0}
                            height={child.y1 - d.y0}
                            fill={fillColor}
                            rx={8}
                            ry={8}
                            opacity={0.85}
                          />
                        )}
                      </g>
                    );
                  })}
              </g>
            ))}
          </g>
        </svg>
      </div>
      <OutputDisplay ref={outputDisplayRef} />
    </>
  );
};

export default Output;
