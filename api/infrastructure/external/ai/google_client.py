# api/infrastructure/external/ai/google_client.py
import logging
import time
from typing import Dict, Any, Optional

import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse

from config import get_settings
from infrastructure.external.ai.provider_interface import AIProviderInterface
from infrastructure.external.ai.token_optimizer import TokenOptimizer

logger = logging.getLogger(__name__)


class GoogleAIClient(AIProviderInterface):
    """Client for Google Gemini AI APIs"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_settings().google_ai_api_key
        genai.configure(api_key=self.api_key)
        self.model = None
        self.token_optimizer = TokenOptimizer()
    
    async def generate_summary(
        self, 
        transcript_text: str, 
        max_length: int = 500,
        model: str = None
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
        # Set default model
        model_name = model or "gemini-pro"
        
        try:
            start_time = time.time()
            
            # Initialize model
            if not self.model or self.model.model_name != model_name:
                self.model = genai.GenerativeModel(model_name=model_name)
            
            # Create prompt
            prompt = self._create_summary_prompt(transcript_text, max_length)
            
            # Optimize prompt if enabled
            if hasattr(self, 'token_optimizer') and get_settings().ai_prompt_optimization_enabled:
                # Google doesn't use separate system/user prompts, so we optimize just the user prompt
                optimized_prompts, token_counts = self.token_optimizer.optimize_prompt(
                    system_prompt="",
                    user_prompt=prompt,
                    model="gemini-pro"  # Use Gemini model for token counting
                )
                prompt_to_use = optimized_prompts["user"]
                logger.info(f"Using optimized prompt: {token_counts['user']} tokens")
            else:
                prompt_to_use = prompt
            
            # Estimate token count
            input_tokens = self.token_optimizer.count_tokens(prompt_to_use, "gemini-pro")
            
            # Call the Google AI API
            response = self.model.generate_content(
                prompt_to_use,
                generation_config={
                    "temperature": 0.5,
                    "max_output_tokens": max_length,
                }
            )
            
            # Extract summary
            summary_text = response.text
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Estimate output tokens
            output_tokens = self.token_optimizer.count_tokens(summary_text, "gemini-pro")
            
            # Return result with metadata
            return {
                "text": summary_text,
                "model": model_name,
                "provider": "google",
                "metadata": {
                    "processing_time": processing_time,
                    "token_count": input_tokens + output_tokens,  # Estimated
                    "prompt_tokens": input_tokens,  # Estimated
                    "completion_tokens": output_tokens,  # Estimated
                    "prompt_version": "1.1",
                    "model_parameters": {
                        "temperature": 0.5,
                        "max_output_tokens": max_length
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating summary with Google AI: {str(e)}")
            raise
    
    def _create_summary_prompt(self, transcript_text: str, max_length: int) -> str:
        """
        Create the prompt for summarization
        
        Args:
            transcript_text: Transcript text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Prompt string
        """
        return f"""
        You are an expert summarizer that creates concise, informative summaries of YouTube videos based on their transcripts.
        Your summaries should:
        1. Capture the key points and main message
        2. Be well-structured and easy to read
        3. Be factual and objective, based only on the transcript
        4. Highlight important concepts, technologies, or ideas mentioned
        5. Avoid unnecessary details, tangents, or repetition
        
        Below is a transcript from a YouTube video. Please provide a concise summary that captures the main points and key information.
        
        TRANSCRIPT:
        {transcript_text}
        
        Please provide a summary of approximately {max_length//4} words.
        """