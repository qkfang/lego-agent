"""
Example usage of the Content Understanding Video Agent
"""

import asyncio
import os
from agent_cu import ContentUnderstandingVideoAgent
from dotenv import load_dotenv

load_dotenv()


async def example_basic_analysis():
    """Basic example: Analyze a video and get results"""
    print("=" * 80)
    print("Example 1: Basic Video Analysis")
    print("=" * 80)
    
    agent = ContentUnderstandingVideoAgent()
    await agent.init()
    
    # Replace with your actual video URL
    video_url = os.environ.get("TEST_VIDEO_URL", "https://example.com/sample-video.mp4")
    
    print(f"\nAnalyzing video: {video_url}")
    print("This may take a few minutes...\n")
    
    try:
        result = await agent.analyze_video_from_url(video_url)
        
        print("Analysis Results:")
        print("-" * 80)
        print(f"Status: {result['status']}")
        print(f"\nTranscript length: {len(result['transcript'])} characters")
        print(f"Number of segments: {len(result['segments'])}")
        print(f"Number of key frames: {len(result['key_frames'])}")
        print(f"\nSummary: {result['summary']}")
        
        if result['transcript']:
            print(f"\nTranscript (first 500 chars):")
            print(result['transcript'][:500])
            print("...\n")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        await agent.close()


async def example_query_analysis():
    """Example: Ask specific questions about a video"""
    print("=" * 80)
    print("Example 2: Query-Based Video Analysis")
    print("=" * 80)
    
    agent = ContentUnderstandingVideoAgent()
    await agent.init()
    
    video_url = os.environ.get("TEST_VIDEO_URL", "https://example.com/sample-video.mp4")
    query = "What are the main topics discussed in this video? Provide a detailed summary."
    
    print(f"\nVideo URL: {video_url}")
    print(f"Query: {query}\n")
    
    try:
        result = await agent.execute(query, video_url)
        print("Response:")
        print("-" * 80)
        print(result)
        print()
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        await agent.close()


async def example_multiple_videos():
    """Example: Analyze multiple videos"""
    print("=" * 80)
    print("Example 3: Multiple Video Analysis")
    print("=" * 80)
    
    agent = ContentUnderstandingVideoAgent()
    await agent.init()
    
    # Replace with your actual video URLs
    video_urls = [
        os.environ.get("TEST_VIDEO_URL_1", "https://example.com/video1.mp4"),
        os.environ.get("TEST_VIDEO_URL_2", "https://example.com/video2.mp4"),
    ]
    
    results = []
    
    for i, video_url in enumerate(video_urls, 1):
        print(f"\nAnalyzing video {i}/{len(video_urls)}: {video_url}")
        try:
            result = await agent.analyze_video_from_url(video_url)
            results.append({
                "url": video_url,
                "result": result
            })
            print(f"✓ Video {i} analyzed successfully")
        except Exception as e:
            print(f"✗ Error analyzing video {i}: {str(e)}")
    
    print("\n" + "=" * 80)
    print("Summary of All Videos")
    print("=" * 80)
    
    for i, item in enumerate(results, 1):
        print(f"\nVideo {i}: {item['url']}")
        print(f"  Segments: {len(item['result']['segments'])}")
        print(f"  Key Frames: {len(item['result']['key_frames'])}")
        print(f"  Transcript length: {len(item['result']['transcript'])} characters")
    
    await agent.close()


async def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("Content Understanding Video Agent Examples")
    print("=" * 80 + "\n")
    
    # Check required environment variables
    required_vars = [
        "PROJECT_CONNECTION_STRING",
        "CONTENT_UNDERSTANDING_ENDPOINT",
        "CONTENT_UNDERSTANDING_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        return
    
    # Run examples
    examples = [
        ("Basic Analysis", example_basic_analysis),
        ("Query-Based Analysis", example_query_analysis),
        ("Multiple Videos", example_multiple_videos),
    ]
    
    for name, example_func in examples:
        try:
            await example_func()
        except Exception as e:
            print(f"Error in {name}: {str(e)}")
        
        print("\n" + "-" * 80 + "\n")
        
        # Wait a bit between examples
        await asyncio.sleep(2)
    
    print("=" * 80)
    print("All examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
