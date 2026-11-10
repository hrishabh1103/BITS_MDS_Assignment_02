"""LLM Provider abstraction layer for Retrieval-Augmented Generation (RAG).

Supports local Ollama instances, OpenAI-compatible APIs (OpenAI, Gemini, Groq, vLLM),
and a deterministic Mock provider for offline testing and continuous integration.
Strictly manages API credentials without committing or logging secrets.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import os
import re
import time
from typing import Any, Dict, List, Optional
import requests

from src.config import (
    EXTERNAL_API_BASE_URL,
    EXTERNAL_API_KEY,
    EXTERNAL_MODEL_NAME,
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)
from src.utils import setup_logger

logger = setup_logger("llm_provider")


@dataclass
class LLMResponse:
    """Standardized response container across all LLM backends."""
    content: str
    model_name: str
    provider_name: str
    generation_mode: str  # 'real' or 'mock'
    latency_ms: float
    tokens_used: Dict[str, int] = field(default_factory=dict)
    error: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.error is None and bool(self.content.strip())


class BaseLLMProvider(ABC):
    """Abstract base class for all language model providers."""

    def __init__(self, model_name: str):
        self.model_name = model_name

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier string."""
        pass

    @property
    @abstractmethod
    def generation_mode(self) -> str:
        """Indicates whether provider executes real or mock generation."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Checks whether the provider is currently reachable and configured."""
        pass

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Generates a text completion for the provided prompt."""
        pass


class OllamaProvider(BaseLLMProvider):
    """Connects to a locally running Ollama daemon."""

    def __init__(
        self,
        model_name: str = OLLAMA_MODEL,
        base_url: str = OLLAMA_BASE_URL,
        timeout_seconds: int = 180,
    ):
        super().__init__(model_name=model_name)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout_seconds

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def generation_mode(self) -> str:
        return "real"

    def is_available(self) -> bool:
        """Pings Ollama /api/tags to verify connectivity and model existence."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                # Check exact or prefix match (e.g. 'llama3.2:latest' vs 'llama3.2')
                base_target = self.model_name.split(":")[0]
                has_model = any(self.model_name in m or base_target in m for m in models)
                if not has_model and models:
                    logger.warning(
                        f"Ollama running but target model '{self.model_name}' not downloaded. "
                        f"Available: {models}"
                    )
                return has_model
            return False
        except Exception as e:
            logger.debug(f"Ollama availability check failed: {e}")
            return False

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        endpoint = f"{self.base_url}/api/chat"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        t0 = time.perf_counter()
        try:
            logger.info(f"Dispatching query to Ollama ('{self.model_name}')...")
            resp = requests.post(endpoint, json=payload, timeout=self.timeout)
            latency_ms = (time.perf_counter() - t0) * 1000.0

            if resp.status_code != 200:
                err_msg = f"Ollama HTTP {resp.status_code}: {resp.text}"
                logger.error(err_msg)
                return LLMResponse(
                    content="",
                    model_name=self.model_name,
                    provider_name=self.name,
                    generation_mode=self.generation_mode,
                    latency_ms=latency_ms,
                    error=err_msg,
                )

            data = resp.json()
            reply = data.get("message", {}).get("content", "").strip()
            prompt_eval_count = data.get("prompt_eval_count", 0)
            eval_count = data.get("eval_count", 0)

            return LLMResponse(
                content=reply,
                model_name=self.model_name,
                provider_name=self.name,
                generation_mode=self.generation_mode,
                latency_ms=round(latency_ms, 2),
                tokens_used={
                    "prompt_tokens": prompt_eval_count,
                    "completion_tokens": eval_count,
                    "total_tokens": prompt_eval_count + eval_count,
                },
            )
        except requests.exceptions.RequestException as e:
            latency_ms = (time.perf_counter() - t0) * 1000.0
            err_msg = f"Ollama connection error: {str(e)}"
            logger.error(err_msg)
            return LLMResponse(
                content="",
                model_name=self.model_name,
                provider_name=self.name,
                generation_mode=self.generation_mode,
                latency_ms=latency_ms,
                error=err_msg,
            )


