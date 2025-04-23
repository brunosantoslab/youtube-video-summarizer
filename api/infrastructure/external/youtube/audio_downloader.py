# api/infrastructure/external/youtube/audio_downloader.py
import logging
import subprocess
import tempfile
import os
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class YouTubeAudioDownloader:
    """Service for downloading audio from YouTube videos using yt-dlp"""
    
    def __init__(self, yt_dlp_path: Optional[str] = None):
        self.yt_dlp_path = yt_dlp_path or "yt-dlp"
    
    def download_audio(self, video_id: str) -> Tuple[bytes, str]:
        """
        Download audio from a YouTube video
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Tuple of (audio_data, file_extension)
        """
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, "audio")
        
        try:
            # Construct the YouTube URL
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Run yt-dlp to download audio
            cmd = [
                self.yt_dlp_path,
                "-f", "bestaudio",
                "-o", temp_file_path,
                "--extract-audio",
                "--audio-format", "mp3",
                "--audio-quality", "0",  # Best quality
                youtube_url
            ]
            
            logger.info(f"Downloading audio for video {video_id}")
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Get the output file path (yt-dlp adds extension)
            output_file = f"{temp_file_path}.mp3"
            
            # Read the audio data
            with open(output_file, "rb") as f:
                audio_data = f.read()
            
            return audio_data, "mp3"
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error downloading audio for video {video_id}: {e.stderr.decode()}")
            raise
        except Exception as e:
            logger.error(f"Error processing audio for video {video_id}: {str(e)}")
            raise
        finally:
            # Clean up temporary files
            try:
                for file in os.listdir(temp_dir):
                    os.unlink(os.path.join(temp_dir, file))
                os.rmdir(temp_dir)
            except Exception as e:
                logger.warning(f"Error cleaning up temporary files: {str(e)}")