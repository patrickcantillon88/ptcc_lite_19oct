"""
LLM Integration Layer for PTCC

Provides unified interface for multiple LLM providers:
- Google Gemini
- OpenAI
- Anthropic Claude
- Local models

Includes token tracking, cost estimation, and error handling.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
import os
from datetime import datetime
import json

from .logging_config import get_logger
from .config import get_settings

logger = get_logger("llm_integration")


class LLMProvider(Enum):
    """Supported LLM providers."""
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class LLMModel(Enum):
    """Supported LLM models.
    
    Model IDs are now managed in config/config.yaml.
    These defaults are used if config is unavailable.
    """
    # Gemini models (see config.yaml for centralized definitions)
    GEMINI_PRO = "gemini-2.5-pro"
    GEMINI_FLASH = "gemini-2.5-flash"
    GEMINI_PRO_VISION = "gemini-pro-vision"
    
    # OpenAI models
    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo-preview"
    GPT35_TURBO = "gpt-3.5-turbo"
    
    # Anthropic models
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"


class LLMResponse:
    """Standardized LLM response object."""
    
    def __init__(
        self,
        text: str,
        model: str,
        provider: str,
        usage: Dict[str, int],
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.text = text
        self.model = model
        self.provider = provider
        self.usage = usage
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "model": self.model,
            "provider": self.provider,
            "usage": self.usage,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


class GeminiClient:
    """Google Gemini API client."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.logger = logger
        
        if not self.api_key:
            raise ValueError("Gemini API key not provided")
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.genai = genai
            self.logger.info("Gemini client initialized successfully")
        except ImportError:
            raise ImportError("google-generativeai package not installed. Install with: pip install google-generativeai")
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        """Generate completion using Gemini.
        
        If model not specified, uses default from config.
        """
        # Use config model if not specified
        if model is None:
            from .config import get_gemini_model
            model = get_gemini_model()
        
        try:
            model_instance = self.genai.GenerativeModel(model)
            
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                **kwargs
            }
            
            response = model_instance.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract usage information
            usage = {
                "prompt_tokens": getattr(response.usage_metadata, "prompt_token_count", 0),
                "completion_tokens": getattr(response.usage_metadata, "candidates_token_count", 0),
                "total_tokens": getattr(response.usage_metadata, "total_token_count", 0)
            }
            
            return LLMResponse(
                text=response.text,
                model=model,
                provider="gemini",
                usage=usage,
                metadata={
                    "finish_reason": getattr(response.candidates[0], "finish_reason", None) if response.candidates else None,
                    "safety_ratings": [
                        {
                            "category": rating.category.name,
                            "probability": rating.probability.name
                        }
                        for rating in response.candidates[0].safety_ratings
                    ] if response.candidates else []
                }
            )
            
        except Exception as e:
            self.logger.error(f"Gemini generation error: {e}")
            raise


class OpenAIClient:
    """OpenAI API client."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.logger = logger
        
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            self.logger.info("OpenAI client initialized successfully")
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")
    
    def generate(
        self,
        prompt: str,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        """Generate completion using OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            return LLMResponse(
                text=response.choices[0].message.content,
                model=model,
                provider="openai",
                usage=usage,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "response_id": response.id
                }
            )
            
        except Exception as e:
            self.logger.error(f"OpenAI generation error: {e}")
            raise


