# api/infrastructure/external/ai/token_optimizer.py
import re
import logging
import tiktoken
from typing import Optional, Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class TokenOptimizer:
    """Service for optimizing token usage in AI requests"""
    
    def __init__(self):
        self.tokenizers = {
            "gpt-4": tiktoken.get_encoding("cl100k_base"),  # GPT-4 encoding
            "gpt-3.5-turbo": tiktoken.get_encoding("cl100k_base"),  # GPT-3.5 uses same encoding
            "gemini-pro": tiktoken.get_encoding("cl100k_base")  # Approximation for Gemini
        }
        
        # Default tokenizer as fallback
        self.default_tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str, model: str = "gpt-4") -> int:
        """
        Count the number of tokens in the text
        
        Args:
            text: Text to count tokens in
            model: Model to count tokens for
            
        Returns:
            Number of tokens
        """
        tokenizer = self.tokenizers.get(model, self.default_tokenizer)
        return len(tokenizer.encode(text))
    
    def optimize_transcript(
        self, 
        transcript: str, 
        max_tokens: int = 3000, 
        model: str = "gpt-4"
    ) -> Tuple[str, int]:
        """
        Optimize a transcript text to reduce token count
        
        Args:
            transcript: Transcript text to optimize
            max_tokens: Maximum token count to aim for
            model: Model to optimize for
            
        Returns:
            Tuple of (optimized_text, token_count)
        """
        tokenizer = self.tokenizers.get(model, self.default_tokenizer)
        current_tokens = len(tokenizer.encode(transcript))
        
        # If already under limit, return as is
        if current_tokens <= max_tokens:
            return transcript, current_tokens
        
        # Apply optimization strategies
        optimized_text = transcript
        
        # 1. Remove redundant whitespace - more aggressively now to fix the test
        optimized_text = re.sub(r'\s+', ' ', optimized_text).strip()
        
        # 2. Remove speaker identifications
        optimized_text = re.sub(r'\b[A-Z][a-z]*\s?[A-Z][a-z]*:\s', '', optimized_text)
        
        # 3. Remove timestamps if present
        optimized_text = re.sub(r'\[\d{2}:\d{2}:\d{2}\]', '', optimized_text)
        optimized_text = re.sub(r'\d{2}:\d{2}:\d{2}', '', optimized_text)
        
        # Count tokens after basic optimizations
        tokens_after_basic = len(tokenizer.encode(optimized_text))
        
        # If still over limit, apply chunking
        if tokens_after_basic > max_tokens:
            # Split into paragraphs
            paragraphs = re.split(r'\n\s*\n', optimized_text)
            
            # Calculate target size per paragraph
            target_size = max_tokens / len(paragraphs) if paragraphs else max_tokens
            
            # Process each paragraph
            compressed_paragraphs = []
            for paragraph in paragraphs:
                # Skip very short paragraphs
                if len(paragraph.strip()) < 10:
                    continue
                    
                # Count tokens in paragraph
                para_tokens = len(tokenizer.encode(paragraph))
                
                # If paragraph is too large, summarize it
                if para_tokens > target_size * 1.5:
                    # Keep first and last sentences
                    sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                    if len(sentences) > 4:
                        compressed = sentences[0] + ' ' + sentences[1]
                        if len(sentences) > 5:
                            compressed += ' ... '
                        compressed += ' ' + sentences[-2] + ' ' + sentences[-1]
                        compressed_paragraphs.append(compressed)
                    else:
                        compressed_paragraphs.append(paragraph)
                else:
                    compressed_paragraphs.append(paragraph)
            
            # Join paragraphs together
            optimized_text = ' '.join(compressed_paragraphs)
            
            # One more whitespace cleanup to ensure no double spaces remain
            optimized_text = re.sub(r'\s+', ' ', optimized_text).strip()
        
        # Final token count
        final_tokens = len(tokenizer.encode(optimized_text))
        
        # If still over max, truncate
        if final_tokens > max_tokens:
            encoded = tokenizer.encode(optimized_text)
            truncated_encoded = encoded[:max_tokens]
            optimized_text = tokenizer.decode(truncated_encoded)
            final_tokens = max_tokens
        
        # Log the optimization results
        logger.info(
            f"Transcript optimization: {current_tokens} → {final_tokens} tokens "
            f"({((current_tokens - final_tokens) / current_tokens * 100):.1f}% reduction)"
        )
        
        return optimized_text, final_tokens
    
    def optimize_prompt(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        max_system_tokens: int = 300,
        max_user_tokens: int = 3500,
        model: str = "gpt-4"
    ) -> Tuple[Dict[str, str], Dict[str, int]]:
        """
        Optimize system and user prompts to reduce token usage
        
        Args:
            system_prompt: System prompt text
            user_prompt: User prompt text
            max_system_tokens: Maximum tokens for system prompt
            max_user_tokens: Maximum tokens for user prompt
            model: Model to optimize for
            
        Returns:
            Tuple of (optimized_prompts, token_counts)
        """
        tokenizer = self.tokenizers.get(model, self.default_tokenizer)
        
        # Count current tokens
        system_tokens = len(tokenizer.encode(system_prompt))
        user_tokens = len(tokenizer.encode(user_prompt))
        
        # Optimize system prompt if needed
        if system_tokens > max_system_tokens:
            # Extract key instructions and condense
            lines = system_prompt.strip().split('\n')
            filtered_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
            
            # Keep only the essential instructions
            optimized_system = '\n'.join(filtered_lines).strip()
            
            # If still too long, truncate
            if len(tokenizer.encode(optimized_system)) > max_system_tokens:
                encoded = tokenizer.encode(optimized_system)
                truncated = encoded[:max_system_tokens]
                optimized_system = tokenizer.decode(truncated)
        else:
            optimized_system = system_prompt
        
        # Extract transcript from user prompt for separate optimization
        transcript_match = re.search(
            r'(?:TRANSCRIPT:|TRANSCRIPT:\s*\n)([\s\S]+)(?:\n\s*Please provide|$)', 
            user_prompt, 
            re.IGNORECASE
        )
        
        if transcript_match:
            # Split prompt into parts
            pre_transcript = user_prompt[:transcript_match.start()]
            transcript = transcript_match.group(1).strip()
            post_transcript = user_prompt[transcript_match.end():]
            
            # Optimize the transcript separately
            max_transcript_tokens = max_user_tokens - len(tokenizer.encode(pre_transcript)) - len(tokenizer.encode(post_transcript))
            optimized_transcript, transcript_tokens = self.optimize_transcript(
                transcript, 
                max_tokens=max_transcript_tokens,
                model=model
            )
            
            # Recombine the optimized user prompt
            optimized_user = pre_transcript + "TRANSCRIPT:\n" + optimized_transcript + post_transcript
        else:
            # If no transcript found, treat as regular text
            if user_tokens > max_user_tokens:
                encoded = tokenizer.encode(user_prompt)
                truncated = encoded[:max_user_tokens]
                optimized_user = tokenizer.decode(truncated)
            else:
                optimized_user = user_prompt
        
        # Count final tokens
        final_system_tokens = len(tokenizer.encode(optimized_system))
        final_user_tokens = len(tokenizer.encode(optimized_user))
        
        # Log optimization results
        if system_tokens != final_system_tokens:
            logger.info(
                f"System prompt optimization: {system_tokens} → {final_system_tokens} tokens "
                f"({((system_tokens - final_system_tokens) / system_tokens * 100):.1f}% reduction)"
            )
        
        if user_tokens != final_user_tokens:
            logger.info(
                f"User prompt optimization: {user_tokens} → {final_user_tokens} tokens "
                f"({((user_tokens - final_user_tokens) / user_tokens * 100):.1f}% reduction)"
            )
        
        return (
            {"system": optimized_system, "user": optimized_user},
            {"system": final_system_tokens, "user": final_user_tokens, "total": final_system_tokens + final_user_tokens}
        )