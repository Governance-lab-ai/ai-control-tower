from app.services.pii import LocalRegexPIIDetector


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
