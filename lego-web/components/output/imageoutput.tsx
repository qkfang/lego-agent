import type { ImageData } from "store/output";
import styles from "./imageoutput.module.scss";

type Props = {
  image: ImageData;
  height: number;
  width: number;
};

const ImageOutput = ({ image }: { image: ImageData }) => { 
  return <div className={styles.container}>{image.description}</div>;
};

export default ImageOutput;
