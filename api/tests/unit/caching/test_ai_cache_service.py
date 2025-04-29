"""
Unit tests for the AI Cache Service
Author: Bruno Santos
"""
import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock, call
import hashlib

from infrastructure.caching.ai_cache_service import AICacheService
from config import get_settings


class TestAICacheService:
    """Test cases for the AICacheService class"""
    
    @pytest.fixture
    def mock_redis_cache(self):
        """Create a mock Redis cache for testing"""
        cache = AsyncMock()
        cache.get = AsyncMock(return_value=None)
        cache.set = AsyncMock(return_value=True)
        cache.delete = AsyncMock(return_value=1)
        return cache
    
    @pytest.fixture
    def cache_service(self, mock_redis_cache):
        """Create an AICacheService with mocked dependencies"""
        with patch('infrastructure.caching.ai_cache_service.get_settings') as mock_settings:
            mock_settings.return_value.ai_cache_enabled = True
            mock_settings.return_value.ai_cache_ttl = 86400
            
            service = AICacheService(mock_redis_cache)
            return service
    
    def test_get_content_hash(self, cache_service):
        """Test content hash generation"""
        # Test with simple string
        content = "This is a test content"
        expected_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        # Generate hash
        content_hash = cache_service.get_content_hash(content)
        
        # Verify hash
        assert content_hash == expected_hash
    
    def test_cache_key_generation(self, cache_service):
        """Test cache key generation methods"""
        # Test summary cache key
        summary_key = cache_service._get_summary_cache_key(
            transcript_hash="123abc",
            provider="openai",
            model="gpt-4",
            max_tokens=500
        )
        assert summary_key == "ai:cache:summary:123abc:openai:gpt-4:500"
        
        # Test topics cache key
        topics_key = cache_service._get_topics_cache_key(
            summary_hash="456def",
            max_topics=5,
            min_relevance=0.3
        )
        assert topics_key == "ai:cache:topics:456def:5:0_3"
    
    @pytest.mark.asyncio
    async def test_get_summary_cache_hit(self, cache_service, mock_redis_cache):
        """Test successful cache hit for summary"""
        # Setup mock
        mock_summary = {
            "text": "This is a summary",
            "model": "gpt-4",
            "metadata": {"token_count": 100}
        }
        mock_redis_cache.get.return_value = json.dumps(mock_summary)
        
        # Call the method
        result = await cache_service.get_summary(
            transcript_hash="123abc",
            provider="openai",
            model="gpt-4",
            max_tokens=500
        )
        
        # Verify results
        assert result == mock_summary
        
        # Verify Redis call
        expected_key = "ai:cache:summary:123abc:openai:gpt-4:500"
        mock_redis_cache.get.assert_called_with(expected_key)
    
    @pytest.mark.asyncio
    async def test_get_summary_cache_miss(self, cache_service, mock_redis_cache):
        """Test cache miss for summary"""
        # Setup mock
        mock_redis_cache.get.return_value = None
        
        # Call the method
        result = await cache_service.get_summary(
            transcript_hash="123abc",
            provider="openai",
            model="gpt-4",
            max_tokens=500
        )
        
        # Verify results
        assert result is None
        
        # Verify Redis call
        expected_key = "ai:cache:summary:123abc:openai:gpt-4:500"
        mock_redis_cache.get.assert_called_with(expected_key)
    
    @pytest.mark.asyncio
    async def test_set_summary(self, cache_service, mock_redis_cache):
        """Test setting summary in cache"""
        # Setup test data
        transcript_hash = "123abc"
        provider = "openai"
        model = "gpt-4"
        max_tokens = 500
        summary_data = {
            "text": "This is a summary",
            "model": "gpt-4",
            "metadata": {"token_count": 100}
        }
        
        # Setup for index update
        mock_redis_cache.get.return_value = json.dumps([])
        
        # Call the method
        result = await cache_service.set_summary(
            transcript_hash=transcript_hash,
            provider=provider,
            model=model,
            max_tokens=max_tokens,
            summary_data=summary_data,
            ttl=3600
        )
        
        # Verify results
        assert result is True
        
        # Verify Redis calls - we need to check both calls now
        expected_key = "ai:cache:summary:123abc:openai:gpt-4:500"
        assert mock_redis_cache.set.call_count == 2
        
        # First call should be to set the summary
        first_call = mock_redis_cache.set.call_args_list[0]
        assert first_call.args[0] == expected_key
        assert first_call.args[1] == json.dumps(summary_data)
        assert first_call.kwargs['ex'] == 3600
        
        # Second call should be to update the index
        second_call = mock_redis_cache.set.call_args_list[1]
        assert second_call.args[0] == "ai:cache:index:summaries"
        assert json.loads(second_call.args[1]) == [expected_key]
    
    @pytest.mark.asyncio
    async def test_get_topic_extraction_cache_hit(self, cache_service, mock_redis_cache):
        """Test successful cache hit for topic extraction"""
        # Setup mock
        mock_topics = [
            {"name": "Topic 1", "relevance": 0.9},
            {"name": "Topic 2", "relevance": 0.7}
        ]
        mock_redis_cache.get.return_value = json.dumps(mock_topics)
        
        # Call the method
        result = await cache_service.get_topic_extraction(
            summary_hash="456def",
            max_topics=5,
            min_relevance=0.3
        )
        
        # Verify results
        assert result == mock_topics
        
        # Verify Redis call
        expected_key = "ai:cache:topics:456def:5:0_3"
        mock_redis_cache.get.assert_called_with(expected_key)
    
    @pytest.mark.asyncio
    async def test_invalidate_cache(self, cache_service, mock_redis_cache):
        """Test cache invalidation"""
        # Setup mock
        mock_redis_cache.delete.return_value = 1
        
        # Call the method
        result = await cache_service.invalidate("ai:cache:summary:123abc")
        
        # Verify results
        assert result is True
        
        # Verify Redis call
        mock_redis_cache.delete.assert_called_with("ai:cache:summary:123abc")
    
    @pytest.mark.asyncio
    async def test_clear_all_cache(self, cache_service, mock_redis_cache):
        """Test clearing all cache entries"""
        # Setup mocks
        summaries_index = ["key1", "key2", "key3"]
        topics_index = ["key4", "key5"]
        
        # Mock get for summaries index
        async def mock_get(key):
            if key == "ai:cache:index:summaries":
                return json.dumps(summaries_index)
            elif key == "ai:cache:index:topics":
                return json.dumps(topics_index)
            return None
        
        mock_redis_cache.get.side_effect = mock_get
        
        # Call the method
        result = await cache_service.clear_all()
        
        # Verify results
        assert result == 5  # Total keys deleted
        
        # Verify Redis calls - should delete all keys from both indexes
        assert mock_redis_cache.delete.call_count == 7  # 5 keys + 2 index keys
    
    @pytest.mark.asyncio
    async def test_cache_disabled(self, mock_redis_cache):
        """Test behavior when cache is disabled"""
        # Create service with cache disabled
        with patch('infrastructure.caching.ai_cache_service.get_settings') as mock_settings:
            mock_settings.return_value.ai_cache_enabled = False
            service = AICacheService(mock_redis_cache)
            
            # Test get summary
            result = await service.get_summary("hash", "openai", "gpt-4", 500)
            assert result is None
            mock_redis_cache.get.assert_not_called()
            
            # Test set summary
            result = await service.set_summary("hash", "openai", "gpt-4", 500, {})
            assert result is False
            mock_redis_cache.set.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_update_index(self, cache_service, mock_redis_cache):
        """Test index updating functionality"""
        # Setup mock for existing index
        existing_index = ["key1", "key2"]
        mock_redis_cache.get.return_value = json.dumps(existing_index)
        
        # Call the method
        await cache_service._update_index("summaries", "key3")
        
        # Verify results - check that set was called with expected arguments
        expected_index = ["key1", "key2", "key3"]
        mock_redis_cache.set.assert_called_once()
        call_args = mock_redis_cache.set.call_args
        
        assert call_args.args[0] == "ai:cache:index:summaries"
        assert json.loads(call_args.args[1]) == expected_index
        assert call_args.kwargs["ex"] == 172800  # 2x the default TTL
        
        # Test adding duplicate key
        mock_redis_cache.reset_mock()
        mock_redis_cache.get.return_value = json.dumps(expected_index)
        
        # Call with existing key
        await cache_service._update_index("summaries", "key2")
        
        # Index should not change but set should still be called
        mock_redis_cache.set.assert_called_once()
        call_args = mock_redis_cache.set.call_args
        
        assert call_args.args[0] == "ai:cache:index:summaries"
        assert json.loads(call_args.args[1]) == expected_index  # Same as before
        assert call_args.kwargs["ex"] == 172800
