from app.services.pii import HybridLocalPIIDetector, LocalRegexPIIDetector, get_pii_detector


def test_local_regex_pii_detector_detects_synthetic_patterns() -> None:
    detector = LocalRegexPIIDetector()

    result = detector.detect(
        "Customer name: Alex Morgan. Email alex.morgan@example.test. "
        "Phone: 555-123-4567. Account ID: ACCT-12345. Address: 10 Demo Street, Testville"
    )

    assert result.pii_detected is True
    assert set(result.pii_types) >= {"account_id", "address", "email", "name", "phone_number"}
    assert result.confidence == "high"
    assert all("[REDACTED_" in location.snippet for location in result.locations)


def test_local_regex_pii_detector_negative_case() -> None:
    detector = LocalRegexPIIDetector()

    result = detector.detect("Synthetic support ticket asks for a delivery status update.")

    assert result.pii_detected is False
    assert result.pii_types == []
    assert result.locations == []
    assert result.confidence == "low"


def test_hybrid_local_pii_detector_detects_broader_local_patterns() -> None:
    detector = HybridLocalPIIDetector()

    result = detector.detect(
        "Customer name: Priya Shah. DOB: 1990-04-12. Phone +44 7700 900123. "
        "Card: 4111 1111 1111 1111. IBAN GB82 WEST 1234 5698 7654 32. "
        "Postcode: SW1A 1AA. National ID: QQ 12 34 56 C."
    )

    assert result.pii_detected is True
    assert set(result.pii_types) >= {
        "date_of_birth",
        "iban",
        "name",
        "national_id",
        "payment_card",
        "phone_number",
        "postal_code",
    }
    assert result.confidence == "high"
    assert all("[REDACTED_" in location.snippet for location in result.locations)


def test_hybrid_local_pii_detector_avoids_invalid_card_numbers() -> None:
    detector = HybridLocalPIIDetector()

    result = detector.detect("Reference number 4111 1111 1111 1112 should not pass card checksum.")

    assert "payment_card" not in result.pii_types


def test_hybrid_local_pii_detector_ignores_uuid_like_identifiers() -> None:
    detector = HybridLocalPIIDetector()

    result = detector.detect("Synthetic system id 6f6176d8-48f2-47f1-a7a0-ed56103a2123 was evaluated.")

    assert result.pii_detected is False
    assert result.pii_types == []


def test_hybrid_local_pii_detector_can_redact_full_text() -> None:
    detector = HybridLocalPIIDetector()

    redacted = detector.redact_text("Customer name: Alex Morgan. Email alex.morgan@example.test.")

    assert "Alex Morgan" not in redacted
    assert "alex.morgan@example.test" not in redacted
    assert "[REDACTED_NAME]" in redacted
    assert "[REDACTED_EMAIL]" in redacted


def test_default_pii_detector_uses_hybrid_detector() -> None:
    assert isinstance(get_pii_detector(), HybridLocalPIIDetector)
