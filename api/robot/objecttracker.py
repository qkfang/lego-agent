#!/usr/bin/env python3
"""
Object Movement Tracking Script

This script tracks object movements across multiple images taken from the same location
and displays the movements in a virtual map.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import argparse
import math
import json
import os
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation

# Import the existing ObjectDetector
from robot.objectdetector import ObjectDetector, create_sample_color_ranges


class ObjectTracker:
    """
    A class for tracking object movements across multiple images.
    """
    
    def __init__(self, max_distance_threshold: float = 100.0):
        """
        Initialize the ObjectTracker.
        
        Args:
            max_distance_threshold (float): Maximum distance an object can move between frames
        """
        self.detector = ObjectDetector()
        self.max_distance_threshold = max_distance_threshold
        self.frames = []  # List of frame data
        self.tracked_objects = {}  # Dictionary of tracked objects by ID
        self.next_object_id = 1
        
    def process_image_sequence(self, image_paths: List[str], method: str = "color", 
                             **detector_kwargs) -> Dict[str, Any]:
        """
        Process a sequence of images to track object movements.
        
        Args:
            image_paths (List[str]): List of image file paths
            method (str): Detection method ("color", "template", "yolo")
            **detector_kwargs: Additional arguments for the detector
            
        Returns:
            Dict[str, Any]: Tracking analysis results
        """
        print(f"Processing {len(image_paths)} images for movement tracking...")
        
        # Process each image
        for frame_idx, image_path in enumerate(image_paths):
            print(f"\nProcessing frame {frame_idx + 1}/{len(image_paths)}: {image_path}")
            
            # Load and process the image
            success = self.detector.load_image(image_path)
            if not success:
                print(f"Failed to load image: {image_path}")
                continue
                
            # Detect objects in this frame
            if method == "color":
                color_ranges = detector_kwargs.get('color_ranges', create_sample_color_ranges())
                detected_objects = self.detector.detect_objects_by_color(
                    color_ranges, 
                    detector_kwargs.get('enable_preprocessing', True)
                )
            elif method == "yolo":
                target_objects = detector_kwargs.get('target_objects', None)
                confidence = detector_kwargs.get('confidence', 0.5)
                detected_objects = self.detector.detect_objects_by_yolo(confidence, target_objects)
            elif method == "template":
                templates = detector_kwargs.get('templates', [])
                threshold = detector_kwargs.get('threshold', 0.8)
                detected_objects = self.detector.detect_objects_by_template(templates, threshold)
            else:
                print(f"Unknown detection method: {method}")
                continue
            # Store frame data
            frame_data = {
                'frame_idx': frame_idx,
                'image_path': image_path,
                'detected_objects': detected_objects,
                'timestamp': frame_idx,  # Use frame index as timestamp for now
                'image_dimensions': (self.detector.image_width, self.detector.image_height)
            }
            self.frames.append(frame_data)
            
            # Track objects across frames
            if frame_idx == 0:
                # First frame - initialize all objects
                self._initialize_tracking(detected_objects, frame_idx)
            else:
                # Subsequent frames - match and update tracking
                self._update_tracking(detected_objects, frame_idx)
                
            print(f"  Detected {len(detected_objects)} objects")
        
        # Generate tracking analysis
        return self._generate_tracking_analysis()
    
    def _initialize_tracking(self, detected_objects: List[Dict], frame_idx: int):
        """Initialize tracking for the first frame."""
        for obj in detected_objects:
            track_id = self.next_object_id
            self.next_object_id += 1
            
            self.tracked_objects[track_id] = {
                'track_id': track_id,
                'object_type': obj['name'],
                'positions': [(frame_idx, obj['coordinates_2d'])],
                'first_seen': frame_idx,
                'last_seen': frame_idx,
                'total_distance': 0.0,
                'avg_speed': 0.0,
                'trajectory': [obj['coordinates_2d']]
            }
            
    def _update_tracking(self, detected_objects: List[Dict], frame_idx: int):
        """Update tracking for subsequent frames."""
        # Get current positions of tracked objects
        current_tracks = {}
        for track_id, track in self.tracked_objects.items():
            if track['last_seen'] == frame_idx - 1:  # Active in previous frame
                current_tracks[track_id] = track['positions'][-1][1]  # Last known position
        
        # Match detected objects to existing tracks
        matched_pairs = self._match_objects_to_tracks(detected_objects, current_tracks)
        
        # Update matched tracks
        for obj_idx, track_id in matched_pairs.items():
            obj = detected_objects[obj_idx]
            track = self.tracked_objects[track_id]
            
            # Calculate movement distance
            last_pos = track['positions'][-1][1]
            new_pos = obj['coordinates_2d']
            distance = math.sqrt((new_pos[0] - last_pos[0])**2 + (new_pos[1] - last_pos[1])**2)
            
            # Update track
            track['positions'].append((frame_idx, new_pos))
            track['trajectory'].append(new_pos)
            track['last_seen'] = frame_idx
            track['total_distance'] += distance
            
            # Calculate average speed (distance per frame)
            if len(track['positions']) > 1:
                total_frames = track['last_seen'] - track['first_seen']
                track['avg_speed'] = track['total_distance'] / total_frames if total_frames > 0 else 0.0
        
        # Create new tracks for unmatched objects
        unmatched_objects = [i for i in range(len(detected_objects)) if i not in matched_pairs]
        
        for obj_idx in unmatched_objects:
            obj = detected_objects[obj_idx]
            track_id = self.next_object_id
            self.next_object_id += 1
            
            self.tracked_objects[track_id] = {
                'track_id': track_id,
                'object_type': obj['name'],
                'positions': [(frame_idx, obj['coordinates_2d'])],
                'first_seen': frame_idx,
                'last_seen': frame_idx,
                'total_distance': 0.0,
                'avg_speed': 0.0,
                'trajectory': [obj['coordinates_2d']]
            }
    
    def _match_objects_to_tracks(self, detected_objects: List[Dict], 
                                current_tracks: Dict[int, Tuple[int, int]]) -> Dict[int, int]:
        """
        Match detected objects to existing tracks using loose color and distance criteria.
        
        Returns:
            Dict[int, int]: Mapping from object index to track ID
        """
        if not current_tracks or not detected_objects:
            return {}
        # Get color (object_type) for each track
        track_ids = list(current_tracks.keys())
        track_colors = {tid: self.tracked_objects[tid]['object_type'] for tid in track_ids}
        # Calculate distance matrix, but allow loose color match
        distance_matrix = []
        for obj_idx, obj in enumerate(detected_objects):
            obj_color = obj.get('name', None)
            obj_distances = []
            for track_idx, track_id in enumerate(track_ids):
                track_color = track_colors[track_id]
                # Loose color match: allow if either is None, or if color names are similar (case-insensitive, substring)
                color_match = False
                if obj_color is None or track_color is None:
                    color_match = True
                elif obj_color.lower() == track_color.lower():
                    color_match = True
                elif obj_color.lower() in track_color.lower() or track_color.lower() in obj_color.lower():
                    color_match = True
                else:
                    color_match = False
                if color_match:
                    track_pos = current_tracks[track_id]
                    obj_pos = obj['coordinates_2d']
                    distance = math.sqrt((obj_pos[0] - track_pos[0])**2 + (obj_pos[1] - track_pos[1])**2)
                else:
                    distance = float('inf')  # Do not allow cross-color matching
                obj_distances.append(distance)
            distance_matrix.append(obj_distances)
        # Simple greedy matching (could be improved with Hungarian algorithm)
        matched_pairs = {}
        used_tracks = set()
        # Sort object-track pairs by distance
        all_pairs = []
        # Make matching looser by increasing the allowed distance threshold
        loose_distance_threshold = self.max_distance_threshold * 1.5
        for obj_idx, distances in enumerate(distance_matrix):
            for track_idx, distance in enumerate(distances):
                # if distance <= loose_distance_threshold:
                    all_pairs.append((distance, obj_idx, track_ids[track_idx]))
        all_pairs.sort(key=lambda x: x[0])  # Sort by distance
        # Greedily assign matches
        for distance, obj_idx, track_id in all_pairs:
            if obj_idx not in matched_pairs and track_id not in used_tracks:
                matched_pairs[obj_idx] = track_id
                used_tracks.add(track_id)
        return matched_pairs
    
    def _generate_tracking_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive tracking analysis."""
        analysis = {
            'total_frames': len(self.frames),
            'tracking_summary': {
                'total_tracks': len(self.tracked_objects),
                'active_tracks': len([t for t in self.tracked_objects.values() 
                                    if t['last_seen'] == len(self.frames) - 1]),
                'completed_tracks': len([t for t in self.tracked_objects.values() 
                                       if t['last_seen'] < len(self.frames) - 1])
            },
            'frame_data': self.frames,
            'tracked_objects': [],
            'movement_statistics': {}
        }
        
        # Process each tracked object
        total_distance = 0
        max_distance = 0
        max_speed = 0
        
        for track in self.tracked_objects.values():
            track_data = {
                'track_id': track['track_id'],
                'object_type': track['object_type'],
                'duration_frames': track['last_seen'] - track['first_seen'] + 1,
                'total_distance_moved': track['total_distance'],
                'average_speed': track['avg_speed'],
                'trajectory': track['trajectory'],
                'first_position': track['positions'][0][1],
                'last_position': track['positions'][-1][1],
                'first_seen_frame': track['first_seen'],
                'last_seen_frame': track['last_seen']
            }
            
            analysis['tracked_objects'].append(track_data)
            
            # Update statistics
            total_distance += track['total_distance']
            max_distance = max(max_distance, track['total_distance'])
            max_speed = max(max_speed, track['avg_speed'])
        
        # Movement statistics
        analysis['movement_statistics'] = {
            'total_distance_all_objects': total_distance,
            'max_distance_single_object': max_distance,
            'max_speed_observed': max_speed,
            'average_objects_per_frame': sum(len(f['detected_objects']) for f in self.frames) / len(self.frames) if self.frames else 0
        }
        
        return analysis
    
    def visualize_movement_map(self, analysis: Dict[str, Any], save_path: str = None, 
                              show_plot: bool = True, create_animation: bool = False):
        """
        Create a virtual map visualization showing object movements.
        
        Args:
            analysis (Dict[str, Any]): Tracking analysis results
            save_path (str): Path to save the visualization
            show_plot (bool): Whether to display the plot
            create_animation (bool): Whether to create an animated visualization
        """
        if not self.frames:
            print("No frames to visualize")
            return
        
        # Get image dimensions from first frame
        img_width, img_height = self.frames[0]['image_dimensions']
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.set_xlim(0, img_width)
        ax.set_ylim(0, img_height)
        ax.set_aspect('equal')
        ax.invert_yaxis()  # Match image coordinate system
        
        # Color map for different tracks
        colors = plt.cm.tab10(np.linspace(0, 1, len(analysis['tracked_objects'])))
        
        # Plot each trajectory
        for i, track in enumerate(analysis['tracked_objects']):
            trajectory = track['trajectory']
            if len(trajectory) < 2:
                continue
                
            color = colors[i % len(colors)]
            
            # Extract x and y coordinates
            x_coords = [pos[0] for pos in trajectory]
            y_coords = [img_height - pos[1] for pos in trajectory]  # Convert to image coordinates
            
            # Plot trajectory line
            ax.plot(x_coords, y_coords, color=color, linewidth=2, alpha=0.7, 
                   label=f"Track {track['track_id']} ({track['object_type']})")
            
            # Mark start and end points
            ax.scatter(x_coords[0], y_coords[0], color=color, s=100, marker='o', 
                      edgecolors='black', linewidth=2, label=f"Start {track['track_id']}")
            ax.scatter(x_coords[-1], y_coords[-1], color=color, s=100, marker='s', 
                      edgecolors='black', linewidth=2, label=f"End {track['track_id']}")
            
            # Add direction arrows
            if len(trajectory) > 1:
                for j in range(0, len(x_coords)-1, max(1, len(x_coords)//5)):  # Add arrows every few points
                    dx = x_coords[j+1] - x_coords[j]
                    dy = y_coords[j+1] - y_coords[j]
                    if abs(dx) > 1 or abs(dy) > 1:  # Only draw arrow if movement is significant
                        ax.annotate('', xy=(x_coords[j+1], y_coords[j+1]), 
                                   xytext=(x_coords[j], y_coords[j]),
                                   arrowprops=dict(arrowstyle='->', color=color, alpha=0.6))
            
            # Add track information
            mid_x = sum(x_coords) / len(x_coords)
            mid_y = sum(y_coords) / len(y_coords)
            ax.text(mid_x, mid_y, f"ID:{track['track_id']}\nDist:{track['total_distance_moved']:.1f}", 
                   fontsize=8, ha='center', va='center', 
                   bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.3))
        
        # Customize the plot
        ax.set_title(f'Object Movement Tracking Map\n{len(analysis["tracked_objects"])} objects tracked across {analysis["total_frames"]} frames', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('X Coordinate (pixels)', fontsize=12)
        ax.set_ylabel('Y Coordinate (pixels)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Add legend (limit to avoid crowding)
        handles, labels = ax.get_legend_handles_labels()
        # Only show trajectory lines in legend
        trajectory_handles = handles[::3]  # Every 3rd handle (trajectory lines)
        trajectory_labels = [f"Track {track['track_id']} ({track['object_type']})" 
                           for track in analysis['tracked_objects']]
        ax.legend(trajectory_handles[:10], trajectory_labels[:10], 
                 loc='upper right', bbox_to_anchor=(1.15, 1))
        
        # Add statistics text
        stats_text = f"""Movement Statistics:
Total Distance: {analysis['movement_statistics']['total_distance_all_objects']:.1f} px
Max Single Distance: {analysis['movement_statistics']['max_distance_single_object']:.1f} px
Max Speed: {analysis['movement_statistics']['max_speed_observed']:.1f} px/frame
Avg Objects/Frame: {analysis['movement_statistics']['average_objects_per_frame']:.1f}"""
        
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray', alpha=0.8))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            print(f"Movement map saved to: {save_path}")
        
        if show_plot:
            plt.show()
    
    def export_tracking_data(self, analysis: Dict[str, Any], output_path: str):
        """Export tracking data to JSON file."""
        # Convert numpy arrays to lists for JSON serialization
        json_safe_analysis = self._make_json_serializable(analysis)
        
        with open(output_path, 'w') as f:
            json.dump(json_safe_analysis, f, indent=2)
        print(f"Tracking data exported to: {output_path}")
    
    def _make_json_serializable(self, obj):
        """Convert numpy arrays and other non-serializable objects to JSON-safe format."""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, tuple):
            return [self._make_json_serializable(item) for item in obj]
        else:
            return obj


def main():
    """Main function for the object tracking script."""
    parser = argparse.ArgumentParser(description='Track object movements across multiple images')
    parser.add_argument('images', nargs='+', help='Input image files (in chronological order)')
    parser.add_argument('--colors', nargs='+', default=None, help='List of color names to track (e.g. blue red green)')
    parser.add_argument('--method', choices=['color', 'template', 'yolo'], default='color',
                       help='Detection method to use')
    parser.add_argument('--output', help='Output JSON file for tracking data')
    parser.add_argument('--visualize', help='Save movement map visualization to file')
    parser.add_argument('--no-display', action='store_true', help='Do not display visualization')
    parser.add_argument('--max-distance', type=float, default=100.0,
                       help='Maximum distance an object can move between frames (pixels)')
    parser.add_argument('--pixels-per-unit', type=float, default=1.0,
                       help='Pixels per unit for distance measurements')
    # Detection method specific arguments
    parser.add_argument('--target-objects', nargs='*', 
                       help='For YOLO: Target object types to detect')
    parser.add_argument('--confidence', type=float, default=0.5,
                       help='For YOLO: Minimum confidence threshold')
    parser.add_argument('--templates', nargs='*',
                       help='For template matching: Template image files')
    parser.add_argument('--threshold', type=float, default=0.8,
                       help='For template matching: Matching threshold')
    parser.add_argument('--no-preprocessing', action='store_true',
                       help='For color detection: Disable noise reduction preprocessing')
    args = parser.parse_args()
    # Validate input files
    valid_images = []
    for img_path in args.images:
        if os.path.exists(img_path):
            valid_images.append(img_path)
        else:
            print(f"Warning: Image file not found: {img_path}")
    if len(valid_images) < 2:
        print("Error: At least 2 images are required for movement tracking")
        return 1
    print(f"Tracking objects across {len(valid_images)} images...")
    tracker = ObjectTracker(max_distance_threshold=args.max_distance)
    detector_kwargs = {
        'pixels_per_unit': args.pixels_per_unit
    }
    if args.method == 'yolo':
        detector_kwargs['target_objects'] = args.target_objects
        detector_kwargs['confidence'] = args.confidence
    elif args.method == 'template':
        detector_kwargs['templates'] = args.templates or []
        detector_kwargs['threshold'] = args.threshold
    elif args.method == 'color':
        detector_kwargs['enable_preprocessing'] = not args.no_preprocessing
        # Filter color ranges if --colors is specified
        all_color_ranges = create_sample_color_ranges()
        if args.colors:
            color_ranges = [cr for cr in all_color_ranges if cr['name'].lower() in [c.lower() for c in args.colors]]
            if not color_ranges:
                print(f"Warning: No matching color ranges found for: {args.colors}. Using all available colors.")
                color_ranges = all_color_ranges
        else:
            color_ranges = all_color_ranges
        detector_kwargs['color_ranges'] = color_ranges
    analysis = tracker.process_image_sequence(valid_images, args.method, **detector_kwargs)
    print(f"\n=== MOVEMENT TRACKING RESULTS ===")
    print(f"Total frames processed: {analysis['total_frames']}")
    print(f"Total objects tracked: {analysis['tracking_summary']['total_tracks']}")
    print(f"Active tracks (present in last frame): {analysis['tracking_summary']['active_tracks']}")
    print(f"Completed tracks: {analysis['tracking_summary']['completed_tracks']}")
    print(f"\nTracked Objects:")
    for track in analysis['tracked_objects']:
        print(f"  Track {track['track_id']} ({track['object_type']}):")
        print(f"    Duration: {track['duration_frames']} frames")
        print(f"    Distance moved: {track['total_distance_moved']:.2f} pixels")
        print(f"    Average speed: {track['average_speed']:.2f} pixels/frame")
        print(f"    Start position: {track['first_position']}")
        print(f"    End position: {track['last_position']}")
    print(f"\nMovement Statistics:")
    stats = analysis['movement_statistics']
    print(f"  Total distance (all objects): {stats['total_distance_all_objects']:.2f} pixels")
    print(f"  Maximum distance (single object): {stats['max_distance_single_object']:.2f} pixels")
    print(f"  Maximum speed observed: {stats['max_speed_observed']:.2f} pixels/frame")
    print(f"  Average objects per frame: {stats['average_objects_per_frame']:.2f}")
    if args.output:
        tracker.export_tracking_data(analysis, args.output)
    if len(analysis['tracked_objects']) > 0:
        tracker.visualize_movement_map(analysis, args.visualize, not args.no_display)
    else:
        print("No objects tracked - skipping visualization")
    return 0


if __name__ == "__main__":
    exit(main())