class AnthropicClient:
    """Anthropic Claude API client."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.logger = logger
        
        if not self.api_key:
            raise ValueError("Anthropic API key not provided")
        
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
            self.logger.info("Anthropic client initialized successfully")
        except ImportError:
            raise ImportError("anthropic package not installed. Install with: pip install anthropic")
    
    def generate(
        self,
        prompt: str,
        model: str = "claude-3-sonnet-20240229",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        """Generate completion using Claude."""
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            
            usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
            
            return LLMResponse(
                text=response.content[0].text,
                model=model,
                provider="anthropic",
                usage=usage,
                metadata={
                    "stop_reason": response.stop_reason,
                    "response_id": response.id
                }
            )
            
        except Exception as e:
            self.logger.error(f"Anthropic generation error: {e}")
            raise


class LLMOrchestrator:
    """Orchestrates LLM requests across multiple providers."""
    
    def __init__(self):
        self.logger = logger
        self.clients = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize available LLM clients."""
        # Try to initialize Gemini
        try:
            gemini_key = os.getenv("GEMINI_API_KEY")
            if gemini_key:
                self.clients["gemini"] = GeminiClient(gemini_key)
        except Exception as e:
            self.logger.warning(f"Could not initialize Gemini client: {e}")
        
        # Try to initialize OpenAI
        try:
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                self.clients["openai"] = OpenAIClient(openai_key)
        except Exception as e:
            self.logger.warning(f"Could not initialize OpenAI client: {e}")
        
        # Try to initialize Anthropic
        try:
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            if anthropic_key:
                self.clients["anthropic"] = AnthropicClient(anthropic_key)
        except Exception as e:
            self.logger.warning(f"Could not initialize Anthropic client: {e}")
        
        if not self.clients:
            self.logger.warning("No LLM clients initialized. Set API keys in environment.")
    
    def generate(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion using specified or default provider.
        
        Args:
            prompt: The prompt text
            provider: LLM provider to use (gemini, openai, anthropic)
            model: Specific model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
        
        Returns:
            LLMResponse object with generated text and metadata
        """
        # Determine provider
        if provider is None:
            # Use first available provider
            if not self.clients:
                raise ValueError("No LLM clients available. Configure API keys.")
            provider = list(self.clients.keys())[0]
        
        if provider not in self.clients:
            raise ValueError(f"Provider '{provider}' not available. Available: {list(self.clients.keys())}")
        
        # Determine model
        if model is None:
            # Use default model for provider
            default_models = {
                "gemini": "gemini-2.5-flash-exp",
                "openai": "gpt-4-turbo-preview",
                "anthropic": "claude-3-sonnet-20240229"
            }
            model = default_models.get(provider)
        
        self.logger.info(f"Generating with {provider}/{model}")
        
        try:
            response = self.clients[provider].generate(
                prompt=prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            self.logger.info(f"Generated {response.usage['total_tokens']} tokens")
            return response
            
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            raise
    
    def batch_generate(
        self,
        prompts: List[str],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> List[LLMResponse]:
        """Generate completions for multiple prompts."""
        responses = []
        for prompt in prompts:
            try:
                response = self.generate(
                    prompt=prompt,
                    provider=provider,
                    model=model,
                    **kwargs
                )
                responses.append(response)
            except Exception as e:
                self.logger.error(f"Batch generation failed for prompt: {e}")
                responses.append(None)
        
        return responses
    
    def estimate_cost(
        self,
        response: LLMResponse
    ) -> float:
        """Estimate cost of LLM call."""
        # Pricing per 1K tokens (approximate, as of 2025)
        pricing = {
            "gemini": {
                "gemini-2.5-pro-exp": {"input": 0.00025, "output": 0.0005},
                "gemini-2.5-flash-exp": {"input": 0.000125, "output": 0.00025}
            },
            "openai": {
                "gpt-4": {"input": 0.03, "output": 0.06},
                "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
                "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015}
            },
            "anthropic": {
                "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
                "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
                "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125}
            }
        }
        
        provider = response.provider
        model = response.model
        
        if provider not in pricing or model not in pricing[provider]:
            self.logger.warning(f"No pricing info for {provider}/{model}")
            return 0.0
        
        input_cost = (response.usage["prompt_tokens"] / 1000) * pricing[provider][model]["input"]
        output_cost = (response.usage["completion_tokens"] / 1000) * pricing[provider][model]["output"]
        
        return input_cost + output_cost


# Global orchestrator instance
_orchestrator = None


def get_llm_orchestrator() -> LLMOrchestrator:
    """Get the global LLM orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = LLMOrchestrator()
    return _orchestrator


def generate_text(
    prompt: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    **kwargs
) -> str:
    """
    Convenience function to generate text.
    
    Returns just the text content.
    """
    orchestrator = get_llm_orchestrator()
    response = orchestrator.generate(
        prompt=prompt,
        provider=provider,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )
    return response.text


def generate_with_context(
    prompt: str,
    context: Dict[str, Any],
    provider: Optional[str] = None,
    **kwargs
) -> LLMResponse:
    """
    Generate text with additional context.
    
    Automatically formats context into the prompt.
    """
    # Format context
    context_str = "\n".join([
        f"{key}: {value}"
        for key, value in context.items()
    ])
    
    full_prompt = f"""Context:
{context_str}

Request:
{prompt}
"""
    
    orchestrator = get_llm_orchestrator()
    return orchestrator.generate(
        prompt=full_prompt,
        provider=provider,
        **kwargs
    )
