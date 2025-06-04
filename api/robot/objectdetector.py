#!/usr/bin/env python3
"""
Object Detection and Distance Calculation Script

This script detects objects in an image and calculates distances between them
on a 2D plane, treating the surface as a flat table.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import argparse
import math
from typing import List, Tuple, Dict, Any
import json
import os

# Optional imports for YOLO detection
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("Warning: ultralytics not available. YOLO detection will be disabled.")


class ObjectDetector:
    """
    A class for detecting objects in images and calculating distances between them.
    """
    
    def __init__(self):
        """Initialize the ObjectDetector with default parameters."""
        self.detected_objects = []
        self.image = None
        self.image_height = 0
        self.image_width = 0
        self.yolo_model = None
        
        # COCO class names for common objects
        self.coco_classes = {
            0: 'person', 47: 'apple', 48: 'banana', 49: 'orange', 50: 'carrot',
            51: 'hot_dog', 52: 'pizza', 53: 'donut', 54: 'cake', 39: 'bottle',
            40: 'wine_glass', 41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon',
            45: 'bowl', 67: 'cell_phone', 68: 'microwave', 69: 'oven', 70: 'toaster',
            71: 'sink', 72: 'refrigerator', 73: 'book', 74: 'clock', 75: 'vase',
            76: 'scissors', 77: 'teddy_bear', 78: 'hair_drier', 79: 'toothbrush',
            1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane', 5: 'bus',
            6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic_light', 10: 'fire_hydrant',
            11: 'stop_sign', 12: 'parking_meter', 13: 'bench', 14: 'bird', 15: 'cat',
            16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow', 20: 'elephant',
            21: 'bear', 22: 'zebra', 23: 'giraffe', 24: 'backpack', 25: 'umbrella',
            26: 'handbag', 27: 'tie', 28: 'suitcase', 29: 'frisbee', 30: 'skis',
            31: 'snowboard', 32: 'sports_ball', 33: 'kite', 34: 'baseball_bat',
            35: 'baseball_glove', 36: 'skateboard', 37: 'surfboard', 38: 'tennis_racket'
        }
        
    def load_image(self, image_path: str) -> bool:
        """
        Load an image from file path.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            bool: True if image loaded successfully, False otherwise
        """
        try:
            self.image = cv2.imread(image_path)
            if self.image is None:
                print(f"Error: Could not load image from {image_path}")
                return False
            
            self.image_height, self.image_width = self.image.shape[:2]
            print(f"Image loaded successfully: {self.image_width}x{self.image_height}")
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False
    
    def detect_objects_by_color(self, color_ranges: List[Dict[str, Any]], 
                               use_preprocessing: bool = True) -> List[Dict[str, Any]]:
        """
        Detect objects in the image based on color ranges with improved noise handling.
        
        Args:
            color_ranges (List[Dict]): List of color range dictionaries with 'name', 'lower', 'upper' keys
            use_preprocessing (bool): Whether to apply noise reduction preprocessing
            
        Returns:
            List[Dict]: List of detected objects with their properties
        """
        if self.image is None:
            print("No image loaded")
            return []
        
        # Apply preprocessing for complex backgrounds
        processed_image = self.image.copy()
        if use_preprocessing:
            # Apply Gaussian blur to reduce noise
            processed_image = cv2.GaussianBlur(processed_image, (5, 5), 0)
            
            # Apply bilateral filter to reduce noise while keeping edges sharp
            processed_image = cv2.bilateralFilter(processed_image, 9, 75, 75)
        
        # Convert BGR to HSV for better color detection
        hsv = cv2.cvtColor(processed_image, cv2.COLOR_BGR2HSV)
        detected_objects = []
        
        for color_range in color_ranges:
            name = color_range['name']
            lower = np.array(color_range['lower'])
            upper = np.array(color_range['upper'])
            
            # Create mask for the color range
            mask = cv2.inRange(hsv, lower, upper)
            
            # Apply morphological operations to reduce noise
            if use_preprocessing:
                # Remove small noise
                kernel = np.ones((3, 3), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                # Fill holes
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                # Smooth edges
                mask = cv2.medianBlur(mask, 5)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Filter small contours (adaptive threshold based on image size)
                min_area = max(500, self.image_width * self.image_height * 0.001)  # At least 0.1% of image
                area = cv2.contourArea(contour)
                if area < min_area:
                    continue
                
                # Filter contours that are too elongated (likely noise)
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = max(w, h) / min(w, h)
                if aspect_ratio > 10:  # Skip very elongated shapes
                    continue
                
                # Calculate center point
                center_x = x + w // 2
                center_y = y + h // 2
                
                # Calculate orientation (angle of the major axis)
                if len(contour) >= 5:
                    ellipse = cv2.fitEllipse(contour)
                    angle = ellipse[2]
                else:
                    angle = 0
                
                # Convert image coordinates to 2D coordinate system
                # (0,0) at bottom-left, with y increasing upward
                coord_x = center_x
                coord_y = self.image_height - center_y
                
                obj_data = {
                    'name': name,
                    'center': (center_x, center_y),
                    'coordinates_2d': (coord_x, coord_y),
                    'bounding_box': (x, y, w, h),
                    'area': area,
                    'orientation_angle': angle,
                    'contour': contour,
                    'detection_method': 'color'
                }
                
                detected_objects.append(obj_data)
        
        self.detected_objects = detected_objects
        return detected_objects
    
    def detect_objects_by_template(self, template_paths: List[str], threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        Detect objects using template matching.
        
        Args:
            template_paths (List[str]): List of template image paths
            threshold (float): Matching threshold (0-1)
            
        Returns:
            List[Dict]: List of detected objects
        """
        if self.image is None:
            print("No image loaded")
            return []
        
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        detected_objects = []
        
        for i, template_path in enumerate(template_paths):
            try:
                template = cv2.imread(template_path, 0)
                if template is None:
                    print(f"Could not load template: {template_path}")
                    continue
                
                w, h = template.shape[::-1]
                
                # Perform template matching
                res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
                locations = np.where(res >= threshold)
                
                for pt in zip(*locations[::-1]):
                    center_x = pt[0] + w // 2
                    center_y = pt[1] + h // 2
                    
                    # Convert to 2D coordinate system
                    coord_x = center_x
                    coord_y = self.image_height - center_y
                    
                    obj_data = {
                        'name': f'object_{i+1}',
                        'center': (center_x, center_y),
                        'coordinates_2d': (coord_x, coord_y),
                        'bounding_box': (pt[0], pt[1], w, h),
                        'area': w * h,
                        'orientation_angle': 0,  # Template matching doesn't provide orientation
                        'confidence': res[pt[1], pt[0]]
                    }
                    
                    detected_objects.append(obj_data)
                    
            except Exception as e:
                print(f"Error processing template {template_path}: {e}")
        
        self.detected_objects = detected_objects
        return detected_objects
    
    def detect_objects_by_yolo(self, confidence_threshold: float = 0.5, 
                              target_objects: List[str] = None) -> List[Dict[str, Any]]:
        """
        Detect objects using YOLO deep learning model.
        
        Args:
            confidence_threshold (float): Minimum confidence score for detections (0-1)
            target_objects (List[str]): List of specific object names to detect (e.g., ['apple', 'bottle'])
                                       If None, detects all objects
            
        Returns:
            List[Dict]: List of detected objects
        """
        if not YOLO_AVAILABLE:
            print("Error: YOLO detection requires ultralytics package. Install with: pip install ultralytics")
            return []
            
        if self.image is None:
            print("No image loaded")
            return []
        
        # Initialize YOLO model if not already done
        if self.yolo_model is None:
            try:
                print("Loading YOLO model (this may take a moment on first run)...")
                self.yolo_model = YOLO('yolov8n.pt')  # Use nano model for speed
                print("YOLO model loaded successfully")
            except Exception as e:
                print(f"Error loading YOLO model: {e}")
                return []
        
        detected_objects = []
        
        try:
            # Run YOLO inference
            results = self.yolo_model(self.image, conf=confidence_threshold, verbose=False)
            
            for result in results:
                boxes = result.boxes
                if boxes is None:
                    continue
                    
                for box in boxes:
                    # Extract detection data
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    # Get class name
                    class_name = self.coco_classes.get(class_id, f'class_{class_id}')
                    
                    # Filter by target objects if specified
                    if target_objects and class_name not in target_objects:
                        continue
                    
                    # Calculate center and dimensions
                    center_x = int((x1 + x2) / 2)
                    center_y = int((y1 + y2) / 2)
                    width = int(x2 - x1)
                    height = int(y2 - y1)
                    area = width * height
                    
                    # Convert to 2D coordinate system (origin at bottom-left)
                    coord_x = center_x
                    coord_y = self.image_height - center_y
                    
                    # Estimate orientation from bounding box aspect ratio
                    if width > height * 1.5:
                        orientation_angle = 0  # Horizontal
                    elif height > width * 1.5:
                        orientation_angle = 90  # Vertical
                    else:
                        orientation_angle = 45  # Roughly square
                    
                    obj_data = {
                        'name': class_name,
                        'center': (center_x, center_y),
                        'coordinates_2d': (coord_x, coord_y),
                        'bounding_box': (int(x1), int(y1), width, height),
                        'area': area,
                        'orientation_angle': orientation_angle,
                        'confidence': confidence,
                        'class_id': class_id,
                        'detection_method': 'yolo'
                    }
                    
                    detected_objects.append(obj_data)
                    
        except Exception as e:
            print(f"Error during YOLO detection: {e}")
            return []
        
        self.detected_objects = detected_objects
        return detected_objects
    
    def calculate_distance(self, obj1: Dict[str, Any], obj2: Dict[str, Any], 
                          pixels_per_unit: float = 1.0) -> float:
        """
        Calculate Euclidean distance between two objects on a 2D plane.
        
        Args:
            obj1 (Dict): First object data
            obj2 (Dict): Second object data
            pixels_per_unit (float): Conversion factor from pixels to real-world units
            
        Returns:
            float: Distance between objects in specified units
        """
        x1, y1 = obj1['coordinates_2d']
        x2, y2 = obj2['coordinates_2d']
        
        # Calculate Euclidean distance
        pixel_distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        real_distance = pixel_distance / pixels_per_unit
        
        return real_distance
    
    def get_object_analysis(self, pixels_per_unit: float = 1.0) -> Dict[str, Any]:
        """
        Get comprehensive analysis of detected objects including distances.
        
        Args:
            pixels_per_unit (float): Conversion factor from pixels to real-world units
            
        Returns:
            Dict: Analysis results
        """
        if len(self.detected_objects) < 2:
            return {
                'error': 'At least 2 objects required for distance analysis',
                'objects_detected': len(self.detected_objects)
            }
        
        analysis = {
            'image_dimensions': (self.image_width, self.image_height),
            'coordinate_system': '2D with origin at bottom-left, y-axis pointing up',
            'objects': [],
            'distances': []
        }
        
        # Add object information
        for i, obj in enumerate(self.detected_objects):
            obj_info = {
                'id': i,
                'name': obj['name'],
                'position_2d': obj['coordinates_2d'],
                'center_pixels': obj['center'],
                'area_pixels': obj['area'],
                'orientation_degrees': obj['orientation_angle'],
                'facing_direction': self._get_facing_direction(obj['orientation_angle'])
            }
            analysis['objects'].append(obj_info)
        
        # Calculate all pairwise distances
        for i in range(len(self.detected_objects)):
            for j in range(i + 1, len(self.detected_objects)):
                obj1 = self.detected_objects[i]
                obj2 = self.detected_objects[j]
                distance = self.calculate_distance(obj1, obj2, pixels_per_unit)
                
                distance_info = {
                    'object1': obj1['name'],
                    'object2': obj2['name'],
                    'distance_pixels': distance * pixels_per_unit,
                    'distance_units': distance,
                    'object1_position': obj1['coordinates_2d'],
                    'object2_position': obj2['coordinates_2d']
                }
                analysis['distances'].append(distance_info)
        
        return analysis
    
    def _get_facing_direction(self, angle: float) -> str:
        """
        Convert angle to cardinal direction.
        
        Args:
            angle (float): Angle in degrees
            
        Returns:
            str: Cardinal direction
        """
        # Normalize angle to 0-360 range
        angle = angle % 360
        
        if 45 <= angle < 135:
            return "North"
        elif 135 <= angle < 225:
            return "West"
        elif 225 <= angle < 315:
            return "South"
        else:
            return "East"
    
    def visualize_results(self, save_path: str = None, show_plot: bool = True):
        """
        Visualize the detected objects and their relationships.
        
        Args:
            save_path (str): Path to save the visualization (optional)
            show_plot (bool): Whether to display the plot
        """
        if self.image is None or not self.detected_objects:
            print("No image or objects to visualize")
            return
        
        # Create a copy of the image for visualization
        vis_image = self.image.copy()
        
        # Draw detected objects
        for i, obj in enumerate(self.detected_objects):
            x, y, w, h = obj['bounding_box']
            center = obj['center']
            
            # Draw bounding box
            cv2.rectangle(vis_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw center point
            cv2.circle(vis_image, center, 5, (0, 0, 255), -1)
            
            # Draw label
            label = f"{obj['name']} ({center[0]}, {self.image_height - center[1]})"
            cv2.putText(vis_image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Draw distance lines between objects
        for i in range(len(self.detected_objects)):
            for j in range(i + 1, len(self.detected_objects)):
                pt1 = self.detected_objects[i]['center']
                pt2 = self.detected_objects[j]['center']
                cv2.line(vis_image, pt1, pt2, (255, 0, 0), 2)
                
                # Add distance label
                mid_x = (pt1[0] + pt2[0]) // 2
                mid_y = (pt1[1] + pt2[1]) // 2
                distance = self.calculate_distance(self.detected_objects[i], self.detected_objects[j])
                cv2.putText(vis_image, f"{distance:.1f}px", (mid_x, mid_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
       
        # Convert BGR to RGB for matplotlib
        vis_image_rgb = cv2.cvtColor(vis_image, cv2.COLOR_BGR2RGB)
        
        plt.figure(figsize=(12, 8))
        plt.imshow(vis_image_rgb)
        plt.title('Object Detection and Distance Analysis')
        plt.axis('off')
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            print(f"Visualization saved to: {save_path}")
        
        # if show_plot:
        #     plt.show()
        

def create_sample_color_ranges():
    """Create sample color ranges for common objects."""
    return [
        {
            'name': 'red',
            'lower': [0, 50, 50],    # Lower HSV for red
            'upper': [10, 255, 255]  # Upper HSV for red
        },
        {
            'name': 'blue',
            'lower': [100, 50, 50],   # Lower HSV for blue
            'upper': [130, 255, 255]  # Upper HSV for blue
        },
        {
            'name': 'green',
            'lower': [40, 50, 50],    # Lower HSV for green
            'upper': [80, 255, 255]   # Upper HSV for green
        }
    ]


def main():
    """Main function to run the object detection and distance calculation."""
    parser = argparse.ArgumentParser(description='Detect objects and calculate distances in images')
    parser.add_argument('image_path', help='Path to input image')
    parser.add_argument('--method', choices=['color', 'template', 'yolo'], default='color',
                       help='Detection method: color-based, template matching, or YOLO deep learning')
    parser.add_argument('--templates', nargs='+', help='Template image paths (for template method)')
    parser.add_argument('--target-objects', nargs='+', 
                       help='Specific objects to detect (for YOLO method, e.g., apple bottle car)')
    parser.add_argument('--confidence', type=float, default=0.5,
                       help='Confidence threshold for YOLO detection (0-1)')
    parser.add_argument('--output', help='Output JSON file path')
    parser.add_argument('--visualize', help='Save visualization image path')
    parser.add_argument('--pixels-per-unit', type=float, default=1.0,
                       help='Pixels per unit for distance measurement')
    parser.add_argument('--no-display', action='store_true', help='Don\'t display visualization')
    parser.add_argument('--no-preprocessing', action='store_true', 
                       help='Disable noise reduction preprocessing (for color method)')
    
    args = parser.parse_args()
    run(args)
    

def run(args):
    # Initialize detector
    detector = ObjectDetector()
    
    # Load image
    if not detector.load_image(args.image_path):
        return 1
    
    # Detect objects based on method
    if args.method == 'color':
        color_ranges = create_sample_color_ranges()
        detected_objects = detector.detect_objects_by_color(
            color_ranges, use_preprocessing=not args.no_preprocessing)
    elif args.method == 'template':
        if not args.templates:
            print("Template paths required for template matching method")
            return 1
        detected_objects = detector.detect_objects_by_template(args.templates)
    elif args.method == 'yolo':
        detected_objects = detector.detect_objects_by_yolo(
            confidence_threshold=args.confidence, 
            target_objects=args.target_objects)
        if not detected_objects and not YOLO_AVAILABLE:
            print("YOLO method requires ultralytics package. Install with: pip install ultralytics")
            return 1
    
    print(f"\nDetected {len(detected_objects)} objects:")
    for i, obj in enumerate(detected_objects):
        confidence_info = f" (conf: {obj['confidence']:.2f})" if 'confidence' in obj else ""
        print(f"  {i+1}. {obj['name']} at {obj['coordinates_2d']} (area: {obj['area']} pixels){confidence_info}")
    
    # Get analysis
    analysis = detector.get_object_analysis(args.pixels_per_unit)
    
    # Output results
    if 'error' in analysis:
        print(f"\nError: {analysis['error']}")
    else:
        print(f"\n=== ANALYSIS RESULTS ===")
        print(f"Image dimensions: {analysis['image_dimensions']}")
        print(f"Coordinate system: {analysis['coordinate_system']}")
        
        print(f"\nObjects detected:")
        for obj in analysis['objects']:
            print(f"  - {obj['name']}: Position {obj['position_2d']}, Facing {obj['facing_direction']}")
        
        print(f"\nDistances:")
        for dist in analysis['distances']:
            print(f"  - {dist['object1']} to {dist['object2']}: {dist['distance_units']:.2f} units")
    
    # Save results to JSON if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    # Visualize results
    if len(detected_objects) > 0:
        detector.visualize_results(args.visualize, not args.no_display)
    
    return analysis


if __name__ == "__main__":
    exit(main())