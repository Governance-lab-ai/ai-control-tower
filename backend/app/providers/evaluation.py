import re
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.models.ai_system import AISystem


@dataclass(frozen=True)
class EvaluationRequest:
    ai_system: AISystem
    prompt: str
    input_text: str
    output_text: str
    retrieved_documents: list[str]
    threshold: int


@dataclass(frozen=True)
class EvaluationResult:
    provider: str
    evaluation_score: int
    relevance_score: int
    groundedness_score: int
    hallucination_flag: bool
    evaluation_summary: str
    requires_human_review: bool
    threshold: int


class EvaluationProvider(ABC):
    @abstractmethod
    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        raise NotImplementedError


class LocalEvaluationProvider(EvaluationProvider):
    provider_name = "local_heuristic"

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        relevance_score = self._relevance_score(request.prompt, request.input_text, request.output_text)
        groundedness_score = self._groundedness_score(request.output_text, request.retrieved_documents)
        hallucination_flag = self._hallucination_flag(request.output_text, groundedness_score, request.retrieved_documents)
        evaluation_score = round((relevance_score * 0.6) + (groundedness_score * 0.4))
        requires_human_review = evaluation_score < request.threshold or hallucination_flag

        reasons = [
            f"score {evaluation_score}/100",
            f"relevance {relevance_score}/100",
            f"groundedness {groundedness_score}/100",
            f"threshold {request.threshold}/100 for {request.ai_system.risk_level} risk",
        ]
        if hallucination_flag:
            reasons.append("hallucination signal detected")
        if requires_human_review:
            reasons.append("human review required")
        else:
            reasons.append("evaluation passed")

        return EvaluationResult(
            provider=self.provider_name,
            evaluation_score=evaluation_score,
            relevance_score=relevance_score,
            groundedness_score=groundedness_score,
            hallucination_flag=hallucination_flag,
            evaluation_summary="Local heuristic evaluation: " + "; ".join(reasons) + ".",
            requires_human_review=requires_human_review,
            threshold=request.threshold,
        )

    def _relevance_score(self, prompt: str, input_text: str, output_text: str) -> int:
        expected_terms = self._tokens(f"{prompt} {input_text}")
        output_terms = self._tokens(output_text)
        if not expected_terms or not output_terms:
            return 0
        overlap = expected_terms.intersection(output_terms)
        coverage = len(overlap) / len(expected_terms)
        return self._clamp_score(35 + round(coverage * 65))

    def _groundedness_score(self, output_text: str, retrieved_documents: list[str]) -> int:
        output_terms = self._tokens(output_text)
        if not output_terms:
            return 0
        if not retrieved_documents:
            return 75

        context_terms = self._tokens(" ".join(retrieved_documents))
        if not context_terms:
            return 50
        overlap = output_terms.intersection(context_terms)
        coverage = len(overlap) / min(len(output_terms), len(context_terms))
        score = 35 + round(coverage * 65)
        if "retrieved document" in output_text.lower():
            score = max(score, 70)
        return self._clamp_score(score)

    def _hallucination_flag(self, output_text: str, groundedness_score: int, retrieved_documents: list[str]) -> bool:
        lowered = output_text.lower()
        explicit_signals = (
            "unsupported claim",
            "not in the retrieved context",
            "not in the provided context",
            "cannot verify",
            "hallucinated",
        )
        if any(signal in lowered for signal in explicit_signals):
            return True
        return bool(retrieved_documents and groundedness_score < 40)

    def _tokens(self, text: str) -> set[str]:
        stop_words = {
            "and",
            "are",
            "for",
            "from",
            "has",
            "that",
            "the",
            "this",
            "using",
            "with",
        }
        return {token for token in re.findall(r"[a-z0-9]{3,}", text.lower()) if token not in stop_words}

    def _clamp_score(self, value: int) -> int:
        return max(0, min(100, value))


def get_evaluation_provider(provider_name: str) -> EvaluationProvider:
    if provider_name == "local":
        return LocalEvaluationProvider()
    raise ValueError(f"Unsupported EVALUATION_PROVIDER: {provider_name}")
