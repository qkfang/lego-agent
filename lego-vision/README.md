# LEGO Vision - Azure Custom Vision Object Detection

Azure Custom Vision service integration for training custom object detection models to identify LEGO objects in images.

## Overview

This module provides a complete pipeline for:
- Creating and managing Azure Custom Vision projects
- Uploading and tagging training images with bounding boxes
- Training supervised object detection models
- Deploying trained models for inference
- Making predictions on new images

## Prerequisites

- **Azure Account** with Custom Vision service enabled
- **Python 3.8+**
- **Azure Custom Vision Resource** (both training and prediction keys)

## Setup

### 1. Create Azure Custom Vision Resource

1. Go to [Azure Portal](https://portal.azure.com)
2. Create a new **Custom Vision** resource
3. Choose **Both** for training and prediction, or create separate resources
4. Note down:
   - Training endpoint and key
   - Prediction endpoint and key
   - Prediction resource ID (for publishing)

### 2. Install Dependencies

```bash
cd lego-vision
pip install -r requirements.txt
```

### 3. Configure Environment

Copy the environment template and fill in your credentials:

```bash
cp .env.template .env
```

Edit `.env` and add your Azure Custom Vision credentials:

```env
TRAINING_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com/
TRAINING_KEY=your-training-key-here
PREDICTION_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com/
PREDICTION_KEY=your-prediction-key-here
PROJECT_NAME=lego-object-detection
PUBLISH_ITERATION_NAME=production
```

## Usage

### Step 1: Prepare Training Data

The training process requires images with bounding box annotations. Each image needs:
- Image file (JPG, PNG, or BMP)
- Bounding box coordinates (normalized 0-1 range)
- Tag/label for each bounding box

#### Create Annotation Template

Generate an annotation template from your images:

```bash
python prepare_data.py --data-dir ../testdata --create-template
```

This creates `annotations.json` with entries for each image found in the directory.

#### Edit Annotations

Open `../testdata/annotations.json` and add bounding box coordinates:

```json
{
  "images": [
    {
      "path": "test1.jpg",
      "width": 1920,
      "height": 1080,
      "regions": [
        {
          "tag": "lego_robot",
          "left": 0.3,
          "top": 0.4,
          "width": 0.2,
          "height": 0.3
        },
        {
          "tag": "lego_brick",
          "left": 0.6,
          "top": 0.2,
          "width": 0.15,
          "height": 0.15
        }
      ]
    }
  ],
  "tags": [
    "lego_robot",
    "lego_brick",
    "lego_wheel",
    "lego_minifig"
  ]
}
```

**Coordinate System:**
- All coordinates are normalized (0.0 to 1.0)
- `left`: X position of top-left corner (0 = left edge, 1 = right edge)
- `top`: Y position of top-left corner (0 = top edge, 1 = bottom edge)
- `width`: Width of bounding box (relative to image width)
- `height`: Height of bounding box (relative to image height)

#### Validate Annotations

Check your annotations are correctly formatted:

```bash
python prepare_data.py --data-dir ../testdata --validate
```

### Step 2: Train the Model

Once you have prepared and validated your training data:

#### Update train.py

Modify `train.py` to load your annotations:

```python
# In train.py main() function, replace:
training_data = create_sample_training_data()

# With:
from prepare_data import TrainingDataManager
manager = TrainingDataManager('../testdata')
training_data = manager.prepare_training_data()
```

#### Run Training

```bash
python train.py
```

The training script will:
1. Create or connect to your Custom Vision project
2. Create tags for object categories
3. Upload images with bounding box annotations
4. Train the object detection model
5. Publish the trained model

**Note:** Training typically takes 10-30 minutes depending on the number of images.

### Step 3: Make Predictions

After training and publishing your model, you can make predictions on new images.

#### Update .env for Predictions

Add your project ID to `.env`:

```env
PROJECT_ID=your-project-id-here
```

You can find the project ID in the Azure Custom Vision portal or from the training script output.

#### Run Predictions

```bash
# Basic prediction
python predict.py ../testdata/test1.jpg

# With custom threshold
python predict.py ../testdata/test1.jpg --threshold 0.7

# With visualization
python predict.py ../testdata/test1.jpg --visualize --output result.jpg
```

The prediction script will:
1. Load the published model
2. Analyze the image
3. Return detected objects with confidence scores
4. Optionally create a visualization with bounding boxes

## File Structure

```
lego-vision/
├── train.py              # Main training script
├── prepare_data.py       # Data preparation and annotation tools
├── predict.py            # Prediction and deployment script
├── requirements.txt      # Python dependencies
├── .env.template         # Environment variable template
├── .env                  # Your credentials (gitignored)
└── README.md            # This file
```

## Training Data Format

### Annotations JSON Structure

```json
{
  "images": [
    {
      "path": "relative/path/to/image.jpg",
      "width": 1920,
      "height": 1080,
      "regions": [
        {
          "tag": "object_name",
          "left": 0.0,     // 0.0 to 1.0
          "top": 0.0,      // 0.0 to 1.0
          "width": 0.0,    // 0.0 to 1.0
          "height": 0.0    // 0.0 to 1.0
        }
      ]
    }
  ],
  "tags": [
    "object_category_1",
    "object_category_2"
  ],
  "description": "Training annotations for Custom Vision"
}
```

### Recommended Dataset Size

For good model performance:
- **Minimum:** 15 images per tag, 30 tagged regions per tag
- **Recommended:** 50+ images per tag, 100+ tagged regions per tag
- **Maximum:** Azure Custom Vision supports up to 100,000 images per project

## Tips for Best Results

1. **Diverse Images:** Use images with varied:
   - Lighting conditions
   - Angles and perspectives
   - Backgrounds
   - Object positions and sizes

2. **Accurate Annotations:** 
   - Draw tight bounding boxes around objects
   - Include all visible instances of objects
   - Be consistent with tag names

3. **Balanced Dataset:**
   - Try to have similar numbers of examples for each tag
   - Include both easy and challenging examples

4. **Iterative Improvement:**
   - Start with a small dataset and train a baseline model
   - Test predictions on new images
   - Add more training data for objects that are detected poorly
   - Retrain with the expanded dataset

## Troubleshooting

### "Training endpoint not set"
- Ensure `.env` file exists and has correct credentials
- Check that environment variables are properly formatted

### "No images uploaded yet"
- Verify your annotations.json file has image entries
- Check that image paths are correct (relative to data directory)
- Ensure regions are properly defined with bounding boxes

### "Training failed"
- Check Azure Custom Vision quotas (free tier has limits)
- Ensure you have at least 15 images per tag
- Verify all images are in supported formats (JPG, PNG, BMP)

### Low prediction accuracy
- Add more diverse training images
- Review and correct annotation errors
- Ensure bounding boxes are accurate and tight
- Add more examples of objects that are poorly detected

## API Reference

### CustomVisionTrainer

Main class for training models.

**Methods:**
- `create_or_get_project()`: Create or connect to project
- `create_tags(tag_names)`: Create object category tags
- `upload_tagged_images(images_with_tags)`: Upload annotated images
- `train_model()`: Train the model
- `publish_model(iteration_id)`: Deploy the trained model

### CustomVisionPredictor

Main class for making predictions.

**Methods:**
- `predict_image_file(image_path, threshold)`: Predict from local image
- `predict_image_url(image_url, threshold)`: Predict from URL
- `visualize_detections(image_path, detections)`: Create visualization

### TrainingDataManager

Helper class for data preparation.

**Methods:**
- `scan_images()`: Find images in directory
- `create_annotation_template(image_paths)`: Generate template
- `load_annotations()`: Load annotations from JSON
- `prepare_training_data()`: Convert to training format
- `validate_annotations()`: Check annotation validity

## Additional Resources

- [Azure Custom Vision Documentation](https://docs.microsoft.com/azure/cognitive-services/custom-vision-service/)
- [Custom Vision Python SDK](https://docs.microsoft.com/python/api/overview/azure/cognitiveservices/customvision)
- [Training Tips and Best Practices](https://docs.microsoft.com/azure/cognitive-services/custom-vision-service/getting-started-improving-your-classifier)

## License

This module is part of the LEGO Agent project and follows the same license.

## Support

For issues or questions:
1. Check this README and Azure documentation
2. Review example code in the scripts
3. Open an issue in the main repository
