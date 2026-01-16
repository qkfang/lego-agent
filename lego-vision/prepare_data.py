#!/usr/bin/env python3
"""
Image Upload and Tagging Automation Script

This script helps automate the process of uploading images and creating annotations
for Azure Custom Vision object detection training.
"""

import os
import json
from typing import List, Dict
from PIL import Image


class TrainingDataManager:
    """Manages training data preparation and annotation"""
    
    def __init__(self, data_dir: str = "../testdata"):
        """
        Initialize the training data manager
        
        Args:
            data_dir: Directory containing training images
        """
        self.data_dir = data_dir
        self.annotations_file = os.path.join(data_dir, "annotations.json")
    
    def scan_images(self, extensions: List[str] = None) -> List[str]:
        """
        Scan directory for image files
        
        Args:
            extensions: List of image extensions to look for
            
        Returns:
            List of image file paths
        """
        if extensions is None:
            extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        
        images = []
        for root, dirs, files in os.walk(self.data_dir):
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    images.append(os.path.join(root, file))
        
        return images
    
    def get_image_dimensions(self, image_path: str) -> tuple:
        """
        Get image dimensions
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (width, height)
        """
        with Image.open(image_path) as img:
            return img.size
    
    def create_annotation_template(self, image_paths: List[str]) -> Dict:
        """
        Create an annotation template JSON file
        
        Args:
            image_paths: List of image paths to create annotations for
            
        Returns:
            Annotation template dictionary
        """
        annotations = {
            "images": [],
            "tags": [
                "lego_robot",
                "lego_brick",
                "lego_wheel",
                "lego_minifig"
            ],
            "description": "Training annotations for Azure Custom Vision"
        }
        
        for image_path in image_paths:
            width, height = self.get_image_dimensions(image_path)
            
            image_entry = {
                "path": os.path.relpath(image_path, self.data_dir),
                "width": width,
                "height": height,
                "regions": [
                    # Example region - you need to fill in actual coordinates
                    # {
                    #     "tag": "lego_robot",
                    #     "left": 0.1,     # normalized x position (0-1)
                    #     "top": 0.2,      # normalized y position (0-1)
                    #     "width": 0.3,    # normalized width (0-1)
                    #     "height": 0.4    # normalized height (0-1)
                    # }
                ]
            }
            annotations["images"].append(image_entry)
        
        return annotations
    
    def save_annotations(self, annotations: Dict, output_file: str = None) -> None:
        """
        Save annotations to JSON file
        
        Args:
            annotations: Annotation dictionary
            output_file: Output file path (defaults to annotations.json)
        """
        if output_file is None:
            output_file = self.annotations_file
        
        with open(output_file, 'w') as f:
            json.dump(annotations, f, indent=2)
        
        print(f"Annotations saved to: {output_file}")
    
    def load_annotations(self, input_file: str = None) -> Dict:
        """
        Load annotations from JSON file
        
        Args:
            input_file: Input file path (defaults to annotations.json)
            
        Returns:
            Annotation dictionary
        """
        if input_file is None:
            input_file = self.annotations_file
        
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Annotations file not found: {input_file}")
        
        with open(input_file, 'r') as f:
            return json.load(f)
    
    def prepare_training_data(self, annotations_file: str = None) -> List[Dict]:
        """
        Convert annotations to format expected by training script
        
        Args:
            annotations_file: Path to annotations JSON file
            
        Returns:
            List of training data dictionaries
        """
        annotations = self.load_annotations(annotations_file)
        
        training_data = []
        for image_entry in annotations["images"]:
            # Convert relative path to absolute path
            image_path = os.path.join(self.data_dir, image_entry["path"])
            
            # Ensure path exists
            if not os.path.exists(image_path):
                print(f"Warning: Image not found: {image_path}")
                continue
            
            training_entry = {
                "path": image_path,
                "regions": image_entry.get("regions", [])
            }
            training_data.append(training_entry)
        
        return training_data
    
    def validate_annotations(self, annotations: Dict = None) -> tuple:
        """
        Validate annotation data
        
        Args:
            annotations: Annotation dictionary (loads from file if None)
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        if annotations is None:
            try:
                annotations = self.load_annotations()
            except Exception as e:
                return False, [f"Could not load annotations: {e}"]
        
        errors = []
        
        # Check required fields
        if "images" not in annotations:
            errors.append("Missing 'images' field in annotations")
        
        if "tags" not in annotations or len(annotations["tags"]) == 0:
            errors.append("No tags defined in annotations")
        
        # Validate each image entry
        for i, image_entry in enumerate(annotations.get("images", [])):
            if "path" not in image_entry:
                errors.append(f"Image {i}: Missing 'path' field")
                continue
            
            image_path = os.path.join(self.data_dir, image_entry["path"])
            if not os.path.exists(image_path):
                errors.append(f"Image {i}: File not found: {image_path}")
            
            # Validate regions
            for j, region in enumerate(image_entry.get("regions", [])):
                if "tag" not in region:
                    errors.append(f"Image {i}, Region {j}: Missing 'tag' field")
                
                if "left" not in region or "top" not in region:
                    errors.append(f"Image {i}, Region {j}: Missing position fields")
                
                if "width" not in region or "height" not in region:
                    errors.append(f"Image {i}, Region {j}: Missing dimension fields")
                
                # Validate normalized coordinates
                for coord in ["left", "top", "width", "height"]:
                    if coord in region:
                        value = region[coord]
                        if not (0 <= value <= 1):
                            errors.append(
                                f"Image {i}, Region {j}: '{coord}' must be between 0 and 1, got {value}"
                            )
        
        return len(errors) == 0, errors


def main():
    """Main function for training data preparation"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Prepare training data for Azure Custom Vision"
    )
    parser.add_argument(
        "--data-dir",
        default="../testdata",
        help="Directory containing training images"
    )
    parser.add_argument(
        "--create-template",
        action="store_true",
        help="Create annotation template from images in directory"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate existing annotations file"
    )
    
    args = parser.parse_args()
    
    manager = TrainingDataManager(args.data_dir)
    
    if args.create_template:
        print("Scanning for images...")
        images = manager.scan_images()
        print(f"Found {len(images)} images")
        
        print("\nCreating annotation template...")
        annotations = manager.create_annotation_template(images)
        
        output_file = os.path.join(args.data_dir, "annotations.json")
        manager.save_annotations(annotations, output_file)
        
        print("\nNext steps:")
        print(f"1. Edit {output_file}")
        print("2. Add bounding box coordinates for each object")
        print("3. Run with --validate to check your annotations")
        print("4. Use the annotations with train.py to train the model")
    
    elif args.validate:
        print("Validating annotations...")
        is_valid, errors = manager.validate_annotations()
        
        if is_valid:
            print("✓ Annotations are valid!")
            
            # Show summary
            annotations = manager.load_annotations()
            print(f"\nSummary:")
            print(f"  Images: {len(annotations.get('images', []))}")
            print(f"  Tags: {', '.join(annotations.get('tags', []))}")
            
            total_regions = sum(
                len(img.get('regions', [])) 
                for img in annotations.get('images', [])
            )
            print(f"  Total regions: {total_regions}")
        else:
            print("✗ Validation failed with errors:")
            for error in errors:
                print(f"  - {error}")
    
    else:
        print("Please specify an action: --create-template or --validate")
        parser.print_help()


if __name__ == "__main__":
    main()
