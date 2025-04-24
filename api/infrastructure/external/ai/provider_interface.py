# api/infrastructure/external/ai/provider_interface.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class AIProviderInterface(ABC):
    """Interface for AI providers"""
    
    @abstractmethod
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
        pass