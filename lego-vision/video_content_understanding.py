"""
Azure Content Understanding - Video Analysis
Analyzes video files using Azure AI Content Understanding service.
Extracts key frames, transcripts, descriptions, and custom fields.
"""

import os
import json
import base64
import mimetypes
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

load_dotenv()

from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import AnalyzeInput, AnalyzeResult
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# API version for REST calls
API_VERSION = "2025-11-01"


def get_client() -> ContentUnderstandingClient:
    """Create and return a Content Understanding client."""
    endpoint = os.environ.get("CONTENTUNDERSTANDING_ENDPOINT")
    if not endpoint:
        raise ValueError("CONTENTUNDERSTANDING_ENDPOINT environment variable is required")
    
    # Try API key first, fall back to DefaultAzureCredential
    api_key = os.environ.get("CONTENTUNDERSTANDING_KEY")
    if api_key:
        credential = AzureKeyCredential(api_key)
    else:
        credential = DefaultAzureCredential()
    
    return ContentUnderstandingClient(endpoint=endpoint, credential=credential)


def get_auth_headers() -> dict:
    """Get authentication headers for REST API calls."""
    api_key = os.environ.get("CONTENTUNDERSTANDING_KEY")
    if api_key:
        return {"Ocp-Apim-Subscription-Key": api_key}
    else:
        credential = DefaultAzureCredential()
        token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")
        token = token_provider()
        return {"Authorization": f"Bearer {token}"}


def analyze_video_from_url(video_url: str, analyzer_id: str = "prebuilt-videoSearch") -> dict:
    """
    Analyze a video from a URL using Azure Content Understanding.
    
    Args:
        video_url: URL of the video to analyze
        analyzer_id: The analyzer to use (default: prebuilt-videoAnalysis)
    
    Returns:
        dict: Analysis result containing key frames, transcript, descriptions, etc.
    """
    client = get_client()
    
    print(f"Starting video analysis...")
    print(f"Video URL: {video_url}")
    print(f"Analyzer: {analyzer_id}")
    
    # Start the analysis
    poller = client.begin_analyze(
        analyzer_id=analyzer_id,
        inputs=[AnalyzeInput(url=video_url)]
    )
    
    # Poll until complete
    print("Waiting for analysis to complete...")
    result: AnalyzeResult = poller.result()
    
    return result.as_dict()


def analyze_video_from_file(file_path: str, analyzer_id: str = "prebuilt-videoSearch") -> tuple[dict, str]:
    """
    Analyze a local video file using Azure Content Understanding REST API.
    Uses binary upload endpoint for efficient file transfer.
    
    Args:
        file_path: Path to the local video file
        analyzer_id: The analyzer to use (default: prebuilt-videoSearch)
    
    Returns:
        tuple: (Analysis result dict, Operation URL for downloading files)
    """
    endpoint = os.environ.get("CONTENTUNDERSTANDING_ENDPOINT")
    if not endpoint:
        raise ValueError("CONTENTUNDERSTANDING_ENDPOINT environment variable is required")
    
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Video file not found: {file_path}")
    
    print(f"Starting video analysis...")
    print(f"File: {file_path}")
    print(f"Analyzer: {analyzer_id}")
    
    with open(file_path, "rb") as f:
        file_content = f.read()
    
    file_size_mb = len(file_content) / (1024 * 1024)
    print(f"File size: {file_size_mb:.2f} MB")
    
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if not mime_type:
        mime_type = "video/mp4"
    
    # Note: enableSegment and returnDetails are analyzer config options, not query parameters
    # For prebuilt analyzers, these are pre-configured. To customize, create a custom analyzer.
    url = f"{endpoint.rstrip('/')}/contentunderstanding/analyzers/{analyzer_id}:analyzeBinary?api-version={API_VERSION}"
    
    headers = get_auth_headers()
    headers["Content-Type"] = mime_type
    
    print("Uploading and starting analysis...")
    response = requests.post(url, headers=headers, data=file_content)
    
    if response.status_code == 202:
        operation_location = response.headers.get("Operation-Location")
        if operation_location:
            result = poll_operation(operation_location)
            return result, operation_location
    
    if not response.ok:
        print(f"Error {response.status_code}: {response.text}")
    response.raise_for_status()
    return response.json(), ""


