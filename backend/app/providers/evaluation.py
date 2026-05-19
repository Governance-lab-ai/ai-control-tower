import re
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass

import httpx

from app.core.config import Settings
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


class SemanticLocalEvaluationProvider(LocalEvaluationProvider):
    provider_name = "semantic_local_heuristic"

    synonym_groups = (
        {"client", "customer", "user", "prospect"},
        {"refund", "reimburse", "repay", "credit"},
        {"shipment", "shipping", "delivery", "order"},
        {"summarise", "summarize", "summary", "brief"},
        {"policy", "procedure", "guidance", "rule"},
        {"review", "oversight", "approval", "escalate"},
    )

    def _relevance_score(self, prompt: str, input_text: str, output_text: str) -> int:
        expected_terms = self._expanded_tokens(f"{prompt} {input_text}")
        output_terms = self._expanded_tokens(output_text)
        if not expected_terms or not output_terms:
            return 0
        overlap = expected_terms.intersection(output_terms)
        precision = len(overlap) / len(output_terms)
        recall = len(overlap) / len(expected_terms)
        f_score = (2 * precision * recall / (precision + recall)) if precision + recall else 0
        phrase_bonus = self._phrase_bonus(f"{prompt} {input_text}", output_text)
        return self._clamp_score(30 + round(f_score * 60) + phrase_bonus)

    def _groundedness_score(self, output_text: str, retrieved_documents: list[str]) -> int:
        if not output_text:
            return 0
        if not retrieved_documents:
            return 65

        context = " ".join(retrieved_documents)
        output_terms = self._expanded_tokens(output_text)
        context_terms = self._expanded_tokens(context)
        if not output_terms or not context_terms:
            return 40

        overlap = output_terms.intersection(context_terms)
        support_ratio = len(overlap) / len(output_terms)
        sentence_scores = [self._sentence_support_score(sentence, context_terms) for sentence in self._sentences(output_text)]
        weakest_claim = min(sentence_scores) if sentence_scores else 50
        number_penalty = 20 if self._has_unsupported_numbers(output_text, context) else 0
        return self._clamp_score(round((support_ratio * 55) + (weakest_claim * 0.45)) + 20 - number_penalty)

    def _hallucination_flag(self, output_text: str, groundedness_score: int, retrieved_documents: list[str]) -> bool:
        if super()._hallucination_flag(output_text, groundedness_score, retrieved_documents):
            return True
        if not retrieved_documents:
            return False
        context = " ".join(retrieved_documents)
        context_terms = self._expanded_tokens(context)
        unsupported_sentences = [
            sentence
            for sentence in self._sentences(output_text)
            if self._sentence_support_score(sentence, context_terms) < 35
        ]
        return len(unsupported_sentences) >= 2 or self._has_unsupported_numbers(output_text, context)

    def _expanded_tokens(self, text: str) -> set[str]:
        tokens = {self._stem(token) for token in self._tokens(text)}
        expanded = set(tokens)
        for group in self.synonym_groups:
            stemmed_group = {self._stem(token) for token in group}
            if tokens.intersection(stemmed_group):
                expanded.update(stemmed_group)
        return expanded

    def _sentence_support_score(self, sentence: str, context_terms: set[str]) -> int:
        sentence_terms = self._expanded_tokens(sentence)
        if not sentence_terms:
            return 50
        overlap = sentence_terms.intersection(context_terms)
        return self._clamp_score(round((len(overlap) / len(sentence_terms)) * 100))

    def _sentences(self, text: str) -> list[str]:
        return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text) if sentence.strip()]

    def _phrase_bonus(self, source_text: str, output_text: str) -> int:
        source_phrases = self._bigrams(source_text)
        output_phrases = self._bigrams(output_text)
        if not source_phrases or not output_phrases:
            return 0
        return min(10, round((len(source_phrases.intersection(output_phrases)) / len(source_phrases)) * 20))

    def _bigrams(self, text: str) -> set[tuple[str, str]]:
        tokens = [self._stem(token) for token in self._tokens(text)]
        return set(zip(tokens, tokens[1:], strict=False))

    def _has_unsupported_numbers(self, output_text: str, context_text: str) -> bool:
        output_numbers = set(re.findall(r"\b\d+(?:[.,]\d+)?%?\b", output_text))
        if not output_numbers:
            return False
        context_numbers = set(re.findall(r"\b\d+(?:[.,]\d+)?%?\b", context_text))
        return not output_numbers.issubset(context_numbers)

    def _stem(self, token: str) -> str:
        for suffix in ("ingly", "edly", "ing", "ed", "ies", "s"):
            if len(token) > len(suffix) + 3 and token.endswith(suffix):
                if suffix == "ies":
                    return f"{token[:-3]}y"
                return token[: -len(suffix)]
        return token


