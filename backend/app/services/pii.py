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


class HybridLocalPIIDetector(PIIDetector):
    """Free local detector for demo PII patterns.

    This combines deterministic recognizers only. It is intentionally explainable
    and dependency-free; it is not comprehensive PII detection.
    """

    labelled_patterns: tuple[tuple[str, re.Pattern[str]], ...] = (
        (
            "name",
            re.compile(
                r"(?i:\b(?:customer|client|user|patient|employee|contact)?\s*name)\s*:\s*([A-Z][A-Za-z'.-]+(?:\s+[A-Z][A-Za-z'.-]+){0,3})",
            ),
        ),
        (
            "account_id",
            re.compile(
                r"(?i:\b(?:account(?:\s*(?:id|number|no))?|customer\s*(?:id|number)|client\s*(?:id|number)|member\s*(?:id|number)))\s*:\s*([A-Za-z0-9][A-Za-z0-9_-]{3,})",
            ),
        ),
        (
            "address",
            re.compile(
                r"(?i:\b(?:home\s+address|shipping\s+address|billing\s+address|address))\s*:\s*([^.\n]{5,140})",
            ),
        ),
        (
            "date_of_birth",
            re.compile(
                r"(?i:\b(?:dob|date\s+of\s+birth|birth\s+date))\s*:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})",
            ),
        ),
        (
            "national_id",
            re.compile(
                r"(?i:\b(?:ssn|national\s+id|tax\s+id|nino|national\s+insurance\s+number))\s*:\s*([A-Za-z0-9][A-Za-z0-9 -]{5,24})",
            ),
        ),
        (
            "postal_code",
            re.compile(
                r"(?i:\b(?:postcode|postal\s+code|zip\s+code|zip))\s*:\s*([A-Z0-9][A-Z0-9 -]{3,10})",
            ),
        ),
        (
            "phone_number",
            re.compile(r"(?i:\b(?:phone|telephone|mobile|cell))\s*:?\s*(\+?\d[\d().\-\s]{7,20}\d)"),
        ),
    )
    direct_patterns: tuple[tuple[str, re.Pattern[str]], ...] = (
        ("email", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
        (
            "phone_number",
            re.compile(r"(?<!\w)\+\d{1,3}[-.\s]?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{4}(?!\w)"),
        ),
        (
            "iban",
            re.compile(r"\b[A-Z]{2}\d{2}\s+(?:[A-Z0-9]{2,4}\s+){2,7}[A-Z0-9]{2,4}\b", re.IGNORECASE),
        ),
    )
    payment_card_pattern = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")

    def detect(self, text: str) -> PIIResult:
        locations: list[PIILocation] = []
        for pii_type, pattern in (*self.labelled_patterns, *self.direct_patterns):
            locations.extend(self._locations_for_pattern(text, pii_type, pattern))

        for match in self.payment_card_pattern.finditer(text):
            candidate = re.sub(r"\D", "", match.group(0))
            if 13 <= len(candidate) <= 19 and self._passes_luhn(candidate):
                locations.append(self._location(text, match.start(), match.end(), "payment_card"))

        locations = self._deduplicate(locations)
        pii_types = sorted({location.pii_type for location in locations})
        return PIIResult(
            pii_detected=bool(locations),
            pii_types=pii_types,
            locations=locations,
            confidence=self._confidence(pii_types, locations),
        )

    def redact_text(self, text: str) -> str:
        result = self.detect(text)
        redacted = text
        for location in sorted(result.locations, key=lambda item: item.start, reverse=True):
            redacted = f"{redacted[:location.start]}[REDACTED_{location.pii_type.upper()}]{redacted[location.end:]}"
        return redacted

    def _locations_for_pattern(self, text: str, pii_type: str, pattern: re.Pattern[str]) -> list[PIILocation]:
        locations: list[PIILocation] = []
        for match in pattern.finditer(text):
            start, end = match.span(1) if match.groups() else match.span()
            locations.append(self._location(text, start, end, pii_type))
        return locations

    def _location(self, text: str, start: int, end: int, pii_type: str) -> PIILocation:
        prefix_start = max(0, start - 24)
        suffix_end = min(len(text), end + 24)
        prefix = text[prefix_start:start]
        suffix = text[end:suffix_end]
        return PIILocation(
            pii_type=pii_type,
            snippet=f"{prefix}[REDACTED_{pii_type.upper()}]{suffix}".strip(),
            start=start,
            end=end,
        )

    def _deduplicate(self, locations: list[PIILocation]) -> list[PIILocation]:
        sorted_locations = sorted(locations, key=lambda item: (item.start, -(item.end - item.start)))
        deduped: list[PIILocation] = []
        occupied_ranges: list[tuple[int, int]] = []
        for location in sorted_locations:
            if any(location.start < end and location.end > start for start, end in occupied_ranges):
                continue
            deduped.append(location)
            occupied_ranges.append((location.start, location.end))
        return deduped

    def _confidence(self, pii_types: list[str], locations: list[PIILocation]) -> Confidence:
        if not pii_types:
            return "low"
        high_signal_types = {"email", "phone_number", "payment_card", "iban", "national_id"}
        if high_signal_types.intersection(pii_types) or len(locations) >= 3:
            return "high"
        if {"account_id", "address", "date_of_birth", "postal_code"}.intersection(pii_types) or len(locations) >= 2:
            return "medium"
        return "low"

    def _passes_luhn(self, value: str) -> bool:
        total = 0
        reverse_digits = [int(character) for character in value[::-1]]
        for index, digit in enumerate(reverse_digits):
            if index % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            total += digit
        return total % 10 == 0


def get_pii_detector() -> PIIDetector:
    return HybridLocalPIIDetector()
