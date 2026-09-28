"""
rag/topic_engine.py
────────────────────────────────────────────────────────────────────────────────
Module 4: Automated Word Cloud & Topic Identification Engine
Supports:
  - Word cloud frequency data (ready for any frontend word cloud library)
  - Domain-aware topic clustering into named groups
  - Per-document keyword summary
  - Subsidiary-filtered results
  - AI-generated insights from Gemini
"""

import re
from collections import Counter
from typing import List, Dict, Optional

# ── Domain-specific CIL/CMPDI stopwords to filter ────────────────────────────
MINING_STOPWORDS = {
    "the", "a", "an", "and", "or", "is", "in", "on", "at", "to", "of",
    "for", "with", "that", "this", "it", "as", "by", "be", "are", "was",
    "were", "has", "have", "had", "from", "page", "figure", "table", "total",
    "shall", "may", "also", "been", "such", "into", "than", "its", "which",
    "not", "but", "all", "one", "will", "more", "other", "can", "per",
    "during", "after", "before", "between", "including", "about", "under",
    "over", "above", "below", "each", "their", "they", "would", "should",
    "could", "shall", "within", "without", "through", "both", "only",
    "however", "therefore", "whereas", "thereby", "thereof", "therein",
    "where", "when", "what", "how", "nil", "none", "nos", "no", "sl",
}

# ── Named topic clusters: keywords map to these theme labels ──────────────────
TOPIC_KEYWORD_MAP: Dict[str, List[str]] = {
    "Coal Production & Offtake": [
        "production", "offtake", "dispatch", "output", "extraction", "mine", "mining",
        "opencast", "underground", "seam", "coal", "coking", "non-coking", "washed",
        "beneficiation", "grade", "quality", "output", "annual", "monthly", "rake",
        "loading", "railway", "wagon", "metric", "tonne", "million", "mt",
    ],
    "Geological Exploration & Reserves": [
        "geological", "exploration", "reserve", "proved", "indicated", "inferred",
        "borehole", "drilling", "meterage", "seam", "thickness", "depth", "lithology",
        "stratigraphy", "sandstone", "shale", "carboniferous", "gondwana",
        "block", "survey", "geophysical", "seismic", "logging", "core",
        "estimate", "resources", "coal bearing",
    ],
    "Overburden & Stripping Operations": [
        "overburden", "ob", "stripping", "ratio", "composite", "removal", "dragline",
        "shovel", "dumper", "blasting", "surface", "bench", "pit", "quarry",
        "excavation", "earthwork", "advance", "exposure", "highwall",
        "hemm", "heavy", "machinery", "equipment",
    ],
    "Safety & Statutory Compliance": [
        "safety", "accident", "fatal", "injury", "dgms", "statutory", "inspector",
        "regulation", "compliance", "dust", "gas", "ventilation", "support",
        "rescue", "first", "aid", "firefighting", "incident", "occupational",
        "health", "ppe", "training", "fire", "explosion", "methane",
    ],
    "Parliamentary & Administrative Queries": [
        "parliament", "parliamentary", "lok", "sabha", "rajya", "question",
        "starred", "unstarred", "minister", "ministry", "response", "reply",
        "government", "policy", "scheme", "memorandum", "circular", "order",
        "gazette", "notification", "administrative", "subsidiary",
    ],
    "Environment & Forest Clearance": [
        "environment", "environmental", "forest", "clearance", "ec", "fc",
        "wildlife", "sanctuary", "green", "tree", "plantation", "rehabilitation",
        "resettlement", "displacement", "compensation", "pollution", "emission",
        "water", "air", "noise", "eia", "mef", "moef",
    ],
    "HR, Finance & Operations": [
        "manpower", "employee", "worker", "labour", "wage", "salary", "recruitment",
        "training", "budget", "expenditure", "revenue", "profit", "loss",
        "turnover", "capital", "investment", "cost", "productivity", "output",
        "performance", "efficiency", "target", "plan",
    ],
}


# ── In-memory document store for topic engine ─────────────────────────────────
_documents: List[Dict] = []   # each: {text, source, subsidiary}


def add_document(text: str, source: str, subsidiary: str = "General"):
    """Register a document's text into the topic engine."""
    _documents.append({
        "text": text,
        "source": source,
        "subsidiary": subsidiary.strip() if subsidiary else "General",
    })


def reset():
    """Clear all registered documents."""
    _documents.clear()


