#!/usr/bin/env python3
"""
Azure Custom Vision Model Deployment and Prediction Script

This script handles deploying trained models and making predictions
on new images using the Azure Custom Vision service.
"""

import os
import sys
from typing import List, Dict
from dotenv import load_dotenv
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials
from PIL import Image, ImageDraw, ImageFont


class CustomVisionPredictor:
    """Handles predictions using deployed Azure Custom Vision models"""
    
    def __init__(self):
        """Initialize the Custom Vision predictor with credentials from environment"""
        load_dotenv()
        
        self.prediction_endpoint = os.getenv("PREDICTION_ENDPOINT")
        self.prediction_key = os.getenv("PREDICTION_KEY")
        self.project_id = os.getenv("PROJECT_ID")
        self.publish_iteration_name = os.getenv("PUBLISH_ITERATION_NAME", "production")
        
        if not all([self.prediction_endpoint, self.prediction_key, self.project_id]):
            raise ValueError(
                "Missing required environment variables. "
                "Please set PREDICTION_ENDPOINT, PREDICTION_KEY, and PROJECT_ID"
            )
        
        # Initialize the Custom Vision prediction client
        credentials = ApiKeyCredentials(in_headers={"Prediction-key": self.prediction_key})
        self.predictor = CustomVisionPredictionClient(self.prediction_endpoint, credentials)
    
    def predict_image_file(
        self, 
        image_path: str, 
        threshold: float = 0.5
    ) -> List[Dict]:
        """
        Make predictions on an image file
        
        Args:
            image_path: Path to image file
            threshold: Minimum confidence threshold (0-1)
            
        Returns:
            List of detected objects with bounding boxes and confidence scores
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        print(f"Analyzing image: {image_path}")
        
        with open(image_path, "rb") as image_file:
            results = self.predictor.detect_image(
                self.project_id,
                self.publish_iteration_name,
                image_file
            )
        
        # Filter predictions by threshold
        detections = []
        for prediction in results.predictions:
            if prediction.probability >= threshold:
                detection = {
                    "tag": prediction.tag_name,
                    "confidence": prediction.probability,
                    "bounding_box": {
                        "left": prediction.bounding_box.left,
                        "top": prediction.bounding_box.top,
                        "width": prediction.bounding_box.width,
                        "height": prediction.bounding_box.height
                    }
                }
                detections.append(detection)
        
        return detections
    
    def predict_image_url(
        self, 
        image_url: str, 
        threshold: float = 0.5
    ) -> List[Dict]:
        """
        Make predictions on an image from a URL
        
        Args:
            image_url: URL of the image
            threshold: Minimum confidence threshold (0-1)
            
        Returns:
            List of detected objects with bounding boxes and confidence scores
        """
        print(f"Analyzing image from URL: {image_url}")
        
        results = self.predictor.detect_image_url(
            self.project_id,
            self.publish_iteration_name,
            url=image_url
        )
        
        # Filter predictions by threshold
        detections = []
        for prediction in results.predictions:
            if prediction.probability >= threshold:
                detection = {
                    "tag": prediction.tag_name,
                    "confidence": prediction.probability,
                    "bounding_box": {
                        "left": prediction.bounding_box.left,
                        "top": prediction.bounding_box.top,
                        "width": prediction.bounding_box.width,
                        "height": prediction.bounding_box.height
                    }
                }
                detections.append(detection)
        
        return detections
    
    def visualize_detections(
        self,
        image_path: str,
        detections: List[Dict],
        output_path: str = None
    ) -> str:
        """
        Visualize detections on the image
        
        Args:
            image_path: Path to input image
            detections: List of detections from predict_image_file
            output_path: Path to save visualization (optional)
            
        Returns:
            Path to saved visualization
        """
        # Load image
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        
        width, height = image.size
        
        # Try to load a font, fallback to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Draw bounding boxes
        for detection in detections:
            bbox = detection["bounding_box"]
            tag = detection["tag"]
            confidence = detection["confidence"]
            
            # Convert normalized coordinates to pixel coordinates
            left = int(bbox["left"] * width)
            top = int(bbox["top"] * height)
            right = int((bbox["left"] + bbox["width"]) * width)
            bottom = int((bbox["top"] + bbox["height"]) * height)
            
            # Draw rectangle
            draw.rectangle([left, top, right, bottom], outline="red", width=3)
            
            # Draw label
            label = f"{tag}: {confidence:.2%}"
            
            # Draw label background
            text_bbox = draw.textbbox((left, top - 25), label, font=font)
            draw.rectangle(text_bbox, fill="red")
            draw.text((left, top - 25), label, fill="white", font=font)
        
        # Save or create output path
        if output_path is None:
            base, ext = os.path.splitext(image_path)
            output_path = f"{base}_detected{ext}"
        
        image.save(output_path)
        print(f"Visualization saved to: {output_path}")
        
        return output_path


def main():
    """Main function for prediction and deployment"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Make predictions using Azure Custom Vision model"
    )
    parser.add_argument(
        "image_path",
        help="Path to image file for prediction"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Confidence threshold for detections (0-1, default: 0.5)"
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Create visualization with bounding boxes"
    )
    parser.add_argument(
        "--output",
        help="Output path for visualization"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize predictor
        predictor = CustomVisionPredictor()
        
        # Make prediction
        detections = predictor.predict_image_file(args.image_path, args.threshold)
        
        # Display results
        print(f"\nDetected {len(detections)} objects:")
        for i, detection in enumerate(detections, 1):
            print(f"\n{i}. {detection['tag']}")
            print(f"   Confidence: {detection['confidence']:.2%}")
            bbox = detection['bounding_box']
            print(f"   Bounding Box: left={bbox['left']:.3f}, top={bbox['top']:.3f}, "
                  f"width={bbox['width']:.3f}, height={bbox['height']:.3f}")
        
        # Create visualization if requested
        if args.visualize:
            output_path = predictor.visualize_detections(
                args.image_path,
                detections,
                args.output
            )
            print(f"\nVisualization saved to: {output_path}")
        
        # Return success
        return 0
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
