# api/tests/unit/external/ai/test_token_optimizer.py
import pytest
from unittest.mock import patch, MagicMock
import tiktoken

from infrastructure.external.ai.token_optimizer import TokenOptimizer


class TestTokenOptimizer:
    """Test cases for the TokenOptimizer class"""
    
    @pytest.fixture
    def token_optimizer(self):
        """Create a TokenOptimizer instance for testing"""
        return TokenOptimizer()
    
    def test_count_tokens(self, token_optimizer):
        """Test token counting functionality"""
        # Test with a simple string
        text = "This is a test text with multiple words."
        expected_tokens = len(tiktoken.get_encoding("cl100k_base").encode(text))
        
        # Count tokens
        tokens = token_optimizer.count_tokens(text, "gpt-4")
        
        # Assert correct count
        assert tokens == expected_tokens
    
    def test_optimize_transcript_under_limit(self, token_optimizer):
        """Test optimization when transcript is already under the token limit"""
        # Short transcript
        transcript = "This is a short transcript."
        max_tokens = 50
        
        # Optimize
        optimized_text, token_count = token_optimizer.optimize_transcript(
            transcript, max_tokens, "gpt-4"
        )
        
        # Should return original text
        assert optimized_text == transcript
        assert token_count <= max_tokens
    
    def test_optimize_transcript_over_limit(self, token_optimizer):
        """Test optimization when transcript is over the token limit"""
        # Create a long transcript with redundant whitespace and speaker labels
        transcript = """
        Speaker A: Hello, this is speaker A.
        
        Speaker B:   This is speaker B with extra whitespace.  
        
        [00:01:23] This has a timestamp.
        
        Speaker A: This is a very long paragraph with lots of information that should be preserved
        but might need to be truncated if the overall transcript is too long. We want to make sure
        that the important information is kept while reducing the token count efficiently.
        
        Speaker B: Another paragraph with more information.
        """
        max_tokens = 50  # Short limit to force optimization
        
        # Optimize
        optimized_text, token_count = token_optimizer.optimize_transcript(
            transcript, max_tokens, "gpt-4"
        )
        
        # Check results
        assert token_count <= max_tokens
        assert "Speaker A:" not in optimized_text  # Speaker labels removed
        assert "[00:01:23]" not in optimized_text  # Timestamps removed
        assert "  " not in optimized_text  # Extra whitespace removed
    
    def test_optimize_prompt(self, token_optimizer):
        """Test prompt optimization"""
        # Create test prompts
        system_prompt = """
        You are an AI assistant designed to summarize text.
        Please follow these guidelines:
        1. Be concise
        2. Capture key points
        3. Maintain factual accuracy
        4. Highlight important details
        5. Use simple language
        """
        
        user_prompt = f"""
        Please summarize the following transcript:
        
        TRANSCRIPT:
        {'This is a test transcript. ' * 100}
        
        Provide a summary that captures the main points.
        """
        
        # Set limits
        max_system_tokens = 50
        max_user_tokens = 100
        
        # Optimize
        optimized_prompts, token_counts = token_optimizer.optimize_prompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_system_tokens=max_system_tokens,
            max_user_tokens=max_user_tokens
        )
        
        # Check results
        assert token_counts["system"] <= max_system_tokens
        assert token_counts["user"] <= max_user_tokens
        assert "You are an AI assistant" in optimized_prompts["system"]
        assert "TRANSCRIPT:" in optimized_prompts["user"]
        assert "Please summarize" in optimized_prompts["user"]
