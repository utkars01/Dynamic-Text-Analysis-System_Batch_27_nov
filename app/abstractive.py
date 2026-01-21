# app/abstractive.py

from transformers import pipeline
from typing import Optional

_summarizer = None


def _load_model():
    global _summarizer
    if _summarizer is None:
        _summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            device=-1  # CPU-safe
        )
    return _summarizer

def _dynamic_max_length(text: str) -> int:
    n_tokens = len(text.split())
    return min(150, max(40, n_tokens // 2))


def abstractive_summary(
    text: str
) -> Optional[str]:
    """
    Generate abstractive summary from provided text.
    Expects already-prepared input text.
    """

    if not text or not text.strip():
        return None

    text = text.strip()

    # Hard safety limit
    if len(text) > 3000:
        text = text[:3000]

    summarizer = _load_model()
    max_len = _dynamic_max_length(text)

    try:
        result = summarizer(
            text,
            min_length=max(20, max_len // 3),
            max_length=max_len,
            length_penalty=1.5,
            do_sample=False
        )
        return result[0]["summary_text"]
    except Exception:
        return None
