from __future__ import annotations

import re
from collections import Counter

from seemycitations.models import KeywordResult, PageMatch

STOP_WORDS = {
    "a", "about", "also", "an", "and", "are", "as", "at", "be", "been", "between",
    "by", "can", "could", "do", "for", "from", "had", "has", "have", "in", "into",
    "is", "it", "its", "may", "more", "most", "not", "of", "on", "or", "our", "such",
    "than", "that", "the", "their", "these", "this", "those", "to", "using", "was",
    "we", "were", "which", "will", "with", "within", "would", "you", "your",
}


def extract_keywords(pages: list[dict], *, limit: int = 12) -> list[str]:
    """Rank repeated local terms and phrases without external models."""
    text = "\n".join(page.get("text", "") for page in pages)
    tokens = [token.casefold() for token in re.findall(r"[A-Za-z][A-Za-z'-]{2,}", text)]
    useful = [token for token in tokens if token not in STOP_WORDS and not token.isnumeric()]
    if not useful or limit <= 0:
        return []
    singles = Counter(useful)
    phrases: Counter[str] = Counter()
    for size in (2, 3):
        for index in range(len(tokens) - size + 1):
            group = tokens[index:index + size]
            if all(word not in STOP_WORDS for word in group):
                phrases[" ".join(group)] += 1
    candidates: list[tuple[str, float, int]] = []
    candidates.extend((term, float(count), 1) for term, count in singles.items() if count >= 2)
    candidates.extend(
        (term, count * (1.8 if words == 2 else 2.3), words)
        for term, count in phrases.items()
        if count >= 2
        for words in [term.count(" ") + 1]
    )
    candidates.sort(key=lambda item: (-item[1], -item[2], item[0]))
    chosen: list[str] = []
    for term, _score, words in candidates:
        if words == 1 and any(term in phrase.split() for phrase in chosen if " " in phrase):
            continue
        if term not in chosen:
            chosen.append(term)
        if len(chosen) == limit:
            break
    return chosen


def parse_keywords(raw: str) -> list[str]:
    seen: set[str] = set()
    parsed: list[str] = []
    for value in re.split(r"[,\n]+", raw):
        keyword = " ".join(value.strip().split())
        folded = keyword.casefold()
        if keyword and folded not in seen:
            seen.add(folded)
            parsed.append(keyword)
    return parsed


def _snippet(text: str, start: int, end: int, *, radius: int = 70) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    value = " ".join(text[left:right].split())
    if left:
        value = f"…{value}"
    if right < len(text):
        value = f"{value}…"
    return value


def analyze_keywords(pages: list[dict], raw: str) -> list[KeywordResult]:
    results: list[KeywordResult] = []
    for keyword in parse_keywords(raw):
        pattern = re.compile(rf"(?<!\w){re.escape(keyword)}(?!\w)", re.IGNORECASE)
        matches: list[PageMatch] = []
        for page in pages:
            text = page.get("text", "")
            for match in pattern.finditer(text):
                matches.append(
                    PageMatch(
                        page=int(page["page"]),
                        snippet=_snippet(text, match.start(), match.end()),
                        start=match.start(),
                    )
                )
        results.append(KeywordResult(keyword=keyword, count=len(matches), pages=matches))
    return sorted(results, key=lambda item: (-item.count, item.keyword.casefold()))
