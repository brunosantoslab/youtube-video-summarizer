# api/infrastructure/external/ai/whisper_client.py
import logging
import os
import tempfile
from typing import Optional, List, Dict, Any
import time
import uuid

import httpx
from httpx import Response

from domain.models.transcript import TranscriptSegment
from config import get_settings

logger = logging.getLogger(__name__)


class WhisperApiClient:
    """Client for OpenAI's Whisper API for audio transcription"""
    
    API_URL = "https://api.openai.com/v1/audio/transcriptions"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_settings().openai_api_key
    
    async def transcribe_audio(
        self,
        audio_data: bytes,
        filename: str = "audio.mp3",
        language: str = "en",
        timestamp_granularities: List[str] = ["segment"]
    ) -> Dict[str, Any]:
        """
        Transcribe audio data using Whisper API
        
        Args:
            audio_data: Raw audio bytes
            filename: Name for the temporary file
            language: Language code (e.g., 'en', 'es')
            timestamp_granularities: Timestamp detail level ('segment' or 'word')
            
        Returns:
            Dictionary with transcription results
        """
        try:
            start_time = time.time()
            
            # Write audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
                temp_file_path = temp_file.name
                temp_file.write(audio_data)
            
            # Prepare request data
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Use httpx.AsyncClient for the request
            async with httpx.AsyncClient(timeout=300.0) as client:
                files = {
                    "file": (os.path.basename(temp_file_path), open(temp_file_path, "rb"), "audio/mpeg")
                }
                
                form_data = {
                    "model": "whisper-1",
                    "language": language,
                    "response_format": "verbose_json",
                    "timestamp_granularities[]": timestamp_granularities
                }
                
                response = await client.post(
                    self.API_URL,
                    headers=headers,
                    files=files,
                    data=form_data
                )
                
                response.raise_for_status()
                result = response.json()
                
                processing_time = time.time() - start_time
                
                # Add processing metadata
                result["_metadata"] = {
                    "processing_time": processing_time,
                    "model": "whisper-1",
                    "timestamp_granularities": timestamp_granularities
                }
                
                return result
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            raise
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    def parse_segments(self, whisper_result: Dict[str, Any]) -> List[TranscriptSegment]:
        """
        Parse Whisper API response into transcript segments
        
        Args:
            whisper_result: Response from Whisper API
            
        Returns:
            List of TranscriptSegment objects
        """
        segments = []
        
        for segment in whisper_result.get("segments", []):
            transcript_segment = TranscriptSegment(
                start_time=segment.get("start", 0.0),
                end_time=segment.get("end", 0.0),
                text=segment.get("text", "").strip()
            )
            segments.append(transcript_segment)
        
        return segments