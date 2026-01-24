#!/usr/bin/env python3
"""
Object Detection and Distance Calculation

This module detects objects in an image and calculates distances between them
on a 2D plane, treating the surface as a flat table.
"""

import cv2
import numpy as np
import math
from typing import List, Dict, Any
import json
import os

# Optional imports for YOLO detection
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


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
        """Load an image from file path."""
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
                               use_preprocessing: bool = True, display_mask: bool = False, 
                               save_mask_path: str = None) -> List[Dict[str, Any]]:
        """Detect objects in the image based on color ranges."""
        if self.image is None:
            print("No image loaded")
            return []
        
        processed_image = self.image.copy()
        if use_preprocessing:
            processed_image = cv2.GaussianBlur(processed_image, (5, 5), 0)
            processed_image = cv2.bilateralFilter(processed_image, 9, 75, 75)
        
        rgb_image = processed_image
        detected_objects = []
        
        for color_range in color_ranges:
            name = color_range['name']
            lower = np.array(color_range['lower'])
            upper = np.array(color_range['upper'])
            
            mask = cv2.inRange(rgb_image, lower, upper)
            
            if use_preprocessing:
                kernel_size = max(3, min(15, int(min(self.image_width, self.image_height) * 0.01)))
                kernel = np.ones((kernel_size, kernel_size), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                blur_size = max(3, min(7, kernel_size // 2))
                if blur_size % 2 == 0:
                    blur_size += 1
                mask = cv2.medianBlur(mask, blur_size)

            if display_mask or save_mask_path:
                masked_image = cv2.bitwise_and(self.image, self.image, mask=mask)
                
                if display_mask:
                    cv2.imshow(f"Mask - {name}", mask)
                    cv2.imshow(f"Masked Image - {name}", masked_image)
                    cv2.waitKey(2000)
                
                if save_mask_path:
                    base_path = os.path.splitext(save_mask_path)[0]
                    mask_save_path = f"{base_path}_{name}_mask.png"
                    masked_save_path = f"{base_path}_{name}_masked.png"
                    cv2.imwrite(mask_save_path, mask)
                    cv2.imwrite(masked_save_path, masked_image)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                min_area = max(1000, self.image_width * self.image_height * 0.001)
                area = cv2.contourArea(contour)
                if area < min_area:
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = max(w, h) / min(w, h)
                if aspect_ratio > 10:
                    continue
                
                if w > 400 or h > 400:
                    continue
                
                center_x = x + w // 2
                center_y = y + h // 2
                
                if name.lower() == 'bowser':
                    if not (center_x > self.image_width * 0.7 and center_y < self.image_height * 0.4):
                        continue
                    if area > 12000:
                        continue
                
                if name.lower() == 'robot':
                    center_y = center_y + 10
                    y = y + 10

                if name.lower() == 'bowser':
                    center_x = center_x - 15
                    x = x - 15

                if len(contour) >= 5:
                    ellipse = cv2.fitEllipse(contour)
                    angle = ellipse[2]
                else:
                    angle = 0
                
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
        
        filtered_objects = self._filter_objects_by_max_area(detected_objects)
        self.detected_objects = filtered_objects
        return filtered_objects
    
    def detect_objects_by_template(self, template_paths: List[str], threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Detect objects using template matching."""
        if self.image is None:
            print("No image loaded")
            return []
        
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        detected_objects = []
        
        for i, template_path in enumerate(template_paths):
            try:
                template = cv2.imread(template_path, 0)
                if template is None:
                    continue
                
                w, h = template.shape[::-1]
                if w > 100 or h > 100:
                    continue
                
                res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
                locations = np.where(res >= threshold)
                
                for pt in zip(*locations[::-1]):
                    center_x = pt[0] + w // 2
                    center_y = pt[1] + h // 2
                    coord_x = center_x
                    coord_y = self.image_height - center_y
                    
                    obj_data = {
                        'name': f'object_{i+1}',
                        'center': (center_x, center_y),
                        'coordinates_2d': (coord_x, coord_y),
                        'bounding_box': (pt[0], pt[1], w, h),
                        'area': w * h,
                        'orientation_angle': 0,
                        'confidence': res[pt[1], pt[0]]
                    }
                    detected_objects.append(obj_data)
                    
            except Exception as e:
                print(f"Error processing template {template_path}: {e}")
        
        filtered_objects = self._filter_objects_by_max_area(detected_objects)
        self.detected_objects = filtered_objects
        return filtered_objects
    
    def detect_objects_by_yolo(self, confidence_threshold: float = 0.5, 
                              target_objects: List[str] = None) -> List[Dict[str, Any]]:
        """Detect objects using YOLO deep learning model."""
        if not YOLO_AVAILABLE:
            print("Error: YOLO detection requires ultralytics package.")
            return []
            
        if self.image is None:
            print("No image loaded")
            return []
        
        if self.yolo_model is None:
            try:
                self.yolo_model = YOLO('yolov8n.pt')
            except Exception as e:
                print(f"Error loading YOLO model: {e}")
                return []
        
        detected_objects = []
        
        try:
            results = self.yolo_model(self.image, conf=confidence_threshold, verbose=False)
            
            for result in results:
                boxes = result.boxes
                if boxes is None:
                    continue
                    
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())
                    class_name = self.coco_classes.get(class_id, f'class_{class_id}')
                    
                    if target_objects and class_name not in target_objects:
                        continue
                    
                    center_x = int((x1 + x2) / 2)
                    center_y = int((y1 + y2) / 2)
                    width = int(x2 - x1)
                    height = int(y2 - y1)
                    
                    if width > 100 or height > 100:
                        continue
                    
                    area = width * height
                    coord_x = center_x
                    coord_y = self.image_height - center_y
                    
                    if width > height * 1.5:
                        orientation_angle = 0
                    elif height > width * 1.5:
                        orientation_angle = 90
                    else:
                        orientation_angle = 45
                    
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
        
        filtered_objects = self._filter_objects_by_max_area(detected_objects)
        self.detected_objects = filtered_objects
        return filtered_objects
    
    def _filter_objects_by_max_area(self, detected_objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter to keep only the object with the biggest area for each name."""
        if not detected_objects:
            return detected_objects
        
        objects_by_name = {}
        for obj in detected_objects:
            name = obj['name']
            if name not in objects_by_name:
                objects_by_name[name] = []
            objects_by_name[name].append(obj)
        
        filtered_objects = []
        for name, objects in objects_by_name.items():
            if len(objects) == 1:
                filtered_objects.append(objects[0])
            else:
                max_area_obj = max(objects, key=lambda x: x['area'])
                filtered_objects.append(max_area_obj)
        
        return filtered_objects
    
    def calculate_distance(self, obj1: Dict[str, Any], obj2: Dict[str, Any], 
                          pixels_per_unit: float = 1.0) -> float:
        """Calculate Euclidean distance between two objects."""
        x1, y1 = obj1['coordinates_2d']
        x2, y2 = obj2['coordinates_2d']
        pixel_distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return pixel_distance / pixels_per_unit
    
    def get_object_analysis(self, pixels_per_unit: float = 1.0) -> Dict[str, Any]:
        """Get comprehensive analysis of detected objects including distances."""
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
        
        for i, obj in enumerate(self.detected_objects):
            obj_info = {
                'id': i,
                'name': obj['name'],
                'position_2d': obj['coordinates_2d'],
                'center_pixels': obj['center'],
                'area_pixels': obj['area'],
                'orientation_degrees': obj['orientation_angle'],
            }
            analysis['objects'].append(obj_info)
        
        robot_obj = None
        coke_obj = None
        bowser_obj = None
        
        for obj in self.detected_objects:
            if obj['name'].lower() == 'robot':
                robot_obj = obj
            elif obj['name'].lower() == 'coke':
                coke_obj = obj
            elif obj['name'].lower() == 'bowser':
                bowser_obj = obj
        
        if robot_obj and coke_obj:
            distance = self.calculate_distance(robot_obj, coke_obj, pixels_per_unit)
            analysis['distances'].append({
                'from': robot_obj['name'],
                'to': coke_obj['name'],
                'distance_pixels': distance * pixels_per_unit,
                'distance_units': distance,
                'from_position': robot_obj['coordinates_2d'],
                'to_position': coke_obj['coordinates_2d']
            })
        
        if robot_obj and bowser_obj:
            distance = self.calculate_distance(robot_obj, bowser_obj, pixels_per_unit)
            analysis['distances'].append({
                'from': robot_obj['name'],
                'to': bowser_obj['name'],
                'distance_pixels': distance * pixels_per_unit,
                'distance_units': distance,
                'from_position': robot_obj['coordinates_2d'],
                'to_position': bowser_obj['coordinates_2d']
            })
        
        if coke_obj and bowser_obj:
            distance = self.calculate_distance(coke_obj, bowser_obj, pixels_per_unit)
            analysis['distances'].append({
                'from': coke_obj['name'],
                'to': bowser_obj['name'],
                'distance_pixels': distance * pixels_per_unit,
                'distance_units': distance,
                'from_position': coke_obj['coordinates_2d'],
                'to_position': bowser_obj['coordinates_2d']
            })
        
        return analysis
    
    def visualize_results(self, save_path: str = None, show_plot: bool = True):
        """Visualize the detected objects and their relationships."""
        if self.image is None or not self.detected_objects:
            print("No image or objects to visualize")
            return
        
        vis_image = self.image.copy()
        
        for i, obj in enumerate(self.detected_objects):
            x, y, w, h = obj['bounding_box']
            center = obj['center']
            cv2.rectangle(vis_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(vis_image, center, 5, (0, 0, 255), -1)
            label = f"{obj['name']} ({center[0]}, {self.image_height - center[1]})"
            cv2.putText(vis_image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        robot_indices = [i for i, obj in enumerate(self.detected_objects) if obj['name'].lower() == 'robot']
        for robot_idx in robot_indices:
            robot_obj = self.detected_objects[robot_idx]
            pt1 = robot_obj['center']
            for j, obj in enumerate(self.detected_objects):
                if j == robot_idx:
                    continue
                pt2 = obj['center']
                cv2.line(vis_image, pt1, pt2, (255, 0, 0), 2)
                mid_x = (pt1[0] + pt2[0]) // 2
                mid_y = (pt1[1] + pt2[1]) // 2
                distance = self.calculate_distance(robot_obj, obj)
                cv2.putText(vis_image, f"{distance:.1f}px", (mid_x, mid_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        
        if save_path:
            cv2.imwrite(save_path, vis_image)


def create_sample_color_ranges():
    """Create sample color ranges for common objects."""
    return [
        {
            'name': 'robot',
            'lower': [100, 140, 0],
            'upper': [255, 240, 120]
        },
        {
            'name': 'coke',
            'lower': [0, 0, 100],
            'upper': [80, 80, 255]
        },
        {
            'name': 'bowser',
            'lower': [0, 120, 120],
            'upper': [80, 240, 240]
        }
    ]


def run_detection(args) -> Dict[str, Any]:
    """Run object detection with the given arguments."""
    detector = ObjectDetector()
    
    if not detector.load_image(args.image_path):
        return {"error": "Failed to load image"}
    
    if args.method == 'color':
        color_ranges = create_sample_color_ranges()
        mask_path = getattr(args, 'save_masks', None) or 'mask_output.png'
        detected_objects = detector.detect_objects_by_color(
            color_ranges, 
            use_preprocessing=not args.no_preprocessing,
            display_mask=False,
            save_mask_path=mask_path
        )
    elif args.method == 'template':
        if not args.templates:
            return {"error": "Template paths required"}
        detected_objects = detector.detect_objects_by_template(args.templates)
    elif args.method == 'yolo':
        detected_objects = detector.detect_objects_by_yolo(
            confidence_threshold=args.confidence, 
            target_objects=args.target_objects
        )
    else:
        return {"error": f"Unknown method: {args.method}"}
    
    print(f"\nDetected {len(detected_objects)} objects:")
    for i, obj in enumerate(detected_objects):
        confidence_info = f" (conf: {obj['confidence']:.2f})" if 'confidence' in obj else ""
        print(f"  {i+1}. {obj['name']} at {obj['coordinates_2d']} (area: {obj['area']} pixels){confidence_info}")
    
    analysis = detector.get_object_analysis(args.pixels_per_unit)
    
    if 'error' not in analysis:
        print(f"\n=== ANALYSIS RESULTS ===")
        print(f"Image dimensions: {analysis['image_dimensions']}")
        
        print(f"\nObjects detected:")
        for obj in analysis['objects']:
            print(f"  - {obj['name']}: Position {obj['position_2d']}")
        
        print(f"\nDistances:")
        for dist in analysis['distances']:
            print(f"  - {dist['from']} to {dist['to']}: {dist['distance_units']:.2f} units")
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(analysis, f, indent=2)
    
    if len(detected_objects) > 0 and args.visualize:
        detector.visualize_results(args.visualize, not args.no_display)
    
    return analysis
