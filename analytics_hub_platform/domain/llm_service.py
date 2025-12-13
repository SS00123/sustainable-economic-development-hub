"""
LLM Service Module
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module provides LLM-based recommendation generation
using OpenAI or Anthropic APIs with robust error handling.
"""

import os
import json
import hashlib
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

try:
    import openai
    from openai import OpenAIError, APITimeoutError, APIConnectionError, RateLimitError
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    OpenAIError = Exception  # type: ignore
    APITimeoutError = Exception  # type: ignore
    APIConnectionError = Exception  # type: ignore
    RateLimitError = Exception  # type: ignore

try:
    import anthropic
    from anthropic import APIError, APITimeoutError as AnthropicTimeoutError
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    APIError = Exception  # type: ignore
    AnthropicTimeoutError = Exception  # type: ignore

from analytics_hub_platform.infrastructure.settings import get_settings
from analytics_hub_platform.infrastructure.caching import get_cache_manager

logger = logging.getLogger(__name__)


@dataclass
class Recommendation:
    """A single strategic recommendation."""
    id: str
    title: str
    description: str
    priority: str  # high, medium, low
    category: str  # economic, environmental, social, governance
    impact: str
    timeline: str
    kpis_affected: List[str]


@dataclass
class LLMResponse:
    """Container for LLM response."""
    executive_summary: str
    key_insights: List[str]
    recommendations: List[Recommendation]
    risk_alerts: List[str]
    provider: str
    model: str
    generated_at: datetime


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate_recommendations(
        self,
        kpi_data: Dict[str, Any],
        anomalies: List[Dict[str, Any]],
        forecasts: List[Dict[str, Any]],
        language: str = "en",
    ) -> LLMResponse:
        pass
    
    def _build_system_prompt(self, language: str) -> str:
        """Build the system prompt for recommendation generation."""
        if language == "ar":
            return """أنت مستشار اقتصادي خبير لوزارة الاقتصاد والتخطيط في المملكة العربية السعودية.
مهمتك هي تحليل بيانات مؤشرات الأداء الرئيسية وتقديم توصيات استراتيجية تتماشى مع رؤية 2030.

قدم ردك بتنسيق JSON مع الهيكل التالي:
{
    "executive_summary": "ملخص تنفيذي موجز",
    "key_insights": ["رؤية 1", "رؤية 2", ...],
    "recommendations": [
        {
            "id": "rec_1",
            "title": "عنوان التوصية",
            "description": "وصف مفصل",
            "priority": "high/medium/low",
            "category": "economic/environmental/social/governance",
            "impact": "التأثير المتوقع",
            "timeline": "الجدول الزمني",
            "kpis_affected": ["kpi_1", "kpi_2"]
        }
    ],
    "risk_alerts": ["تنبيه 1", "تنبيه 2", ...]
}"""
        else:
            return """You are an expert economic advisor for the Ministry of Economy and Planning, Kingdom of Saudi Arabia.
Your task is to analyze KPI data and provide strategic recommendations aligned with Vision 2030.

Provide your response in JSON format with the following structure:
{
    "executive_summary": "Brief executive summary",
    "key_insights": ["insight 1", "insight 2", ...],
    "recommendations": [
        {
            "id": "rec_1",
            "title": "Recommendation title",
            "description": "Detailed description",
            "priority": "high/medium/low",
            "category": "economic/environmental/social/governance",
            "impact": "Expected impact",
            "timeline": "Implementation timeline",
            "kpis_affected": ["kpi_1", "kpi_2"]
        }
    ],
    "risk_alerts": ["alert 1", "alert 2", ...]
}"""
    
    def _build_user_prompt(
        self,
        kpi_data: Dict[str, Any],
        anomalies: List[Dict[str, Any]],
        forecasts: List[Dict[str, Any]],
        language: str,
    ) -> str:
        """Build the user prompt with context data."""
        if language == "ar":
            prompt = "حلل البيانات التالية وقدم توصيات استراتيجية:\n\n"
        else:
            prompt = "Analyze the following data and provide strategic recommendations:\n\n"
        
        prompt += f"## KPI Data\n{json.dumps(kpi_data, indent=2, default=str)}\n\n"
        
        if anomalies:
            prompt += f"## Detected Anomalies\n{json.dumps(anomalies, indent=2, default=str)}\n\n"
        
        if forecasts:
            prompt += f"## Forecasts\n{json.dumps(forecasts, indent=2, default=str)}\n\n"
        
        return prompt
    
    def _parse_response(self, content: str, provider: str, model: str) -> LLMResponse:
        """Parse LLM response into structured format."""
        try:
            # Try to extract JSON from response
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0]
            else:
                json_str = content
            
            data = json.loads(json_str.strip())
            
            recommendations = []
            for rec in data.get("recommendations", []):
                recommendations.append(Recommendation(
                    id=rec.get("id", f"rec_{len(recommendations)}"),
                    title=rec.get("title", ""),
                    description=rec.get("description", ""),
                    priority=rec.get("priority", "medium"),
                    category=rec.get("category", "economic"),
                    impact=rec.get("impact", ""),
                    timeline=rec.get("timeline", ""),
                    kpis_affected=rec.get("kpis_affected", []),
                ))
            
            return LLMResponse(
                executive_summary=data.get("executive_summary", ""),
                key_insights=data.get("key_insights", []),
                recommendations=recommendations,
                risk_alerts=data.get("risk_alerts", []),
                provider=provider,
                model=model,
                generated_at=datetime.now(),
            )
        except Exception as e:
            # Return a basic response if parsing fails
            return LLMResponse(
                executive_summary=content[:500] if content else "Analysis unavailable",
                key_insights=["Unable to parse structured insights"],
                recommendations=[],
                risk_alerts=[f"Response parsing error: {str(e)}"],
                provider=provider,
                model=model,
                generated_at=datetime.now(),
            )


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI GPT provider with robust error handling.
    
    Features:
    - Timeout configuration
    - Retry on rate limits
    - Graceful fallback on errors
    - Response caching
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 2
    ):
        settings = get_settings()
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or settings.llm_api_key
        self.model = model or os.environ.get("OPENAI_MODEL") or settings.llm_model_name or "gpt-4"
        self.timeout = timeout
        self.max_retries = max_retries
        
        if self.api_key and HAS_OPENAI:
            self.client = openai.OpenAI(
                api_key=self.api_key,
                timeout=self.timeout,
                max_retries=self.max_retries
            )
        else:
            self.client = None
    
    def generate_recommendations(
        self,
        kpi_data: Dict[str, Any],
        anomalies: List[Dict[str, Any]],
        forecasts: List[Dict[str, Any]],
        language: str = "en",
    ) -> LLMResponse:
        """Generate recommendations with error handling and fallback."""
        if not self.client:
            logger.warning("OpenAI client not initialized, falling back to mock provider")
            return self._fallback_response(language)
        
        try:
            # Check cache first
            cache_key = self._get_cache_key(kpi_data, anomalies, forecasts, language)
            cache_manager = get_cache_manager()
            cached = cache_manager.get(cache_key)
            
            if cached:
                logger.info("Returning cached LLM response")
                return cached
            
            # Make API call with timeout
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._build_system_prompt(language)},
                    {"role": "user", "content": self._build_user_prompt(kpi_data, anomalies, forecasts, language)},
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            
            content = response.choices[0].message.content
            result = self._parse_response(content, "openai", self.model)
            
            # Cache successful response
            cache_manager.set(cache_key, result, ttl=3600)  # 1 hour
            
            return result
            
        except APITimeoutError:
            logger.error("OpenAI API timeout, falling back")
            return self._fallback_response(language, error="API timeout")
        
        except APIConnectionError:
            logger.error("OpenAI API connection error, falling back")
            return self._fallback_response(language, error="Connection error")
        
        except RateLimitError:
            logger.error("OpenAI rate limit exceeded, falling back")
            return self._fallback_response(language, error="Rate limit exceeded")
        
        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}, falling back")
            return self._fallback_response(language, error=str(e))
        
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI provider: {str(e)}, falling back")
            return self._fallback_response(language, error=str(e))
    
    def _get_cache_key(
        self,
        kpi_data: Dict[str, Any],
        anomalies: List[Dict[str, Any]],
        forecasts: List[Dict[str, Any]],
        language: str
    ) -> str:
        """Generate cache key for request."""
        data_str = json.dumps({
            "kpi": kpi_data,
            "anomalies": anomalies,
            "forecasts": forecasts,
            "language": language,
            "provider": "openai",
            "model": self.model
        }, sort_keys=True, default=str)
        return f"llm_recommendations_{hashlib.md5(data_str.encode()).hexdigest()}"
    
    def _fallback_response(self, language: str, error: Optional[str] = None) -> LLMResponse:
        """Generate fallback response when API fails."""
        logger.info(f"Generating fallback response (error: {error})")
        mock_provider = MockLLMProvider()
        response = mock_provider.generate_recommendations({}, [], [], language)
        
        # Add error notice to summary
        error_msg = f" [Note: Using template-based analysis due to: {error}]" if error else ""
        response.executive_summary = response.executive_summary + error_msg
        response.provider = "openai_fallback"
        
        return response


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic Claude provider with robust error handling.
    
    Features:
    - Timeout configuration
    - Retry on rate limits
    - Graceful fallback on errors
    - Response caching
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 2
    ):
        settings = get_settings()
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY") or settings.llm_api_key
        self.model = model or os.environ.get("ANTHROPIC_MODEL") or settings.llm_model_name or "claude-3-sonnet-20240229"
        self.timeout = timeout
        self.max_retries = max_retries
        
        if self.api_key and HAS_ANTHROPIC:
            self.client = anthropic.Anthropic(
                api_key=self.api_key,
                timeout=self.timeout,
                max_retries=self.max_retries
            )
        else:
            self.client = None
    
    def generate_recommendations(
        self,
        kpi_data: Dict[str, Any],
        anomalies: List[Dict[str, Any]],
        forecasts: List[Dict[str, Any]],
        language: str = "en",
    ) -> LLMResponse:
        """Generate recommendations with error handling and fallback."""
        if not self.client:
            logger.warning("Anthropic client not initialized, falling back to mock provider")
            return self._fallback_response(language)
        
        try:
            # Check cache first
            cache_key = self._get_cache_key(kpi_data, anomalies, forecasts, language)
            cache_manager = get_cache_manager()
            cached = cache_manager.get(cache_key)
            
            if cached:
                logger.info("Returning cached LLM response")
                return cached
            
            # Make API call with timeout
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=self._build_system_prompt(language),
                messages=[
                    {"role": "user", "content": self._build_user_prompt(kpi_data, anomalies, forecasts, language)},
                ],
            )
            
            content = response.content[0].text
            result = self._parse_response(content, "anthropic", self.model)
            
            # Cache successful response
            cache_manager.set(cache_key, result, ttl=3600)  # 1 hour
            
            return result
            
        except AnthropicTimeoutError:
            logger.error("Anthropic API timeout, falling back")
            return self._fallback_response(language, error="API timeout")
        
        except APIError as e:
            logger.error(f"Anthropic API error: {str(e)}, falling back")
            return self._fallback_response(language, error=str(e))
        
        except Exception as e:
            logger.error(f"Unexpected error in Anthropic provider: {str(e)}, falling back")
            return self._fallback_response(language, error=str(e))
    
    def _get_cache_key(
        self,
        kpi_data: Dict[str, Any],
        anomalies: List[Dict[str, Any]],
        forecasts: List[Dict[str, Any]],
        language: str
    ) -> str:
        """Generate cache key for request."""
        data_str = json.dumps({
            "kpi": kpi_data,
            "anomalies": anomalies,
            "forecasts": forecasts,
            "language": language,
            "provider": "anthropic",
            "model": self.model
        }, sort_keys=True, default=str)
        return f"llm_recommendations_{hashlib.md5(data_str.encode()).hexdigest()}"
    
    def _fallback_response(self, language: str, error: Optional[str] = None) -> LLMResponse:
        """Generate fallback response when API fails."""
        logger.info(f"Generating fallback response (error: {error})")
        mock_provider = MockLLMProvider()
        response = mock_provider.generate_recommendations({}, [], [], language)
        
        # Add error notice to summary
        error_msg = f" [Note: Using template-based analysis due to: {error}]" if error else ""
        response.executive_summary = response.executive_summary + error_msg
        response.provider = "anthropic_fallback"
        
        return response


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider for development/testing."""
    
    def generate_recommendations(
        self,
        kpi_data: Dict[str, Any],
        anomalies: List[Dict[str, Any]],
        forecasts: List[Dict[str, Any]],
        language: str = "en",
    ) -> LLMResponse:
        if language == "ar":
            return LLMResponse(
                executive_summary="تُظهر مؤشرات الأداء الرئيسية تقدماً إيجابياً نحو أهداف رؤية 2030، مع وجود مجالات تحتاج إلى اهتمام.",
                key_insights=[
                    "نمو الناتج المحلي الإجمالي غير النفطي يتجاوز التوقعات",
                    "مؤشرات التوظيف تُظهر تحسناً مستمراً",
                    "استثمارات الطاقة المتجددة تتسارع",
                ],
                recommendations=[
                    Recommendation(
                        id="rec_1",
                        title="تعزيز التنويع الاقتصادي",
                        description="التركيز على قطاعات السياحة والترفيه والتقنية",
                        priority="high",
                        category="economic",
                        impact="زيادة مساهمة القطاع غير النفطي بنسبة 5%",
                        timeline="12-18 شهراً",
                        kpis_affected=["non_oil_gdp", "private_sector_share"],
                    ),
                ],
                risk_alerts=["مراقبة تقلبات أسعار النفط العالمية"],
                provider="mock",
                model="mock-v1",
                generated_at=datetime.now(),
            )
        else:
            return LLMResponse(
                executive_summary="KPIs show positive progress toward Vision 2030 goals, with some areas requiring attention.",
                key_insights=[
                    "Non-oil GDP growth exceeds expectations",
                    "Employment indicators show steady improvement",
                    "Renewable energy investments accelerating",
                ],
                recommendations=[
                    Recommendation(
                        id="rec_1",
                        title="Accelerate Economic Diversification",
                        description="Focus on tourism, entertainment, and technology sectors to reduce oil dependency",
                        priority="high",
                        category="economic",
                        impact="Increase non-oil sector contribution by 5%",
                        timeline="12-18 months",
                        kpis_affected=["non_oil_gdp", "private_sector_share"],
                    ),
                    Recommendation(
                        id="rec_2",
                        title="Strengthen Green Economy Initiatives",
                        description="Expand renewable energy projects and carbon reduction programs",
                        priority="medium",
                        category="environmental",
                        impact="Reduce carbon intensity by 10%",
                        timeline="24 months",
                        kpis_affected=["renewable_energy_share", "carbon_intensity"],
                    ),
                ],
                risk_alerts=[
                    "Monitor global oil price volatility",
                    "Address regional employment disparities",
                ],
                provider="mock",
                model="mock-v1",
                generated_at=datetime.now(),
            )


def get_llm_service(provider: Optional[str] = None) -> BaseLLMProvider:
    """
    Get the appropriate LLM provider with configuration from settings.
    
    Args:
        provider: Provider name ("openai", "anthropic", "mock", or "auto").
                 If None, uses setting from environment.
        
    Returns:
        LLM provider instance
        
    Example:
        # Auto-detect from environment/settings
        llm = get_llm_service()
        
        # Force specific provider
        llm = get_llm_service("openai")
        
        # Mock for development
        llm = get_llm_service("mock")
    """
    settings = get_settings()
    provider = provider or settings.llm_provider
    
    if provider == "auto":
        # Auto-detect: try OpenAI, then Anthropic, then fallback to Mock
        if (os.environ.get("OPENAI_API_KEY") or settings.llm_api_key) and HAS_OPENAI:
            logger.info("Auto-detected OpenAI provider")
            return OpenAIProvider(
                timeout=settings.llm_timeout,
                max_retries=settings.llm_max_retries
            )
        elif os.environ.get("ANTHROPIC_API_KEY") and HAS_ANTHROPIC:
            logger.info("Auto-detected Anthropic provider")
            return AnthropicProvider(
                timeout=settings.llm_timeout,
                max_retries=settings.llm_max_retries
            )
        else:
            logger.info("No LLM API keys found, using mock provider")
            return MockLLMProvider()
    
    elif provider == "openai":
        return OpenAIProvider(
            timeout=settings.llm_timeout,
            max_retries=settings.llm_max_retries
        )
    
    elif provider == "anthropic":
        return AnthropicProvider(
            timeout=settings.llm_timeout,
            max_retries=settings.llm_max_retries
        )
    
    else:
        return MockLLMProvider()


def generate_recommendations(
    kpi_data: Dict[str, Any],
    anomalies: Optional[List[Dict[str, Any]]] = None,
    forecasts: Optional[List[Dict[str, Any]]] = None,
    language: str = "en",
    provider: str = "auto",
) -> Dict[str, Any]:
    """
    High-level function to generate LLM recommendations.
    
    Args:
        kpi_data: Dictionary of KPI data
        anomalies: List of detected anomalies
        forecasts: List of forecast results
        language: Response language ("en" or "ar")
        provider: LLM provider to use
        
    Returns:
        Dictionary with recommendations
    """
    llm = get_llm_service(provider)
    response = llm.generate_recommendations(
        kpi_data=kpi_data,
        anomalies=anomalies or [],
        forecasts=forecasts or [],
        language=language,
    )
    
    return {
        "executive_summary": response.executive_summary,
        "key_insights": response.key_insights,
        "recommendations": [asdict(r) for r in response.recommendations],
        "risk_alerts": response.risk_alerts,
        "provider": response.provider,
        "model": response.model,
        "generated_at": response.generated_at.isoformat(),
    }
