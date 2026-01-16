"""
LEGO Vision - Azure Custom Vision Object Detection Module

This module provides integration with Azure Custom Vision service for
training and deploying custom object detection models for LEGO objects.
"""

from .train import CustomVisionTrainer
from .predict import CustomVisionPredictor
from .prepare_data import TrainingDataManager

__version__ = "1.0.0"
__all__ = [
    "CustomVisionTrainer",
    "CustomVisionPredictor", 
    "TrainingDataManager"
]