class OllamaEvaluationProvider(EvaluationProvider):
    provider_name = "ollama_local_judge"

    def __init__(self, settings: Settings) -> None:
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_evaluation_model
        self.timeout_seconds = settings.request_timeout_seconds
        self.fallback = SemanticLocalEvaluationProvider()

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        prompt = self._build_judge_prompt(request)
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    f"{self.base_url}/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False, "format": "json"},
                )
                response.raise_for_status()
                payload = response.json()
            parsed = self._parse_json_response(str(payload.get("response", "")))
            return self._result_from_payload(parsed, request)
        except Exception as exc:
            fallback_result = self.fallback.evaluate(request)
            return EvaluationResult(
                provider=f"{self.provider_name}_fallback",
                evaluation_score=fallback_result.evaluation_score,
                relevance_score=fallback_result.relevance_score,
                groundedness_score=fallback_result.groundedness_score,
                hallucination_flag=fallback_result.hallucination_flag,
                evaluation_summary=f"Ollama evaluation unavailable; used semantic local fallback. Reason: {exc}",
                requires_human_review=fallback_result.requires_human_review,
                threshold=request.threshold,
            )

    def _build_judge_prompt(self, request: EvaluationRequest) -> str:
        retrieved_context = "\n".join(f"- {document}" for document in request.retrieved_documents) or "No retrieved documents supplied."
        return (
            "You are a bounded AI governance evaluation agent. "
            "Return only JSON with keys evaluation_score, relevance_score, groundedness_score, "
            "hallucination_flag, evaluation_summary.\n"
            f"Risk level: {request.ai_system.risk_level}\n"
            f"Threshold: {request.threshold}\n"
            f"Prompt: {request.prompt}\n"
            f"Input: {request.input_text}\n"
            f"Retrieved documents:\n{retrieved_context}\n"
            f"Output to evaluate: {request.output_text}\n"
        )

    def _parse_json_response(self, response_text: str) -> dict:
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if match is None:
                raise
            return json.loads(match.group(0))

    def _result_from_payload(self, payload: dict, request: EvaluationRequest) -> EvaluationResult:
        evaluation_score = self._score_from_payload(payload, "evaluation_score")
        relevance_score = self._score_from_payload(payload, "relevance_score")
        groundedness_score = self._score_from_payload(payload, "groundedness_score")
        hallucination_flag = bool(payload.get("hallucination_flag", False))
        requires_review = evaluation_score < request.threshold or hallucination_flag
        summary = str(payload.get("evaluation_summary", "Ollama local judge returned a structured evaluation."))
        return EvaluationResult(
            provider=self.provider_name,
            evaluation_score=evaluation_score,
            relevance_score=relevance_score,
            groundedness_score=groundedness_score,
            hallucination_flag=hallucination_flag,
            evaluation_summary=summary,
            requires_human_review=requires_review,
            threshold=request.threshold,
        )

    def _score_from_payload(self, payload: dict, key: str) -> int:
        raw_value = payload.get(key, 0)
        try:
            value = int(raw_value)
        except (TypeError, ValueError):
            value = 0
        return max(0, min(100, value))


def get_evaluation_provider(provider_name: str, settings: Settings | None = None) -> EvaluationProvider:
    if provider_name == "local":
        return LocalEvaluationProvider()
    if provider_name == "semantic_local":
        return SemanticLocalEvaluationProvider()
    if provider_name == "ollama_local":
        if settings is None:
            raise ValueError("ollama_local evaluation provider requires settings.")
        return OllamaEvaluationProvider(settings)
    raise ValueError(f"Unsupported EVALUATION_PROVIDER: {provider_name}")
