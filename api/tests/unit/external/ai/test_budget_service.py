# api/tests/unit/external/ai/test_budget_service.py
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json
from datetime import datetime

from infrastructure.external.ai.budget_service import AIBudgetService


class TestBudgetService:
    """Test cases for the AIBudgetService class"""
    
    @pytest.fixture
    def mock_redis_cache(self):
        """Mock Redis cache for testing"""
        cache = AsyncMock()
        cache.get = AsyncMock(return_value=None)
        cache.set = AsyncMock(return_value=True)
        return cache
    
    @pytest.fixture
    def budget_service(self, mock_redis_cache):
        """Create AIBudgetService with mocked dependencies"""
        with patch('infrastructure.external.ai.budget_service.get_settings') as mock_settings:
            # Use concrete values instead of MagicMock objects
            mock_settings.return_value.ai_provider_costs = {
                "openai": {
                    "gpt-4": {"input": 0.03, "output": 0.06},
                    "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
                },
                "google": {
                    "gemini-pro": {"input": 0.00125, "output": 0.00375}
                }
            }
            # Important fix: We need to use a real number here, not a MagicMock
            mock_settings.return_value.daily_budget = 10.0
            
            service = AIBudgetService(mock_redis_cache)
            # Override the daily_budget property directly to ensure it's a real number
            service.daily_budget = 10.0
            return service
    
    @pytest.mark.asyncio
    async def test_track_usage(self, budget_service, mock_redis_cache):
        """Test tracking usage and cost calculation"""
        # Define test data
        provider = "openai"
        model = "gpt-4"
        input_tokens = 1000
        output_tokens = 500
        
        # Setup mock
        today = datetime.now().strftime("%Y-%m-%d")
        key = f"ai:usage:{today}"
        
        # Call the method
        cost = await budget_service.track_usage(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )
        
        # Verify calculations
        expected_cost = (input_tokens / 1000 * 0.03) + (output_tokens / 1000 * 0.06)
        assert cost == expected_cost
        
        # Verify Redis interactions
        mock_redis_cache.get.assert_called_with(key)
        mock_redis_cache.set.assert_called_once()
        
        # Verify content of set call
        call_args = mock_redis_cache.set.call_args[0]
        assert call_args[0] == key
        
        # Decode JSON
        usage_data = json.loads(call_args[1])
        assert usage_data["total_cost"] == expected_cost
        assert provider in usage_data["providers"]
        assert model in usage_data["providers"][provider]
        assert usage_data["providers"][provider][model]["input_tokens"] == input_tokens
        assert usage_data["providers"][provider][model]["output_tokens"] == output_tokens
    
    @pytest.mark.asyncio
    async def test_check_budget(self, budget_service, mock_redis_cache):
        """Test budget checking functionality"""
        # Setup mock
        today = datetime.now().strftime("%Y-%m-%d")
        key = f"ai:usage:{today}"
        
        mock_usage = {
            "total_cost": 5.0,
            "providers": {
                "openai": {
                    "gpt-4": {
                        "cost": 5.0,
                        "input_tokens": 100000,
                        "output_tokens": 20000,
                        "requests": 10
                    }
                }
            }
        }
        
        mock_redis_cache.get.return_value = json.dumps(mock_usage)
        
        # Call the method
        budget_info = await budget_service.check_budget()
        
        # Verify results
        assert budget_info["date"] == today
        assert budget_info["daily_budget"] == 10.0
        assert budget_info["current_cost"] == 5.0
        assert budget_info["remaining_budget"] == 5.0
        assert budget_info["percentage_used"] == 50.0
        assert budget_info["is_budget_exceeded"] is False
    
    @pytest.mark.asyncio
    async def test_is_within_budget(self, budget_service):
        """Test budget threshold checking"""
        # Mock check_budget to return controlled data
        with patch.object(budget_service, 'check_budget') as mock_check:
            # Test within budget
            mock_check.return_value = {
                "is_budget_exceeded": False
            }
            assert await budget_service.is_within_budget() is True
            
            # Test over budget
            mock_check.return_value = {
                "is_budget_exceeded": True
            }
            assert await budget_service.is_within_budget() is False
    
    def test_calculate_cost(self, budget_service):
        """Test cost calculation for different providers and models"""
        # Test OpenAI GPT-4
        cost = budget_service._calculate_cost("openai", "gpt-4", 1000, 500)
        expected = (1000 / 1000 * 0.03) + (500 / 1000 * 0.06)
        assert cost == expected
        
        # Test OpenAI GPT-3.5
        cost = budget_service._calculate_cost("openai", "gpt-3.5-turbo", 1000, 500)
        expected = (1000 / 1000 * 0.0015) + (500 / 1000 * 0.002)
        assert cost == expected
        
        # Test Google Gemini
        cost = budget_service._calculate_cost("google", "gemini-pro", 1000, 500)
        expected = (1000 / 1000 * 0.00125) + (500 / 1000 * 0.00375)
        assert cost == expected
        
        # Test unknown provider
        cost = budget_service._calculate_cost("unknown", "model", 1000, 500)
        assert cost == 0
        
        # Test unknown model
        cost = budget_service._calculate_cost("openai", "unknown", 1000, 500)
        assert cost == 0