def poll_operation(operation_url: str, poll_interval: int = 5, max_wait: int = 600) -> dict:
    """
    Poll a long-running operation until complete.
    
    Args:
        operation_url: The Operation-Location URL to poll
        poll_interval: Seconds between polls (default: 5)
        max_wait: Maximum seconds to wait (default: 600)
    
    Returns:
        dict: The final operation result
    """
    import time
    
    headers = get_auth_headers()
    elapsed = 0
    
    while elapsed < max_wait:
        response = requests.get(operation_url, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        status = result.get("status", "").lower()
        
        if status == "succeeded":
            print("Analysis complete!")
            return result
        elif status in ("failed", "canceled"):
            error = result.get("error", {})
            raise Exception(f"Operation {status}: {error.get('message', 'Unknown error')}")
        
        print(f"Status: {status}... waiting {poll_interval}s")
        time.sleep(poll_interval)
        elapsed += poll_interval
    
    raise TimeoutError(f"Operation timed out after {max_wait} seconds")


def save_keyframe_image_to_file(
    image_content: bytes,
    keyframe_id: str,
    test_name: str,
    output_dir: str = "output",
    identifier: Optional[str] = None,
) -> str:
    """Save keyframe image to output file.

    Args:
        image_content: The binary image content to save
        keyframe_id: The keyframe ID (e.g., "keyframes/733")
        test_name: Name prefix for the output file
        output_dir: Directory to save the output file (default: "output")
        identifier: Optional unique identifier to avoid conflicts

    Returns:
        str: Path to the saved image file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    frame_id = keyframe_id.split("/")[-1] if "/" in keyframe_id else keyframe_id

    output_dir_path = Path(__file__).parent / output_dir
    output_dir_path.mkdir(parents=True, exist_ok=True)

    if identifier:
        output_filename = f"{test_name}_{identifier}_{timestamp}_{frame_id}.jpg"
    else:
        output_filename = f"{test_name}_{timestamp}_{frame_id}.jpg"

    saved_file_path = output_dir_path / output_filename

    with open(saved_file_path, "wb") as image_file:
        image_file.write(image_content)

    print(f"Image file saved to: {saved_file_path}")
    return str(saved_file_path)


def extract_keyframe_ids(result: Dict[str, Any]) -> List[str]:
    """Extract all keyframe IDs from the analysis result.

    Args:
        result: The analysis result from the analyzer

    Returns:
        List of keyframe IDs (e.g., 'keyframes/1000', 'keyframes/2000')
    """
    keyframe_ids = []
    contents = result.get("result", {}).get("contents", []) or result.get("contents", [])
    
    for content in contents:
        key_frame_times_ms = content.get("keyFrameTimesMs") or content.get("KeyFrameTimesMs", [])
        if key_frame_times_ms:
            for time_ms in key_frame_times_ms:
                keyframe_ids.append(f"keyframes/{time_ms}")
    
    return keyframe_ids


def get_result_file(operation_url: str, file_id: str) -> Optional[bytes]:
    """Download a result file (e.g., keyframe image) from the analysis result.

    Args:
        operation_url: The Operation-Location URL from the analysis
        file_id: The file ID to download (e.g., "keyframes/733")

    Returns:
        bytes: The file content, or None if download failed
    """
    base_url = operation_url.split("?")[0]
    file_url = f"{base_url}/files/{file_id}?api-version={API_VERSION}"
    
    headers = get_auth_headers()
    response = requests.get(file_url, headers=headers)
    
    if response.ok:
        return response.content
    else:
        print(f"Failed to download {file_id}: {response.status_code} - {response.text}")
        return None


def download_keyframes(result: Dict[str, Any], operation_url: str, max_frames: int = 25, identifier: str = None) -> List[str]:
    """Download keyframe images from the analysis result.

    Args:
        result: The analysis result dictionary
        operation_url: The Operation-Location URL from the analysis
        max_frames: Maximum number of frames to download (default: 5)
        identifier: Optional identifier for output filenames

    Returns:
        List of paths to saved keyframe images
    """
    keyframe_ids = extract_keyframe_ids(result)
    saved_paths = []
    
    if not keyframe_ids:
        print("No keyframe IDs found in analysis result.")
        return saved_paths
    
    print(f"\n🖼️ Downloading {min(len(keyframe_ids), max_frames)} of {len(keyframe_ids)} keyframe images...")
    
    for keyframe_id in keyframe_ids[:max_frames]:
        print(f"Getting result file: {keyframe_id}")
        image_content = get_result_file(operation_url, keyframe_id)
        
        if image_content:
            saved_path = save_keyframe_image_to_file(
                image_content=image_content,
                keyframe_id=keyframe_id,
                test_name="video_keyframe",
                identifier=identifier
            )
            saved_paths.append(saved_path)
            print(f"✅ Saved keyframe image to: {saved_path}")
        else:
            print(f"❌ No image content retrieved for keyframe: {keyframe_id}")
    
    return saved_paths


def print_video_analysis(result: dict) -> None:
    """Print formatted video analysis results."""
    print("\n" + "=" * 60)
    print("VIDEO ANALYSIS RESULTS")
    print("=" * 60)
    
    contents = result.get("contents", [])
    
    for i, content in enumerate(contents):
        print(f"\n--- Segment {i + 1} ---")
        
        # Timing info
        start_ms = content.get("startTimeMs", 0)
        end_ms = content.get("endTimeMs", 0)
        print(f"Duration: {start_ms}ms - {end_ms}ms ({(end_ms - start_ms) / 1000:.2f}s)")
        
        # Video dimensions
        width = content.get("width")
        height = content.get("height")
        if width and height:
            print(f"Resolution: {width}x{height}")
        
        # Key frames
        key_frames = content.get("keyFrameTimesMs", [])
        if key_frames:
            print(f"\nKey Frames ({len(key_frames)} extracted):")
            for j, frame_ms in enumerate(key_frames[:10]):  # Show first 10
                print(f"  - Frame {j + 1}: {frame_ms}ms ({frame_ms / 1000:.2f}s)")
            if len(key_frames) > 10:
                print(f"  ... and {len(key_frames) - 10} more")
        
        # Camera shots
        camera_shots = content.get("cameraShotTimesMs", [])
        if camera_shots:
            print(f"\nCamera Shots ({len(camera_shots)} detected):")
            for j, shot_ms in enumerate(camera_shots[:10]):
                print(f"  - Shot {j + 1}: {shot_ms}ms")
            if len(camera_shots) > 10:
                print(f"  ... and {len(camera_shots) - 10} more")
        
        # Transcript
        transcript_phrases = content.get("transcriptPhrases", [])
        if transcript_phrases:
            print(f"\nTranscript ({len(transcript_phrases)} phrases):")
            for phrase in transcript_phrases[:5]:  # Show first 5
                text = phrase.get("text", "")
                speaker = phrase.get("speaker", "Unknown")
                start = phrase.get("startTimeMs", 0)
                print(f"  [{start}ms] {speaker}: {text}")
            if len(transcript_phrases) > 5:
                print(f"  ... and {len(transcript_phrases) - 5} more phrases")
        
        # Custom fields
        fields = content.get("fields", {})
        if fields:
            print("\nExtracted Fields:")
            for field_name, field_data in fields.items():
                value = field_data.get("valueString") or field_data.get("value", "N/A")
                print(f"  {field_name}: {value}")
        
        # Markdown content
        markdown = content.get("markdown", "")
        if markdown:
            print(f"\nMarkdown Preview (first 500 chars):")
            print(markdown[:500])
            if len(markdown) > 500:
                print("...")
    
    print("\n" + "=" * 60)


def main():
    """Main function demonstrating video analysis."""
    import sys
    
    video_path = 'vid/lego-agent-move.mp4'
    analyzer_id = 'prebuilt-videoSearch'
    
    print(f"🔍 Analyzing local video: {video_path}")
    result, operation_url = analyze_video_from_file(video_path, analyzer_id)
    
    print_video_analysis(result)
    
    # Download keyframe images
    if operation_url:
        saved_keyframes = download_keyframes(
            result=result,
            operation_url=operation_url,
            max_frames=5,
            identifier=analyzer_id
        )
        if saved_keyframes:
            print(f"\n✅ Downloaded {len(saved_keyframes)} keyframe images")
    
    # Save full result to JSON
    output_path = Path(__file__).parent / "video_analysis_result.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n📋 Full result saved to: {output_path}")


if __name__ == "__main__":
    main()
