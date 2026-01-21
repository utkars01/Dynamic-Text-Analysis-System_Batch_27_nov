"""
Backend aggregation utilities for AI Narrative Nexus dashboard.

These functions operate ONLY at document-level.
They intentionally hide chunks/rows from the UI.
"""

from collections import Counter, defaultdict
from statistics import mean
from typing import List, Dict
from .abstractive import abstractive_summary


def aggregate_docs(docs: List[Dict]) -> Dict:
    """
    Entry point: aggregate all insights for a single uploaded file.
    `docs` = list of corpus entries belonging to the same file.
    """
    return {
        "topics": aggregate_topics(docs),
        "sentiment": aggregate_sentiment(docs),
        "summaries": aggregate_summaries(docs),
        "tokens": aggregate_tokens(docs),
    }


# -------------------- TOPICS --------------------

def aggregate_topics(docs: List[Dict]) -> Dict:
    """
    Average topic probabilities across all chunks/rows.
    Returns labels, values, and keywords for visualization.
    """
    topic_probs = defaultdict(list)
    topic_keywords = {}

    for doc in docs:
        for t in doc.get("topics", []):
            topic_probs[t["label"]].append(t["probability"])
            topic_keywords[t["label"]] = t.get("keywords", [])

    labels = list(topic_probs.keys())
    values = [round(mean(v), 4) for v in topic_probs.values()]
    keywords = [topic_keywords[l] for l in labels]

    return {
        "labels": labels,
        "values": values,
        "keywords": keywords
    }


# -------------------- SENTIMENT --------------------

def aggregate_sentiment(docs: List[Dict]) -> Dict:
    """
    Aggregate sentiment scores across all chunks.
    Uses model-provided probability scores instead of labels.
    """
    totals = {
        "Positive": 0.0,
        "Neutral": 0.0,
        "Negative": 0.0,
    }

    count = 0

    for doc in docs:
        scores = doc.get("sentiment", {}).get("scores")
        if not scores:
            continue

        for k in totals:
            totals[k] += scores.get(k, 0.0)

        count += 1

    if count == 0:
        return {"values": [0, 0, 0]}

    return {
        "values": [
            round((totals["Positive"] / count) * 100, 2),
            round((totals["Neutral"] / count) * 100, 2),
            round((totals["Negative"] / count) * 100, 2),
        ]
    }


# -------------------- SUMMARIES --------------------

def aggregate_summaries(docs):
    is_csv = docs and docs[0].get("row_index", -1) != -1

    extractive = []
    abstractive = ""

    # ---------- CSV CASE ----------
    if is_csv:
        # Do NOT attempt extractive or abstractive summarization
        return {
            "extractive": [],
            "abstractive": (
                "This dataset contains multiple records covering related topics. "
                "The summary below reflects dominant themes, sentiment distribution, "
                "and frequently occurring terms across all rows."
            ),
        }

    # ---------- TXT / DOC CASE ----------
    extractive_seen = set()
    abstractive_seen = set()

    for d in docs:
        for s in d.get("extractive_summary", []):
            if s not in extractive_seen:
                extractive_seen.add(s)
                extractive.append(s)

        abs_sum = d.get("abstractive_summary")
        if abs_sum and abs_sum not in abstractive_seen:
            abstractive_seen.add(abs_sum)

    # Join ONCE
    abstractive = " ".join(abstractive_seen)

    return {
        "extractive": extractive[:50],
        "abstractive": abstractive,
    }


# -------------------- TOKENS / WORD CLOUD --------------------

def aggregate_tokens(docs: List[Dict]) -> List[str]:
    """
    Collect all tokens for word cloud generation.
    """
    tokens = []
    for doc in docs:
        tokens.extend(doc.get("tokens", []))
    return tokens
