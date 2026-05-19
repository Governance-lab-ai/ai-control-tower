import re
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Literal

Confidence = Literal["low", "medium", "high"]


@dataclass(frozen=True)
class PIILocation:
    pii_type: str
    snippet: str
    start: int
    end: int


@dataclass(frozen=True)
class PIIResult:
    pii_detected: bool
    pii_types: list[str]
    locations: list[PIILocation]
    confidence: Confidence

    def to_dict(self) -> dict:
        return {
            "pii_detected": self.pii_detected,
            "pii_types": self.pii_types,
            "locations": [asdict(location) for location in self.locations],
            "confidence": self.confidence,
        }


class PIIDetector(ABC):
    @abstractmethod
    def detect(self, text: str) -> PIIResult:
        raise NotImplementedError


class LocalRegexPIIDetector(PIIDetector):
    patterns: tuple[tuple[str, re.Pattern[str]], ...] = (
        ("email", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
        ("phone_number", re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b")),
        (
            "name",
            re.compile(
                r"\b(?:customer|client|user|patient|employee)?\s*name\s*:\s*([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,3})",
                re.IGNORECASE,
            ),
        ),
        (
            "account_id",
            re.compile(
                r"\b(?:account(?:\s*(?:id|number))?|customer\s*id|client\s*id)\s*:\s*([A-Za-z0-9][A-Za-z0-9_-]{3,})",
                re.IGNORECASE,
            ),
        ),
        (
            "address",
            re.compile(r"\b(?:home\s+address|shipping\s+address|address)\s*:\s*([^.\n]{5,120})", re.IGNORECASE),
        ),
    )

    def detect(self, text: str) -> PIIResult:
        locations: list[PIILocation] = []
        for pii_type, pattern in self.patterns:
            for match in pattern.finditer(text):
                start, end = match.span()
                locations.append(
                    PIILocation(
                        pii_type=pii_type,
                        snippet=self._redacted_snippet(text, start, end, pii_type),
                        start=start,
                        end=end,
                    )
                )

        pii_types = sorted({location.pii_type for location in locations})
        return PIIResult(
            pii_detected=bool(locations),
            pii_types=pii_types,
            locations=locations,
            confidence=self._confidence(pii_types),
        )

    def _confidence(self, pii_types: list[str]) -> Confidence:
        if not pii_types:
            return "low"
        if "email" in pii_types or "phone_number" in pii_types:
            return "high"
        if "account_id" in pii_types or "address" in pii_types:
            return "medium"
        return "low"

    def _redacted_snippet(self, text: str, start: int, end: int, pii_type: str) -> str:
        prefix_start = max(0, start - 24)
        suffix_end = min(len(text), end + 24)
        prefix = text[prefix_start:start]
        suffix = text[end:suffix_end]
        return f"{prefix}[REDACTED_{pii_type.upper()}]{suffix}".strip()


def get_pii_detector() -> PIIDetector:
    return LocalRegexPIIDetector()
