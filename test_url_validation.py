import sys
sys.path.append('backend')

from app.services.youtube_service import YouTubeService
import asyncio

async def test_url_validation():
    yt = YouTubeService()
    url = 'https://youtu.be/U7tmd4Yh9Do?si=NXcearW5XABOqzcF'
    
    print(f"Testing URL: {url}")
    print(f"URL validation: {yt._is_valid_youtube_url(url)}")
    
    try:
        print("Getting video info...")
        info = await yt.get_video_info(url)
        print(f"Success! Title: {info.get('title')}")
        print(f"Duration: {info.get('duration')} seconds")
    except Exception as e:
        print(f"Error getting video info: {e}")

if __name__ == "__main__":
    asyncio.run(test_url_validation()) 