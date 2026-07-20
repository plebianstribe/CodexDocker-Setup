from seemycitations.services.keywords import analyze_keywords, parse_keywords


PAGES = [
    {"page": 1, "text": "Model models MODEL. Evidence-based evidence."},
    {"page": 2, "text": "A model offers evidence, and another model follows."},
]


def test_parser_trims_collapses_duplicates_and_empties() -> None:
    assert parse_keywords(" Model, evidence\nmodel,  ,Evidence ") == ["Model", "evidence"]


def test_whole_word_case_insensitive_counts_are_sorted() -> None:
    results = analyze_keywords(PAGES, "evidence, model, absent")
    assert [(item.keyword, item.count) for item in results] == [
        ("model", 4),
        ("evidence", 3),
        ("absent", 0),
    ]
    assert [match.page for match in results[0].pages] == [1, 1, 2, 2]


def test_punctuation_and_phrase_boundaries_are_consistent() -> None:
    results = analyze_keywords(
        [{"page": 3, "text": "meta-analysis meta-analysis; metaanalysis. deep learning's reach"}],
        "meta-analysis, deep learning",
    )
    assert [(item.keyword, item.count) for item in results] == [("meta-analysis", 2), ("deep learning", 1)]
    assert results[0].pages[0].snippet


def test_alphabetical_tie_break_is_deterministic() -> None:
    results = analyze_keywords([{"page": 1, "text": "beta alpha"}], "beta, alpha")
    assert [item.keyword for item in results] == ["alpha", "beta"]
