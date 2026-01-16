#!/usr/bin/env python3
"""
Azure Custom Vision Training Script for Object Detection

This script creates and trains a custom object detection model using Azure Custom Vision service.
It supports supervised learning with tagged images for LEGO object detection.
"""

import os
import sys
import time
from typing import List, Dict, Tuple
from dotenv import load_dotenv
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import (
    ImageFileCreateBatch,
    ImageFileCreateEntry,
    Region,
)
from msrest.authentication import ApiKeyCredentials


class CustomVisionTrainer:
    """Handles training of Azure Custom Vision object detection models"""

    def __init__(self):
        """Initialize the Custom Vision trainer with credentials from environment"""
        load_dotenv()
        
        self.training_endpoint = os.getenv("TRAINING_ENDPOINT")
        self.training_key = os.getenv("TRAINING_KEY")
        self.project_name = os.getenv("PROJECT_NAME", "lego-object-detection")
        self.publish_iteration_name = os.getenv("PUBLISH_ITERATION_NAME", "production")
        self.domain_type = os.getenv("DOMAIN_TYPE", "ObjectDetection")
        
        if not self.training_endpoint or not self.training_key:
            raise ValueError(
                "Missing required environment variables. "
                "Please set TRAINING_ENDPOINT and TRAINING_KEY"
            )
        
        # Initialize the Custom Vision training client
        credentials = ApiKeyCredentials(in_headers={"Training-key": self.training_key})
        self.trainer = CustomVisionTrainingClient(self.training_endpoint, credentials)
        self.project = None
        self.tags = {}
    
    def create_or_get_project(self) -> None:
        """Create a new project or get existing one"""
        print(f"Looking for project: {self.project_name}")
        
        # Check if project already exists
        for project in self.trainer.get_projects():
            if project.name == self.project_name:
                self.project = project
                print(f"Found existing project: {self.project_name} (ID: {self.project.id})")
                return
        
        # Create new project if it doesn't exist
        print(f"Creating new project: {self.project_name}")
        
        # Get the object detection domain
        obj_detection_domain = None
        for domain in self.trainer.get_domains():
            if domain.type == self.domain_type:
                obj_detection_domain = domain
                break
        
        if not obj_detection_domain:
            raise ValueError(f"Could not find {self.domain_type} domain")
        
        self.project = self.trainer.create_project(
            self.project_name,
            domain_id=obj_detection_domain.id
        )
        print(f"Created project: {self.project_name} (ID: {self.project.id})")
    
    def create_tags(self, tag_names: List[str]) -> None:
        """Create tags for the objects to detect"""
        print("\nCreating tags...")
        
        # Get existing tags
        existing_tags = self.trainer.get_tags(self.project.id)
        existing_tag_names = {tag.name: tag for tag in existing_tags}
        
        for tag_name in tag_names:
            if tag_name in existing_tag_names:
                self.tags[tag_name] = existing_tag_names[tag_name]
                print(f"  Using existing tag: {tag_name}")
            else:
                tag = self.trainer.create_tag(self.project.id, tag_name)
                self.tags[tag_name] = tag
                print(f"  Created new tag: {tag_name}")
    
    def upload_tagged_images(
        self, 
        images_with_tags: List[Dict[str, any]]
    ) -> None:
        """
        Upload images with bounding box tags to the project
        
        Args:
            images_with_tags: List of dicts with format:
                {
                    'path': 'path/to/image.jpg',
                    'regions': [
                        {
                            'tag': 'object_name',
                            'left': 0.1,    # normalized coordinates (0-1)
                            'top': 0.2,
                            'width': 0.3,
                            'height': 0.4
                        },
                        ...
                    ]
                }
        """
        print(f"\nUploading {len(images_with_tags)} images...")
        
        # Process images in batches (max 64 per batch)
        batch_size = 64
        for i in range(0, len(images_with_tags), batch_size):
            batch = images_with_tags[i:i + batch_size]
            image_list = []
            
            for img_data in batch:
                image_path = img_data['path']
                regions_data = img_data.get('regions', [])
                
                if not os.path.exists(image_path):
                    print(f"  Warning: Image not found: {image_path}")
                    continue
                
                # Create regions for this image
                regions = []
                for region_data in regions_data:
                    tag_name = region_data['tag']
                    if tag_name not in self.tags:
                        print(f"  Warning: Tag '{tag_name}' not found, skipping region")
                        continue
                    
                    region = Region(
                        tag_id=self.tags[tag_name].id,
                        left=region_data['left'],
                        top=region_data['top'],
                        width=region_data['width'],
                        height=region_data['height']
                    )
                    regions.append(region)
                
                # Read image file
                with open(image_path, 'rb') as image_file:
                    image_contents = image_file.read()
                
                # Create image entry
                image_entry = ImageFileCreateEntry(
                    name=os.path.basename(image_path),
                    contents=image_contents,
                    regions=regions
                )
                image_list.append(image_entry)
            
            # Upload the batch
            if image_list:
                upload_result = self.trainer.create_images_from_files(
                    self.project.id,
                    ImageFileCreateBatch(images=image_list)
                )
                
                if upload_result.is_batch_successful:
                    print(f"  Uploaded batch {i//batch_size + 1}: {len(image_list)} images")
                else:
                    print(f"  Batch upload had issues:")
                    for image in upload_result.images:
                        if image.status != "OK":
                            print(f"    {image.source_url}: {image.status}")
    
    def train_model(self) -> str:
        """Train the model with uploaded images"""
        print("\nStarting training...")
        
        # Start training
        iteration = self.trainer.train_project(self.project.id)
        
        # Wait for training to complete
        while iteration.status != "Completed":
            iteration = self.trainer.get_iteration(self.project.id, iteration.id)
            print(f"  Training status: {iteration.status}")
            time.sleep(10)
        
        print(f"Training completed! Iteration: {iteration.name}")
        return iteration.id
    
    def publish_model(self, iteration_id: str, prediction_resource_id: str = None) -> None:
        """
        Publish the trained model
        
        Args:
            iteration_id: ID of the trained iteration to publish
            prediction_resource_id: Azure resource ID for prediction 
                (if None, will use the training resource)
        """
        print(f"\nPublishing model as '{self.publish_iteration_name}'...")
        
        # If no prediction resource ID provided, get it from the project
        if not prediction_resource_id:
            # For simplicity, we'll skip publishing if no resource ID is provided
            # In production, you'd want to specify this
            print("  Note: prediction_resource_id not provided, using default")
            # Get the prediction resource ID from environment or project settings
            # This would typically come from your Azure Custom Vision resource
        
        try:
            # Use None as fallback instead of empty string for API compatibility
            resource_id = prediction_resource_id or os.getenv("PREDICTION_RESOURCE_ID")
            if not resource_id:
                resource_id = None
            
            self.trainer.publish_iteration(
                self.project.id,
                iteration_id,
                self.publish_iteration_name,
                resource_id
            )
            print("  Model published successfully!")
        except Exception as e:
            print(f"  Error publishing model: {e}")
            print("  You may need to publish manually from Azure Portal")
    
    def get_project_stats(self) -> Dict:
        """Get statistics about the current project"""
        if not self.project:
            return {}
        
        images = self.trainer.get_tagged_images(self.project.id)
        tags = self.trainer.get_tags(self.project.id)
        
        return {
            "project_name": self.project.name,
            "project_id": self.project.id,
            "total_images": len(images),
            "tags": [{"name": tag.name, "count": tag.image_count} for tag in tags]
        }


