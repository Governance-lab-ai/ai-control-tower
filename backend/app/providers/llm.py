from abc import ABC, abstractmethod
from dataclasses import dataclass

import httpx

from app.core.config import Settings


@dataclass(frozen=True)
class LLMRequest:
    system_name: str
    prompt: str
    input_text: str
    retrieved_documents: list[str]
    metadata: dict


@dataclass(frozen=True)
class LLMResponse:
    output_text: str
    provider: str
    model: str
    model_version: str


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        raise NotImplementedError


class LocalMockLLMProvider(LLMProvider):
    def generate(self, request: LLMRequest) -> LLMResponse:
        context_note = f" using {len(request.retrieved_documents)} retrieved document(s)" if request.retrieved_documents else ""
        return LLMResponse(
            output_text=(
                f"[Local mock output] {request.system_name} processed the request{context_note}. "
                f"Input summary: {request.input_text[:180]}"
            ),
            provider="local_mock",
            model="mock-governance-gateway",
            model_version="local-mock-v1",
        )


class OllamaLLMProvider(LLMProvider):
    def __init__(self, settings: Settings) -> None:
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model
        self.timeout_seconds = settings.request_timeout_seconds

    def generate(self, request: LLMRequest) -> LLMResponse:
        prompt_parts = [
            f"System: {request.system_name}",
            f"Instruction: {request.prompt}",
            f"Input: {request.input_text}",
        ]
        if request.retrieved_documents:
            prompt_parts.append("Retrieved documents:")
            prompt_parts.extend(f"- {document}" for document in request.retrieved_documents)

        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": "\n".join(prompt_parts),
                    "stream": False,
                },
            )
            response.raise_for_status()
            payload = response.json()

        output_text = str(payload.get("response", "")).strip()
        if not output_text:
            raise RuntimeError("Ollama returned an empty response.")

        return LLMResponse(
            output_text=output_text,
            provider="ollama",
            model=self.model,
            model_version=str(payload.get("model", self.model)),
        )


class AzureOpenAIProvider(LLMProvider):
    def generate(self, request: LLMRequest) -> LLMResponse:
        # TODO: Implement Azure OpenAI integration in a later episode.
        # Requirements before enabling:
        # - load credentials through the configured secret provider, not frontend env
        # - log provider metadata without storing unnecessary sensitive text
        # - add timeout, retry, and Azure content-safety integration behaviour
        raise NotImplementedError("AzureOpenAIProvider is a placeholder and is not configured in the local MVP.")


def get_llm_provider(provider_name: str, settings: Settings | None = None) -> LLMProvider:
    if provider_name == "mock":
        return LocalMockLLMProvider()
    if provider_name == "ollama":
        if settings is None:
            raise ValueError("Ollama provider requires settings.")
        return OllamaLLMProvider(settings)
    if provider_name == "azure_openai":
        return AzureOpenAIProvider()
    raise ValueError(f"Unsupported LLM_PROVIDER: {provider_name}")
