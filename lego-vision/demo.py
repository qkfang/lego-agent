#!/usr/bin/env python3
"""
Demo script showing the complete Azure Custom Vision workflow

This script demonstrates:
1. Data preparation and validation
2. Training pipeline setup
3. Model deployment concepts

Note: This is a demonstration script. You need to configure your Azure
credentials in .env before running the actual training.
"""

import os
import sys


def demo_data_preparation():
    """Demonstrate data preparation workflow"""
    print("=" * 70)
    print("STEP 1: DATA PREPARATION")
    print("=" * 70)
    print()
    
    print("The data preparation process involves:")
    print("1. Scanning for images in your training directory")
    print("2. Creating an annotation template")
    print("3. Adding bounding box coordinates for each object")
    print("4. Validating the annotations")
    print()
    
    print("Example commands:")
    print("  # Create annotation template")
    print("  python prepare_data.py --data-dir ../testdata --create-template")
    print()
    print("  # Validate annotations")
    print("  python prepare_data.py --data-dir ../testdata --validate")
    print()
    
    # Load and show existing annotations
    print("Current testdata annotations:")
    try:
        from prepare_data import TrainingDataManager
        manager = TrainingDataManager('../testdata')
        is_valid, errors = manager.validate_annotations()
        
        if is_valid:
            print("  ✓ Annotations are valid")
            annotations = manager.load_annotations()
            print(f"  ✓ {len(annotations.get('images', []))} images annotated")
            print(f"  ✓ {len(annotations.get('tags', []))} object categories defined")
        else:
            print("  ✗ Validation errors found:")
            for error in errors[:5]:  # Show first 5 errors
                print(f"    - {error}")
    except Exception as e:
        print(f"  Note: Could not load annotations - {e}")
    
    print()


def demo_training_pipeline():
    """Demonstrate training pipeline"""
    print("=" * 70)
    print("STEP 2: TRAINING PIPELINE")
    print("=" * 70)
    print()
    
    print("The training pipeline includes:")
    print("1. Creating or connecting to an Azure Custom Vision project")
    print("2. Creating tags for object categories")
    print("3. Uploading images with bounding box annotations")
    print("4. Training the object detection model")
    print("5. Publishing the trained model for predictions")
    print()
    
    print("Example workflow:")
    print("  # Set up Azure credentials in .env")
    print("  cp .env.template .env")
    print("  # Edit .env with your Azure Custom Vision credentials")
    print()
    print("  # Run training")
    print("  python train.py")
    print()
    
    print("Training considerations:")
    print("  - Minimum: 15 images per tag, 30 regions per tag")
    print("  - Recommended: 50+ images per tag for better accuracy")
    print("  - Training typically takes 10-30 minutes")
    print("  - Azure free tier has quotas and limitations")
    print()


def demo_prediction():
    """Demonstrate prediction workflow"""
    print("=" * 70)
    print("STEP 3: MODEL DEPLOYMENT & PREDICTION")
    print("=" * 70)
    print()
    
    print("After training, use the model for predictions:")
    print()
    print("Example commands:")
    print("  # Basic prediction")
    print("  python predict.py ../testdata/test1.jpg")
    print()
    print("  # With confidence threshold")
    print("  python predict.py ../testdata/test1.jpg --threshold 0.7")
    print()
    print("  # With visualization")
    print("  python predict.py ../testdata/test1.jpg --visualize --output result.jpg")
    print()
    
    print("Prediction output includes:")
    print("  - Detected object tags")
    print("  - Confidence scores (0-1)")
    print("  - Bounding box coordinates")
    print("  - Optional visualization with boxes drawn on image")
    print()


def demo_best_practices():
    """Show best practices"""
    print("=" * 70)
    print("BEST PRACTICES")
    print("=" * 70)
    print()
    
    print("For optimal results:")
    print()
    print("1. Dataset Quality:")
    print("   - Use diverse images (different angles, lighting, backgrounds)")
    print("   - Draw tight, accurate bounding boxes")
    print("   - Include all visible object instances")
    print()
    
    print("2. Annotation Consistency:")
    print("   - Use consistent tag names")
    print("   - Define clear object categories")
    print("   - Avoid overlapping categories")
    print()
    
    print("3. Iterative Improvement:")
    print("   - Start with a small dataset (baseline)")
    print("   - Test on new images")
    print("   - Add examples for poorly detected objects")
    print("   - Retrain with expanded dataset")
    print()
    
    print("4. Azure Resources:")
    print("   - Use F0 (free tier) for development/testing")
    print("   - Upgrade to S0 (standard) for production")
    print("   - Monitor quotas and usage")
    print()


def demo_file_structure():
    """Show the module structure"""
    print("=" * 70)
    print("MODULE STRUCTURE")
    print("=" * 70)
    print()
    
    print("lego-vision/")
    print("├── train.py              # Training pipeline script")
    print("├── prepare_data.py       # Data preparation tools")
    print("├── predict.py            # Prediction and inference")
    print("├── requirements.txt      # Python dependencies")
    print("├── .env.template         # Configuration template")
    print("├── .env                  # Your credentials (create this)")
    print("└── README.md             # Detailed documentation")
    print()
    print("See README.md for complete documentation and examples.")
    print()


def check_environment():
    """Check if environment is configured"""
    print("=" * 70)
    print("ENVIRONMENT CHECK")
    print("=" * 70)
    print()
    
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"✓ Found {env_file}")
        
        # Check for required variables
        from dotenv import dotenv_values
        config = dotenv_values(env_file)
        
        required_vars = ['TRAINING_ENDPOINT', 'TRAINING_KEY']
        all_set = True
        
        for var in required_vars:
            if config.get(var) and not config[var].startswith('your-'):
                print(f"  ✓ {var} is configured")
            else:
                print(f"  ✗ {var} needs to be set")
                all_set = False
        
        if all_set:
            print()
            print("✓ Environment is configured! You can run the training pipeline.")
        else:
            print()
            print("⚠ Please configure your Azure credentials in .env")
    else:
        print(f"✗ {env_file} not found")
        print()
        print("To get started:")
        print(f"  cp .env.template .env")
        print(f"  # Edit .env with your Azure Custom Vision credentials")
    
    print()


def main():
    """Run the demo"""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Azure Custom Vision - LEGO Object Detection Demo".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    demo_file_structure()
    check_environment()
    demo_data_preparation()
    demo_training_pipeline()
    demo_prediction()
    demo_best_practices()
    
    print("=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print()
    print("1. Configure Azure credentials:")
    print("   cp .env.template .env")
    print("   # Edit .env with your credentials")
    print()
    print("2. Prepare training data:")
    print("   python prepare_data.py --data-dir ../testdata --create-template")
    print("   # Edit annotations.json with bounding boxes")
    print("   python prepare_data.py --data-dir ../testdata --validate")
    print()
    print("3. Train the model:")
    print("   python train.py")
    print()
    print("4. Make predictions:")
    print("   python predict.py ../testdata/test1.jpg --visualize")
    print()
    print("For detailed documentation, see README.md")
    print()


if __name__ == "__main__":
    main()
