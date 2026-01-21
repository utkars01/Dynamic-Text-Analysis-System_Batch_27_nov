from typing import List
import numpy as np
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

_nlp = None

def _load_spacy():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])
        if "sentencizer" not in _nlp.pipe_names:
            _nlp.add_pipe("sentencizer")
    return _nlp


def _dynamic_top_n(n_sentences: int) -> int:
    """
    Hybrid rule:
    - 20% of sentences
    - min 2, max 8
    """
    return min(8, max(2, round(0.2 * n_sentences)))


def extractive_summary(text: str) -> List[str]:
    """
    TextRank-based extractive summarization.
    Returns a list of important sentences.
    """

    if not text or not text.strip():
        return []

    nlp = _load_spacy()
    doc = nlp(text)

    sentences = [s.text.strip() for s in doc.sents if s.text.strip()]
    n = len(sentences)

    if n <= 2:
        return sentences

    top_n = _dynamic_top_n(n)

    # Vectorize sentences
    vectorizer = TfidfVectorizer(stop_words="english")
    sent_vectors = vectorizer.fit_transform(sentences)

    # Similarity matrix
    sim_matrix = cosine_similarity(sent_vectors)

    # Build graph
    graph = nx.from_numpy_array(sim_matrix)

    # PageRank scoring
    scores = nx.pagerank(graph)

    ranked = sorted(
        ((scores[i], s) for i, s in enumerate(sentences)),
        reverse=True
    )

    return [s for _, s in ranked[:top_n]]