class OpenAICompatibleProvider(BaseLLMProvider):
    """Connects to any standard OpenAI-compatible completions endpoint."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout_seconds: int = 180,
    ):
        model = model_name or EXTERNAL_MODEL_NAME or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        super().__init__(model_name=model)
        self.api_key = api_key or EXTERNAL_API_KEY or os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY") or ""
        self.base_url = (base_url or EXTERNAL_API_BASE_URL or "https://api.openai.com/v1").rstrip("/")
        self.timeout = timeout_seconds

    @property
    def name(self) -> str:
        return "openai_compatible"

    @property
    def generation_mode(self) -> str:
        return "real"

    def is_available(self) -> bool:
        """Verifies API key is set without exposing its value."""
        return bool(self.api_key and self.api_key.strip())

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        if not self.is_available():
            return LLMResponse(
                content="",
                model_name=self.model_name,
                provider_name=self.name,
                generation_mode=self.generation_mode,
                latency_ms=0.0,
                error="API key not configured in environment variables (EXTERNAL_API_KEY/OPENAI_API_KEY).",
            )

        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        t0 = time.perf_counter()
        try:
            logger.info(f"Dispatching query to API provider ('{self.model_name}')...")
            resp = requests.post(endpoint, json=payload, headers=headers, timeout=self.timeout)
            latency_ms = (time.perf_counter() - t0) * 1000.0

            if resp.status_code != 200:
                err_msg = f"API HTTP {resp.status_code}: {resp.text[:300]}"
                logger.error(f"API generation error: HTTP {resp.status_code}")
                return LLMResponse(
                    content="",
                    model_name=self.model_name,
                    provider_name=self.name,
                    generation_mode=self.generation_mode,
                    latency_ms=latency_ms,
                    error=err_msg,
                )

            data = resp.json()
            reply = data["choices"][0]["message"]["content"].strip()
            usage = data.get("usage", {})

            return LLMResponse(
                content=reply,
                model_name=self.model_name,
                provider_name=self.name,
                generation_mode=self.generation_mode,
                latency_ms=round(latency_ms, 2),
                tokens_used={
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                },
            )
        except requests.exceptions.RequestException as e:
            latency_ms = (time.perf_counter() - t0) * 1000.0
            err_msg = f"API connection error: {str(e)}"
            logger.error(err_msg)
            return LLMResponse(
                content="",
                model_name=self.model_name,
                provider_name=self.name,
                generation_mode=self.generation_mode,
                latency_ms=latency_ms,
                error=err_msg,
            )


class MockLLMProvider(BaseLLMProvider):
    """Deterministic, offline test provider for CI validation and grading verification.

    Extracts keywords and record IDs from the formatted prompt and generates a
    rigorously grounded mock response. Explicitly flags generation_mode='mock'.
    """

    def __init__(self, model_name: str = "mock-automotive-expert:v1"):
        super().__init__(model_name=model_name)

    @property
    def name(self) -> str:
        return "mock"

    @property
    def generation_mode(self) -> str:
        return "mock"

    def is_available(self) -> bool:
        return True

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        t0 = time.perf_counter()

        # Parse retrieved record IDs from context block [RECORD: VTR-XXXXX] or Record ID: VTR-XXXXX
        retrieved_ids = re.findall(r"VTR-[A-Z0-9]+", prompt)
        unique_retrieved_ids = list(dict.fromkeys(retrieved_ids))

        # Check if this is a No-Context Baseline prompt
        is_baseline = "NO RETRIEVED CONTEXT AVAILABLE" in prompt or "No retrieved records provided" in prompt or not unique_retrieved_ids

        if is_baseline:
            # Baseline response: generic automotive advice, zero VTR- citations, lacks specific DTC codes
            content = (
                "### 1. Problem Summary\n"
                "The vehicle reports operational symptoms that may originate from multiple potential automotive systems.\n\n"
                "### 2. General Automotive Causes (Unassisted Baseline)\n"
                "- Potential electrical, mechanical, or sensor malfunctions.\n"
                "- Possible battery discharge, fuel delivery, or ignition coil issues.\n"
                "- General wear and tear or fluid contamination.\n\n"
                "### 3. General Diagnostic Recommendations\n"
                "- Perform an OBD-II diagnostic scan using a generic handheld tool.\n"
                "- Visually inspect wiring harnesses and fluid levels.\n"
                "- Consult a service repair manual for vehicle-specific wiring diagrams.\n\n"
                "### 4. Limitations & Missing Data\n"
                "- Notice: This answer is generated without retrieved troubleshooting database records.\n"
                "- Specific fault codes, confirmed root causes, and step-by-step factory repair actions are unavailable.\n\n"
                "### 5. Safety Disclaimer\n"
                "Professional workshop inspection by an ASE-certified automotive technician is strongly recommended before attempting component repairs."
            )
        else:
            # RAG response: Grounded strictly in retrieved records with explicit citations
            primary_id = unique_retrieved_ids[0]
            supporting_ids = unique_retrieved_ids[1:4]
            citations_str = ", ".join([f"[{rid}]" for rid in unique_retrieved_ids[:3]])

            # Extract sample causes/steps from prompt if available
            causes = []
            for match in re.finditer(r"Possible Causes:\s*([^\n]+)", prompt):
                causes.extend([c.strip() for c in match.group(1).split(";") if c.strip()])
            top_causes = causes[:3] if causes else ["Sensor circuit malfunction", "Component mechanical failure"]

            causes_bullets = "\n".join([f"- {c} (supported by {citations_str})" for c in top_causes])

            content = (
                "### 1. Problem Summary\n"
                f"The reported vehicle symptoms correlate with diagnostic records indexed in the troubleshooting knowledge base. "
                f"Primary matching diagnostic fault is identified under {primary_id}.\n\n"
                "### 2. Possible Causes (Supported by Retrieved Knowledge)\n"
                f"{causes_bullets}\n\n"
                "### 3. Diagnostic & Inspection Checks Supported by Context\n"
                f"1. Connect an OBD-II scanner and verify active Diagnostic Trouble Codes referenced in {citations_str}.\n"
                f"2. Inspect wiring harnesses and harness connectors for pin corrosion, loose terminals, or chafing as documented in [{primary_id}].\n"
                f"3. Verify reference voltages and component ground integrity against factory service specifications.\n"
                f"4. Do NOT replace components solely because a diagnostic code is present; verify electrical continuity first.\n\n"
                "### 4. Limitations & Safety Precautions\n"
                "- Retrieved records represent diagnostic possibilities and do not replace physical vehicle inspection.\n"
                "- For safety-critical systems (braking hydraulics, SRS airbags, high-voltage battery interlocks), professional diagnosis by an ASE-certified technician is required.\n\n"
                "### 5. Source Record Citations\n"
                f"Retrieved diagnostic records cited: {citations_str}"
            )

        latency_ms = (time.perf_counter() - t0) * 1000.0
        return LLMResponse(
            content=content,
            model_name=self.model_name,
            provider_name=self.name,
            generation_mode=self.generation_mode,
            latency_ms=round(latency_ms, 2),
            tokens_used={
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(content.split()),
                "total_tokens": len(prompt.split()) + len(content.split()),
            },
        )


def get_llm_provider(
    provider_name: Optional[str] = None,
    allow_mock_fallback: bool = True,
) -> BaseLLMProvider:
    """Factory function that returns the configured LLM provider.

    Resolution order:
    1. Explicit provider_name if provided ('ollama', 'openai', 'external', 'mock').
    2. Environment variable LLM_PROVIDER ('ollama' or 'external').
    3. If configured real provider is unavailable and allow_mock_fallback is True,
       falls back to MockLLMProvider with an informative warning log.
    """
    target = (provider_name or LLM_PROVIDER or "ollama").lower()

    if target in ("openai", "external", "openai_compatible"):
        provider = OpenAICompatibleProvider()
        if provider.is_available():
            logger.info("Using configured OpenAI-compatible external API provider.")
            return provider
        logger.warning("OpenAI-compatible API key not configured or unavailable.")

    elif target == "ollama":
        provider = OllamaProvider()
        if provider.is_available():
            logger.info(f"Using local Ollama provider at '{provider.base_url}' ('{provider.model_name}').")
            return provider
        logger.warning(f"Local Ollama provider at '{provider.base_url}' is not running or model '{provider.model_name}' is not pulled.")

    elif target == "mock":
        logger.info("Explicit mock LLM provider requested.")
        return MockLLMProvider()

    # Fallback resolution
    if allow_mock_fallback:
        logger.warning(
            "No active real LLM service reached. Falling back to deterministic MockLLMProvider for offline testing and CI. "
            "To enable live inference, run 'ollama pull llama3.2' or set EXTERNAL_API_KEY in .env."
        )
        return MockLLMProvider()

    raise RuntimeError(
        f"Configured LLM provider '{target}' is unavailable. "
        "Ensure Ollama daemon is active or valid API credentials are set in .env."
    )
