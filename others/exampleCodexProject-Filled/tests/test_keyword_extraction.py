from seemycitations.services.keywords import extract_keywords


def test_extracts_repeated_phrases_and_filters_stop_words() -> None:
    pages = [{"page": 1, "text": "Neural networks use memory retrieval. Neural networks improve memory retrieval. The the and and."}]
    result = extract_keywords(pages, limit=5)
    assert "neural networks" in result
    assert "memory retrieval" in result
    assert "the" not in result


def test_extraction_is_deterministic_limited_and_noise_safe() -> None:
    pages = [{"page": 1, "text": "beta beta alpha alpha 123 123 x y"}]
    assert extract_keywords(pages, limit=1) == ["alpha"]
    assert extract_keywords([], limit=10) == []
