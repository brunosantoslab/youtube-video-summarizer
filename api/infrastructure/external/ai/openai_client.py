# api/infrastructure/external/ai/openai_client.py
import logging
import time
from typing import Dict, List, Any, Optional

import openai
from openai import OpenAI

from config import get_settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Client for OpenAI APIs"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_settings().openai_api_key
        self.client = OpenAI(api_key=self.api_key)
    
    async def generate_summary(
        self, 
        transcript_text: str, 
        max_length: int = 500,
        model: str = "gpt-4"
    ) -> Dict[str, Any]:
        """
        Generate a summary from transcript text
        
        Args:
            transcript_text: The text to summarize
            max_length: Maximum length of summary in tokens
            model: Model to use for summarization
            
        Returns:
            Dictionary with summary and metadata
        """
        try:
            start_time = time.time()
            
            # Create prompt
            prompt = self._create_summary_prompt(transcript_text, max_length)
            
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": prompt["user"]}
                ],
                max_tokens=max_length,
                temperature=0.5
            )
            
            # Extract summary
            summary_text = response.choices[0].message.content
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Return result with metadata
            return {
                "text": summary_text,
                "model": model,
                "metadata": {
                    "processing_time": processing_time,
                    "token_count": response.usage.total_tokens,
                    "prompt_version": "1.0",
                    "model_parameters": {
                        "temperature": 0.5,
                        "max_tokens": max_length
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating summary with OpenAI: {str(e)}")
            raise
    
    def _create_summary_prompt(self, transcript_text: str, max_length: int) -> Dict[str, str]:
        """
        Create the prompt for summarization
        
        Args:
            transcript_text: Transcript text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Dictionary with system and user prompts
        """
        system_prompt = """
        You are an expert summarizer that creates concise, informative summaries of YouTube videos based on their transcripts.
        Your summaries should:
        1. Capture the key points and main message
        2. Be well-structured and easy to read
        3. Be factual and objective, based only on the transcript
        4. Highlight important concepts, technologies, or ideas mentioned
        5. Avoid unnecessary details, tangents, or repetition
        
        Make the summary informative enough that the user understands what the video was about without watching it.
        """
        
        user_prompt = f"""
        Below is a transcript from a YouTube video. Please provide a concise summary that captures the main points and key information.
        
        TRANSCRIPT:
        {transcript_text}
        
        Please provide a summary of approximately {max_length//4} words.
        """
        
        return {
            "system": system_prompt.strip(),
            "user": user_prompt.strip()
        }