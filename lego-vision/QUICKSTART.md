# Quick Start Guide - Azure Custom Vision for LEGO Object Detection

## Prerequisites
1. Azure account with Custom Vision service
2. Training and prediction endpoints/keys

## Setup (5 minutes)

```bash
# 1. Install dependencies
cd lego-vision
pip install -r requirements.txt

# 2. Configure Azure credentials
cp .env.template .env
# Edit .env with your Azure Custom Vision credentials

# 3. Verify setup
python demo.py
```

## Training Workflow

### Step 1: Prepare Data
```bash
# Create annotation template from images
python prepare_data.py --data-dir ../testdata --create-template

# Edit ../testdata/annotations.json with bounding boxes
# Format: {"images": [...], "tags": [...]}

# Validate annotations
python prepare_data.py --data-dir ../testdata --validate
```

### Step 2: Train Model
```bash
# Run training pipeline
python train.py

# This will:
# - Create/connect to project
# - Upload tagged images
# - Train the model (10-30 min)
# - Publish for predictions
```

### Step 3: Make Predictions
```bash
# Basic prediction
python predict.py ../testdata/test1.jpg

# With visualization
python predict.py ../testdata/test1.jpg --visualize

# With custom threshold
python predict.py ../testdata/test1.jpg --threshold 0.7
```

## Annotation Format

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
          "left": 0.35,     // 0.0-1.0 (x position)
          "top": 0.4,       // 0.0-1.0 (y position)
          "width": 0.25,    // 0.0-1.0 (box width)
          "height": 0.35    // 0.0-1.0 (box height)
        }
      ]
    }
  ],
  "tags": ["lego_robot", "lego_brick", "lego_wheel"]
}
```

## Tips for Best Results

1. **Dataset Size**: 50+ images per tag recommended
2. **Diverse Images**: Vary angles, lighting, backgrounds
3. **Accurate Boxes**: Draw tight bounding boxes
4. **Iterative Training**: Start small, test, expand, retrain

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Missing environment variables" | Configure .env file |
| "No images uploaded" | Check annotations.json format |
| Low accuracy | Add more diverse training images |
| Training fails | Check Azure quotas (free tier limits) |

## Files Overview

- `train.py` - Training pipeline
- `prepare_data.py` - Data preparation tools
- `predict.py` - Make predictions
- `demo.py` - Interactive demo
- `README.md` - Full documentation

## Support

See README.md for complete documentation and examples.