def _clean_text(text: str) -> str:
    """Remove special characters, normalize whitespace, lowercase."""
    text = re.sub(r"[^a-zA-Z\s\-]", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def _get_word_freq(text: str, min_len: int = 4) -> Counter:
    """Compute word frequency from text, excluding stopwords."""
    words = [
        w.strip("-") for w in _clean_text(text).split()
        if len(w) >= min_len and w.strip("-") not in MINING_STOPWORDS
    ]
    return Counter(words)


def get_wordcloud_data(subsidiary: Optional[str] = None, top_n: int = 100) -> List[Dict]:
    """
    Returns word cloud frequency array ready for any frontend library.
    Format: [{"text": "coal", "value": 85}, ...]

    Args:
        subsidiary: Filter by subsidiary name or None for all.
        top_n: Number of top words to return.
    """
    docs = _documents
    if subsidiary and subsidiary.lower() not in ("all", "all subsidiaries", ""):
        docs = [d for d in _documents if d["subsidiary"].lower() == subsidiary.lower()]

    if not docs:
        return []

    combined = " ".join(d["text"] for d in docs)
    freq = _get_word_freq(combined)

    return [
        {"text": word, "value": count}
        for word, count in freq.most_common(top_n)
    ]


def get_topic_clusters(subsidiary: Optional[str] = None) -> List[Dict]:
    """
    Classify words from all documents into named CIL/CMPDI topic clusters.

    Returns:
        [
          {
            "topic": "Coal Production & Offtake",
            "score": 0.42,
            "top_keywords": ["production", "offtake", "coking"],
            "document_count": 3
          },
          ...
        ]
    """
    docs = _documents
    if subsidiary and subsidiary.lower() not in ("all", "all subsidiaries", ""):
        docs = [d for d in _documents if d["subsidiary"].lower() == subsidiary.lower()]

    if not docs:
        return []

    combined = " ".join(d["text"] for d in docs)
    word_freq = _get_word_freq(combined)
    total_words = sum(word_freq.values()) or 1

    results = []
    for topic_name, keywords in TOPIC_KEYWORD_MAP.items():
        matched = {kw: word_freq.get(kw, 0) for kw in keywords if word_freq.get(kw, 0) > 0}
        if not matched:
            continue

        topic_word_count = sum(matched.values())
        score = round(topic_word_count / total_words, 4)

        # Documents that mention at least one keyword in this topic
        relevant_docs = set()
        for d in docs:
            d_words = set(_clean_text(d["text"]).split())
            if any(kw in d_words for kw in keywords):
                relevant_docs.add(d["source"])

        results.append({
            "topic": topic_name,
            "score": score,
            "top_keywords": sorted(matched, key=matched.get, reverse=True)[:8],
            "document_count": len(relevant_docs),
            "documents": sorted(relevant_docs),
        })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def get_per_document_keywords(top_n: int = 10) -> List[Dict]:
    """
    Returns keyword summary per uploaded document.
    """
    output = []
    for doc in _documents:
        freq = _get_word_freq(doc["text"])
        keywords = [
            {"keyword": word, "count": count}
            for word, count in freq.most_common(top_n)
        ]
        output.append({
            "source": doc["source"],
            "subsidiary": doc["subsidiary"],
            "keywords": keywords,
        })
    return output


def get_ai_insights(subsidiary: Optional[str] = None) -> str:
    """
    Use Gemini to generate a natural-language topic insight summary
    from keyword frequency data. Returns a string.
    """
    from rag.gemini_client import generate

    docs = _documents
    if subsidiary and subsidiary.lower() not in ("all", "all subsidiaries", ""):
        docs = [d for d in _documents if d["subsidiary"].lower() == subsidiary.lower()]

    if not docs:
        return "No documents available to generate insights."

    combined = " ".join(d["text"] for d in docs)[:8000]  # limit tokens

    clusters = get_topic_clusters(subsidiary=subsidiary)
    cluster_summary = "\n".join(
        f"- {c['topic']}: keywords = {', '.join(c['top_keywords'][:5])}"
        for c in clusters[:5]
    )

    prompt = f"""You are a domain expert for Coal India Limited (CIL) and CMPDI.

Based on the following topic clusters extracted from uploaded official documents, write a concise 3-4 sentence intelligence briefing:

Identified Topic Clusters:
{cluster_summary}

Document Sample:
{combined[:2000]}

Write a brief insight note for Ministry of Coal leadership about:
1. What are the main themes/issues across documents?
2. Any notable operational bottlenecks or priorities visible in the data?

Keep it factual, formal, and government-report style."""

    return generate(prompt, max_tokens=512)
