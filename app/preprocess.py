from typing import List, Dict, Tuple, Optional
import re
import math


try:
    import spacy
    # We will try to load model lazily in normalize_text to give clearer error messages
    _SPACY_AVAILABLE = True
except Exception:
    _SPACY_AVAILABLE = False

# Basic stopword list fallback (small). If spacy is available we will use spacy's stop words.
FALLBACK_STOPWORDS = {
    "the","and","is","in","it","of","to","a","an","that","this","for","on","with","as","are","was","were","be",
    "by","or","from","at","which","but","not","have","has","had","I","you","he","she","they","we","their","them"
}

_url_re = re.compile(r"https?://\S+|www\.\S+")
_non_alnum_re = re.compile(r"[^A-Za-z0-9\s]")
_multi_space_re = re.compile(r"\s+")


_spacy_nlp = None
def _load_spacy_model():
    global _spacy_nlp
    if _spacy_nlp is None:
        if not _SPACY_AVAILABLE:
            raise RuntimeError(
                "spaCy is not installed. Install with `pip install spacy` and download the model "
                "with `python -m spacy download en_core_web_sm`."
            )
        try:
            _spacy_nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        except OSError as e:
            raise RuntimeError(
                "spaCy model 'en_core_web_sm' not found. Run:\n"
                "  python -m spacy download en_core_web_sm"
            ) from e
    return _spacy_nlp

def clean_text(text: str, remove_stopwords: bool = True) -> str:
    
    if text is None:
        return ""

    s = text.strip()
    # lowercase
    s = s.lower()
    # remove urls
    s = _url_re.sub(" ", s)
    # remove non-alphanumeric
    s = _non_alnum_re.sub(" ", s)
    # collapse spaces
    s = _multi_space_re.sub(" ", s).strip()

    if remove_stopwords:
        # choose stopword set
        if _SPACY_AVAILABLE:
            try:
                nlp = _load_spacy_model()
                stop_words = nlp.Defaults.stop_words
            except Exception:
                stop_words = FALLBACK_STOPWORDS
        else:
            stop_words = FALLBACK_STOPWORDS

        # remove stopwords (simple token-level remove)
        tokens = s.split()
        tokens_filtered = [t for t in tokens if t not in stop_words]
        s = " ".join(tokens_filtered)

    return s

def split_text(text: str, max_chars: int = 50000) -> List[str]:
    
    if text is None:
        return []

    text = text.strip()
    if len(text) <= max_chars:
        return [text]

    # Tried to split by paragraphs/newlines first
    paragraphs = [p.strip() for p in re.split(r"\n{1,}", text) if p.strip()]
    chunks = []
    current = []
    current_len = 0

    for p in paragraphs:
        plen = len(p)
        if current_len + plen + 1 <= max_chars:
            current.append(p)
            current_len += plen + 1
        else:
            if current:
                chunks.append("\n".join(current))
            # If paragraph itself is too long, split it by sentences 
            if plen > max_chars:
                # char-based slicing
                for i in range(0, plen, max_chars):
                    chunks.append(p[i:i+max_chars])
                current = []
                current_len = 0
            else:
                current = [p]
                current_len = plen + 1
    if current:
        chunks.append("\n".join(current))

    # As a final check, ensure none exceed
    final = []
    for c in chunks:
        if len(c) <= max_chars:
            final.append(c)
        else:
            # hard-split
            for i in range(0, len(c), max_chars):
                final.append(c[i:i+max_chars])
    return final

def normalize_text(text: str) -> str:
    
    cleaned = clean_text(text, remove_stopwords=True)
    if not cleaned:
        return ""

    nlp = _load_spacy_model()  
    # process in one batch 
    doc = nlp(cleaned)
    lemmas = []
    for token in doc:
        lemma = token.lemma_.strip()
        if lemma == "" or lemma == "-PRON-":
            lemma = token.text
        # filter tiny tokens
        if len(lemma) >= 1:
            lemmas.append(lemma)
    normalized = " ".join(lemmas)
    # final collapse
    normalized = _multi_space_re.sub(" ", normalized).strip()
    return normalized

def tokenize(text: str) -> List[str]:
    
    if not text:
        return []
    return [t for t in text.split() if t.strip()]

def preprocess_text(raw_text: str) -> Dict[str, object]:
    
    cleaned = clean_text(raw_text, remove_stopwords=True)
    try:
        normalized = normalize_text(raw_text)
    except RuntimeError:
        # If spacy is missing, will fall back to using cleaned text as 'normalized'
        normalized = cleaned
    tokens = tokenize(normalized)
    return {
        "raw_text": raw_text,
        "clean_text": cleaned,
        "normalized_text": normalized,
        "tokens": tokens
    }

def preprocess_texts(texts: List[Dict[str, object]],
                     source_file: str,
                     starting_id: int = 0,
                     max_chars: int = 50000) -> Tuple[List[Dict[str, object]], int]:

    docs = []
    current_id = starting_id
    for i, item in enumerate(texts):
        # item can be either a str or a dict {'text':..., 'row_index':...}
        if isinstance(item, dict):
            raw = item.get("text", "") or ""
            row_index = item.get("row_index", None)
        else:
            raw = item or ""
            row_index = None

        # handle missing
        if not raw or not raw.strip():
            continue

        # chunk if needed
        chunks = split_text(raw, max_chars=max_chars)
        for chunk_idx, chunk in enumerate(chunks):
            proc = preprocess_text(chunk)
            doc = {
                "id": current_id,
                "source_file": source_file,
                "row_index": row_index if row_index is not None else -1,
                "chunk_index": chunk_idx,
                "raw_text": proc["raw_text"],
                "clean_text": proc["clean_text"],
                "normalized_text": proc["normalized_text"],
                "tokens": proc["tokens"]
            }
            docs.append(doc)
            current_id += 1

    return docs, current_id
