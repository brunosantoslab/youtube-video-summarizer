# api/infrastructure/external/ai/langchain_client.py
import logging
import time
from typing import Dict, List, Any, Optional

# Updated imports for newer LangChain version
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.chains import LLMChain
from pydantic import BaseModel, Field

from config import get_settings

logger = logging.getLogger(__name__)


class ExtractedTopic(BaseModel):
    """Model for a topic extracted from text"""
    name: str = Field(description="Short name of the topic")
    description: str = Field(description="Brief description of the topic")
    relevance: float = Field(description="Relevance score from 0.0 to 1.0")


class ExtractedTopics(BaseModel):
    """Model for a list of extracted topics"""
    topics: List[ExtractedTopic]


class LangChainClient:
    """Client for LangChain-based workflows"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.api_key = openai_api_key or get_settings().openai_api_key
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            temperature=0.2,
            model_name="gpt-4"
        )
    
    async def extract_topics(
        self, 
        text: str,
        max_topics: int = 5,
        min_relevance: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Extract topics from text using LangChain
        
        Args:
            text: Text to extract topics from
            max_topics: Maximum number of topics to extract
            min_relevance: Minimum relevance score (0.0 to 1.0)
            
        Returns:
            List of topics with name, description, and relevance
        """
        try:
            start_time = time.time()
            
            # Set up output parser
            parser = PydanticOutputParser(pydantic_object=ExtractedTopics)
            
            # Create the prompt template
            system_template = f"""
            You are an expert at extracting key topics from text.
            Extract the {max_topics} most important topics from the provided text.
            For each topic, provide:
            1. A short name (1-3 words)
            2. A brief description (1-2 sentences)
            3. A relevance score from 0.0 to 1.0 (where 1.0 is highly relevant)
            
            Only include topics with relevance >= {min_relevance}.
            Format the output exactly as specified.
            """
            
            human_template = """
            Text: {text}
            
            {format_instructions}
            """
            
            # Create the prompt with updated LangChain approach
            chat_prompt = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(system_template),
                HumanMessagePromptTemplate.from_template(human_template)
            ])
            
            # Create and run the chain
            chain = LLMChain(llm=self.llm, prompt=chat_prompt)
            result = await chain.arun(
                text=text,
                format_instructions=parser.get_format_instructions()
            )
            
            # Parse the output
            topics_data = parser.parse(result)
            
            # Convert to dictionary format
            topics = []
            for topic in topics_data.topics:
                topics.append({
                    "name": topic.name,
                    "description": topic.description,
                    "relevance": topic.relevance
                })
            
            # Log processing time
            processing_time = time.time() - start_time
            logger.info(f"Topic extraction completed in {processing_time:.2f}s")
            
            return topics
            
        except Exception as e:
            logger.error(f"Error extracting topics: {str(e)}")
            raise
    
    async def detect_topic_timestamps(
        self,
        transcript_segments: List[Dict[str, Any]],
        topics: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, float]]:
        """
        Detect timestamps for when topics occur in transcript
        
        Args:
            transcript_segments: List of transcript segments with start_time, end_time, text
            topics: List of topics with name, description
            
        Returns:
            Dictionary mapping topic names to start/end times
        """
        try:
            # Implementation will depend on transcript segment format
            # This is a simplified version that looks for keyword matches
            
            topic_names = [topic["name"].lower() for topic in topics]
            topic_timestamps = {topic["name"]: {"start": None, "end": None} for topic in topics}
            
            for segment in transcript_segments:
                segment_text = segment["text"].lower()
                for i, topic_name in enumerate(topic_names):
                    # Simple keyword matching - could be improved with NLP
                    if topic_name in segment_text:
                        # If this is the first mention, set start time
                        if topic_timestamps[topics[i]["name"]]["start"] is None:
                            topic_timestamps[topics[i]["name"]]["start"] = segment["start_time"]
                        
                        # Always update end time when topic is mentioned
                        topic_timestamps[topics[i]["name"]]["end"] = segment["end_time"]
            
            return topic_timestamps
            
        except Exception as e:
            logger.error(f"Error detecting topic timestamps: {str(e)}")
            raise