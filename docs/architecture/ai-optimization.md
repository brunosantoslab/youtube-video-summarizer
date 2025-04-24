# AI Optimization Architecture

This document details the architecture and implementation of the AI cost optimization and caching system for the YouTube Video Summarizer (YVS) project.

## Overview

The AI optimization system provides several key features:
1. Token usage optimization to reduce costs
2. Multi-level caching for AI results
3. Budget tracking and management
4. Provider fallback strategies
5. Administrative API for monitoring and control

## Components

### 1. Token Optimizer

The `TokenOptimizer` class is responsible for reducing token usage by:
- Counting tokens for different models
- Optimizing transcript text through redundancy removal and intelligent truncation
- Optimizing prompt structure to maximize information density
- Providing strategies for handling long content without information loss

![Token Optimization Flow](https://mermaid.ink/img/pako:eNptkU1vgzAMhv-K5VOLtKTtpVKlSTs0adIOu-y0w4gK0YIQKR-qKvHfF0i3w5YcHL_PazuO1-ik0CghsmZlF0pJb6lhP1pp1YCVpmUSXnpw7LoLhbI4ncpj2Vh2Vh0PZC4ybSBhBcq73jtJ4J2CpXPcYOV_oPIEm1A7b8j11rGw9g9b44NW_prwJKRxZg6HUElSTnL1FVnYm2PcU6ebj7RLWFmEQl-EqSEw2e1t-3h1DZ-Y6YH9hl-fxELvjK5ZYY3XtDZqh9z9oqldR_rl7mwNspTBf_xvyD-qn-qqetXdpLBobMUKHxbmWMtO6bsjqrVSniFJk0dIbpMUHtI0TtMkji-ZDTJ2PEfALOQMXZ7F0Tx6hMdZDmme5nH0BsYreBc?type=png)

### 2. AI Cache Service

The `AICacheService` provides mechanisms for:
- Caching AI results based on input content hashes
- Managing TTL and invalidation strategies
- Indexing cached entries for monitoring
- Optimizing cache hit rates through intelligent key generation

Cache keys are constructed using the following pattern:
```
ai:cache:{type}:{content_hash}:{provider}:{model}:{params}
```

![Caching Architecture](https://mermaid.ink/img/pako:eNp9kk9rgzAYxr9KeDdp6dq7UChrt8OgnbbrLsFEU4faJCTWMcZ3X6LWrv1TeAm_53nzJ8_RSlGjhsiqwXaQJL3B2v4YIaQGI7ROaDy06OzuGAqF43aQ8ggby06q9Z6MWSYVRKwA8dGOThB4IWBw1mqo3N-oXE1HdGLbZkS2uY6FtVPscQxK-GfCk5DGmdod94VY53Z0xRS0-gBpdMLWfWHrbVixFu87QKJ1Q6GV_Ea6c23PptdeNhPzDMvKUOhCmBwCk-1uGe8vruEHZmxg3-HbB7HQW61KltU5GIHF1CRfQHhsAMvK03_8T8g36rviYF-1meTl9aD05ZRFO1pKwkYvKnl5VU9TXJ7h_nZ3jy9pEt3BS5JEcXL6A1UPDx0?type=png)

### 3. Budget Service

The `AIBudgetService` handles:
- Tracking usage by provider, model, and date
- Converting tokens to costs based on provider pricing
- Enforcing daily budget limits
- Providing historical usage statistics
- Estimating costs before making API calls

Budget information is stored in Redis with keys following this pattern:
```
ai:usage:{date}
```

![Budget Tracking](https://mermaid.ink/img/pako:eNptkkFvgjAUx79KeTeNiW5eJCYGvRhNnGaXnfZSaB8yKbSlZU6M8bsvUMHp9ND0_d_v9aX_vlcaLWTIq8HaiBLfYm1_rJRKg5W64CzuW3Tm0MVCkfF-kIoYNpaeVOs9GbNcKeC8AvkaRydIPEuYnLMaKvcnKlezSI7pqpmQaa7j4ugp7nEMWvqniCehjTPbj_tSLno3uWIKRr-DUZ2wdTy2jg2v-OK-A2RGNRRahR-oO9f2bDrtRTdhj1BWlkKX0hYQmVx2Zry_uoY3zNnAfcV3z2Kht0aXvKhzsBKLqdl8AeGxASyqFv_xPyk_qBF9NVM9c5Gs6t5LTq9M-qFaScJGJypZc1FPSdYVcb5Lbvldlt7eJW9p2Avr?type=png)

### 4. AI Provider Client

The `AIProviderClient` acts as a facade for AI services and integrates the optimization components:
- Manages multiple AI providers (OpenAI, Google, etc.)
- Implements fallback strategies when providers fail
- Integrates with optimization services
- Provides a unified interface for AI operations

![Provider Client Architecture](https://mermaid.ink/img/pako:eNp9ks1ugzAQhF9l5WukFpLcK1WqRHLoL-qhl14qH4xJXAUbGZtWEeLdaxNCE6VV98Kezzezu16k1hxRsKzzYsBI-oCV-7JSSQtW6ZKzeLToXX8OhSLj7SDlMWycPqrWezLmuVLAeY38PY5OkngWMDrvrNbufmVdLJE8nWxG5JrruDh7insai1b-V8TT0MWZHcd9JaK-my6YgtUfYHVHbB2D3bEW33vJUivW1I7NfwzOTfNcRr94YVkZCl1KVyzS3G3X8eHuGj4wZwP3hZ8-icF3axrGyx68wGIuF4j0tEGsK0__8T8lP7AzeVXP6rlc1rVbN3MbZe9oJQsXvbCk5dU9JWlXzC9Zvt4t17v7dB3lm_wZWxJSo8O25ShZEcd4FTcEczkNXhHYpuP3nRkPmA?type=png)

## Data Flow

The overall data flow for AI operations with optimization is:

1. **Request Received**
   - Application requests a summary or topic extraction

2. **Cache Check**
   - Check if result is already cached
   - Return cached result if available and valid

3. **Budget Check**
   - Check if current usage is within daily budget
   - Reject or proceed based on budget status

4. **Token Optimization**
   - Optimize input text to reduce tokens
   - Optimize prompts to reduce tokens

5. **Provider Selection**
   - Select primary provider based on configuration
   - Prepare fallback options if needed

6. **API Call**
   - Make the API call to the selected provider
   - Track token usage and costs

7. **Result Caching**
   - Cache successful results for future use

8. **Fallback Handling**
   - Try fallback providers if primary fails
   - Update statistics on provider reliability

## Monitoring and Control

The system provides API endpoints for monitoring and control:

- `/api/ai-optimization/cache-stats` - Get cache statistics
- `/api/ai-optimization/budget-info` - Get current budget information
- `/api/ai-optimization/usage-history` - Get historical usage data
- `/api/ai-optimization/clear-cache` - Clear cache entries

## Configuration

Optimization settings are defined in the application configuration:

```python
# AI Cost Optimization
ai_cache_enabled: bool = True
ai_cache_ttl: int = 86400  # 24 hours in seconds
ai_daily_budget: float = 10.0  # Daily budget in USD
ai_token_optimization_enabled: bool = True
ai_prompt_optimization_enabled: bool = True

# AI Provider costs per 1K tokens (input/output) in USD
ai_provider_costs: Dict[str, Dict[str, float]] = {
    "openai": {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
    },
    "google": {
        "gemini-pro": {"input": 0.00125, "output": 0.00375}
    }
}
```

*Author: Bruno Santos*
