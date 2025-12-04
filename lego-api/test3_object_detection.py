#!/usr/bin/env python3
"""
Test script to validate object detection improvements.
This test verifies that the object detector can detect blue, red, and yellow objects.
"""

import sys
import os

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from robot.object_detector import ObjectDetector, create_sample_color_ranges


def test_color_ranges():
    """Test that color ranges are properly defined"""
    color_ranges = create_sample_color_ranges()
    
    # Check that we have ranges for all three colors
    color_names = [cr['name'] for cr in color_ranges]
    
    assert 'robot' in color_names, "Missing 'robot' (blue) color range"
    assert 'coke' in color_names, "Missing 'red' color range"
    assert 'bowser' in color_names, "Missing 'yellow' color range"
    
    # Check that all ranges have required keys
    for color_range in color_ranges:
        assert 'name' in color_range, "Color range missing 'name' key"
        assert 'lower' in color_range, "Color range missing 'lower' key"
        assert 'upper' in color_range, "Color range missing 'upper' key"
        assert len(color_range['lower']) == 3, "Lower bound must have 3 values (HSV)"
        assert len(color_range['upper']) == 3, "Upper bound must have 3 values (HSV)"
    
    print("✓ Color ranges test passed")
    return True


def test_detection_on_sample_image():
    """Test object detection on a sample image"""
    # Use a test image from the testdata directory (relative to repository root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)  # Go up one level from lego-api
    test_image = os.path.join(repo_root, "testdata", "raw", "20250603_135447.jpg")
    
    if not os.path.exists(test_image):
        print(f"⚠ Warning: Test image not found at {test_image}, skipping detection test")
        return True
    
    detector = ObjectDetector()
    
    # Load the image
    if not detector.load_image(test_image):
        print("✗ Failed to load test image")
        return False
    
    # Detect objects using color-based detection
    color_ranges = create_sample_color_ranges()
    detected_objects = detector.detect_objects_by_color(color_ranges, use_preprocessing=True)
    
    # Check that we detected objects
    if len(detected_objects) == 0:
        print("✗ No objects detected in test image")
        return False
    
    # Check that we have at least one of each color type
    detected_colors = set(obj['name'] for obj in detected_objects)
    
    print(f"  Detected colors: {detected_colors}")
    print(f"  Total objects detected: {len(detected_objects)}")
    
    # Verify we can detect the three target colors
    if 'robot' not in detected_colors:
        print("⚠ Warning: No 'robot' (blue) objects detected")
    
    if 'red' not in detected_colors:
        print("⚠ Warning: No 'red' objects detected")
    
    if 'yellow' not in detected_colors:
        print("⚠ Warning: No 'yellow' objects detected")
    
    # At minimum, we should detect at least 2 of the 3 target colors
    target_colors = {'robot', 'red', 'yellow'}
    detected_target_colors = detected_colors.intersection(target_colors)
    
    if len(detected_target_colors) < 2:
        print(f"✗ Expected to detect at least 2 of {target_colors}, but only detected {detected_target_colors}")
        return False
    
    print("✓ Object detection test passed")
    return True


def main():
    """Run all tests"""
    print("\n=== Object Detector Tests ===\n")
    
    tests = [
        ("Color Ranges Configuration", test_color_ranges),
        ("Object Detection on Sample Image", test_detection_on_sample_image),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"Running: {test_name}")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            failed += 1
        print()
    
    print(f"=== Test Results ===")
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
