from abc import ABC, abstractmethod
from dataclasses import dataclass


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
        )


class AzureOpenAIProvider(LLMProvider):
    def generate(self, request: LLMRequest) -> LLMResponse:
        # TODO: Implement Azure OpenAI integration in a later episode.
        # Requirements before enabling:
        # - load credentials through the configured secret provider, not frontend env
        # - log provider metadata without storing unnecessary sensitive text
        # - add timeout, retry, and Azure content-safety integration behaviour
        raise NotImplementedError("AzureOpenAIProvider is a placeholder and is not configured in the local MVP.")


def get_llm_provider(provider_name: str) -> LLMProvider:
    if provider_name == "mock":
        return LocalMockLLMProvider()
    if provider_name == "azure_openai":
        return AzureOpenAIProvider()
    raise ValueError(f"Unsupported LLM_PROVIDER: {provider_name}")