def create_sample_training_data() -> List[Dict]:
    """
    Create sample training data structure for demonstration
    
    Returns:
        List of image data with bounding boxes
    """
    # Example structure - in practice, you'd load this from a JSON file or database
    # Coordinates are normalized (0-1 range relative to image dimensions)
    
    sample_data = [
        {
            'path': '../testdata/test1.jpg',
            'regions': [
                {
                    'tag': 'lego_robot',
                    'left': 0.3,
                    'top': 0.4,
                    'width': 0.2,
                    'height': 0.3
                }
            ]
        }
    ]
    
    return sample_data


def main():
    """Main training pipeline"""
    print("=" * 60)
    print("Azure Custom Vision - Object Detection Training")
    print("=" * 60)
    
    try:
        # Initialize trainer
        trainer = CustomVisionTrainer()
        
        # Create or get project
        trainer.create_or_get_project()
        
        # Define tags for objects to detect
        # These should match your training data
        tag_names = [
            'lego_robot',
            'lego_brick',
            'lego_wheel',
            'lego_minifig'
        ]
        trainer.create_tags(tag_names)
        
        # Load training data
        # In production, you'd load this from a JSON file or database
        print("\nNote: Using sample training data structure")
        print("To use real training data, prepare images and annotations")
        print("See README.md for data format details")
        
        training_data = create_sample_training_data()
        
        # Upload images with tags
        # Uncomment the following line when you have real training data
        # trainer.upload_tagged_images(training_data)
        print("\nSkipping image upload in this demo")
        print("To upload images, uncomment the upload_tagged_images call")
        
        # Display project stats
        stats = trainer.get_project_stats()
        print("\n" + "=" * 60)
        print("Project Statistics:")
        print(f"  Project: {stats.get('project_name', 'N/A')}")
        print(f"  Total Images: {stats.get('total_images', 0)}")
        print("  Tags:")
        for tag in stats.get('tags', []):
            print(f"    - {tag['name']}: {tag['count']} images")
        
        # Train model (only if we have images)
        if stats.get('total_images', 0) > 0:
            iteration_id = trainer.train_model()
            
            # Publish model
            trainer.publish_model(iteration_id)
        else:
            print("\nNo images uploaded yet. Upload tagged images to train the model.")
        
        print("\n" + "=" * 60)
        print("Training pipeline completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
