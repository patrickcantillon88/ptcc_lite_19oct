"""
Gemini AI Client for PTCC
Provides AI-powered search and agent functionality with proper error handling and fallbacks.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

# Try to import Gemini - gracefully handle if not available
try:
    import google.generativeai as genai
    # RequestOptions may not be available in all versions
    try:
        from google.generativeai.types import RequestOptions
    except (ImportError, AttributeError):
        RequestOptions = None
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    RequestOptions = None
    GEMINI_AVAILABLE = False
    logging.warning("Google Generative AI not available - AI features will be disabled")

logger = logging.getLogger(__name__)

@dataclass
class GeminiConfig:
    """Configuration for Gemini API client."""
    api_key: str
    model: str = "gemini-2.5-flash-lite"
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 30

class GeminiClient:
    """Client wrapper for Google Gemini AI API with error handling and fallbacks."""

    def __init__(self, config: GeminiConfig):
        self.config = config
        self._client = None
        self._initialized = False
        self._initialize_client()

    def _initialize_client(self) -> bool:
        """Initialize the Gemini client with error handling."""
        if not GEMINI_AVAILABLE:
            logger.warning("Google Generative AI library not available - AI features will be disabled")
            return False

        try:
            if not self.config.api_key:
                logger.warning("Gemini API key not provided - AI features will be disabled")
                return False

            genai.configure(api_key=self.config.api_key)
            self._client = genai.GenerativeModel(self.config.model)
            self._initialized = True
            logger.info(f"Gemini client initialized with model: {self.config.model}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self._initialized = False
            return False

    def is_available(self) -> bool:
        """Check if Gemini client is available and functional."""
        return self._initialized and self._client is not None

    def generate_text(self, prompt: str, **kwargs) -> Optional[str]:
        """
        Generate text using Gemini API with fallback handling.

        Args:
            prompt: The text prompt to send to Gemini
            **kwargs: Additional parameters for generation

        Returns:
            Generated text or None if failed
        """
        if not GEMINI_AVAILABLE or not self.is_available():
            logger.warning("Gemini client not available - returning None")
            return None

        try:
            # Merge config defaults with provided kwargs
            generation_config = genai.types.GenerationConfig(
                temperature=kwargs.get('temperature', self.config.temperature),
                max_output_tokens=kwargs.get('max_tokens', self.config.max_tokens),
            )

            # Build generate_content call with optional request_options
            call_kwargs = {
                'generation_config': generation_config
            }
            
            if RequestOptions is not None:
                request_options = RequestOptions(timeout=kwargs.get('timeout', self.config.timeout))
                call_kwargs['request_options'] = request_options

            response = self._client.generate_content(prompt, **call_kwargs)

            if response and response.text:
                return response.text.strip()
            else:
                logger.warning("Gemini returned empty response")
                return None

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return None

    def analyze_query_intent(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Analyze search query intent using Gemini.

        Args:
            query: The search query to analyze

        Returns:
            Dictionary with intent analysis or None if failed
        """
        prompt = f"""
        Analyze the following search query and provide structured analysis:

        Query: "{query}"

        Please provide:
        1. Intent category (student_info, behavior_incident, academic_performance, schedule_timetable, communication, assessment, general_search)
        2. Key entities mentioned (student names, subjects, dates, etc.)
        3. Query type (factual, analytical, comparative, temporal)
        4. Suggested query expansions or related terms

        Format as JSON:
        {{
            "intent": "category",
            "entities": ["entity1", "entity2"],
            "query_type": "type",
            "expansions": ["expansion1", "expansion2"]
        }}
        """

        response = self.generate_text(prompt, temperature=0.3)
        if not response:
            return None

        try:
            # Simple JSON extraction (in production, use proper JSON parsing)
            import json
            # Clean the response to extract JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            logger.error(f"Failed to parse Gemini intent analysis: {e}")
            return None

    def rank_search_results(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Use Gemini to rank and score search results by relevance.

        Args:
            query: The original search query
            results: List of search result dictionaries

        Returns:
            Ranked results with AI relevance scores
        """
        if not results:
            return results

        # Limit to top 10 results for analysis to avoid token limits
        top_results = results[:10]

        results_text = "\n".join([
            f"Result {i+1}: {r.get('content', '')[:200]}..."
            for i, r in enumerate(top_results)
        ])

        prompt = f"""
        Given the search query: "{query}"

        Rank these search results by relevance (1 = most relevant, {len(top_results)} = least relevant):

        {results_text}

        Provide rankings as a JSON array of indices (0-based) in order of relevance:
        [0, 2, 1, ...]
        """

        response = self.generate_text(prompt, temperature=0.1, max_tokens=512)
        if not response:
            # Return original results if AI ranking fails
            return results

        try:
            import json
            start = response.find('[')
            end = response.rfind(']') + 1
            if start != -1 and end != -1:
                ranking_str = response[start:end]
                ranking = json.loads(ranking_str)

                if len(ranking) == len(top_results):
                    # Reorder results based on AI ranking
                    ranked_results = [top_results[i] for i in ranking]
                    # Add AI score metadata
                    for i, result in enumerate(ranked_results):
                        result['ai_relevance_score'] = len(ranked_results) - i  # Higher score for more relevant
                    return ranked_results + results[10:]  # Add back any remaining results
        except Exception as e:
            logger.error(f"Failed to parse Gemini ranking: {e}")

        # Return original results if ranking fails
        return results

    def generate_agent_response(self, agent_type: str, context: Dict[str, Any], query: str) -> Optional[str]:
        """
        Generate AI-powered agent response for teacher tools.

        Args:
            agent_type: Type of agent (at-risk-identifier, behavior-manager, learning-path-creator)
            context: Context data about the student/situation
            query: The user's query or request

        Returns:
            AI-generated response or None if failed
        """
        context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])

        prompts = {
            "at-risk-identifier": f"""
            You are an AI assistant helping teachers identify at-risk students at BIS HCMC.

            Student Context:
            {context_str}

            Teacher Query: {query}

            Provide a comprehensive analysis including:
            1. Risk assessment (Low/Medium/High risk)
            2. Key indicators from the data
            3. Recommended interventions
            4. Suggested monitoring actions

            Be specific, actionable, and supportive.
            """,

            "behavior-manager": f"""
            You are an AI assistant helping teachers manage student behavior at BIS HCMC.

            Student Context:
            {context_str}

            Teacher Query: {query}

            Provide analysis including:
            1. Behavior pattern assessment
            2. Root cause analysis
            3. Intervention strategies
            4. Prevention recommendations

            Focus on positive behavior support and de-escalation techniques.
            """,

            "learning-path-creator": f"""
            You are an AI assistant helping teachers create personalized learning paths at BIS HCMC.

            Student Context:
            {context_str}

            Teacher Query: {query}

            Provide recommendations including:
            1. Current learning level assessment
            2. Personalized learning objectives
            3. Recommended activities and resources
            4. Progress monitoring suggestions

            Ensure recommendations are differentiated and inclusive.
            """
        }

        prompt = prompts.get(agent_type)
        if not prompt:
            logger.error(f"Unknown agent type: {agent_type}")
            return None

        return self.generate_text(prompt, temperature=0.7, max_tokens=1024)

def create_gemini_client_from_config(config_dict: Dict[str, Any]) -> GeminiClient:
    """
    Factory function to create Gemini client from configuration dictionary.

    Args:
        config_dict: Configuration dictionary with Gemini settings

    Returns:
        Configured GeminiClient instance
    """
    gemini_config = config_dict.get('llm', {}).get('gemini', {})

    # Get API key from config or environment
    api_key = gemini_config.get('api_key') or os.getenv('GEMINI_API_KEY', '')

    config = GeminiConfig(
        api_key=api_key,
        model=gemini_config.get('model', 'gemini-2.0-flash-exp'),
        temperature=gemini_config.get('temperature', 0.7),
        max_tokens=gemini_config.get('max_tokens', 2048),
        timeout=gemini_config.get('timeout', 30)
    )

    return GeminiClient(config)