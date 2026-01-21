import json
from pathlib import Path
from typing import List, Dict
import csv
import os

DATA_DIR = Path(__file__).resolve().parents[0].joinpath("..", "data", "processed").resolve()

def _ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

CORPUS_PATH = DATA_DIR.joinpath("corpus.json")
PREVIEW_CSV = DATA_DIR.joinpath("preprocessed_preview.csv")

def load_corpus() -> List[Dict]:
    _ensure_dirs()
    if not CORPUS_PATH.exists():
        return []
    with CORPUS_PATH.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_corpus(corpus: List[Dict]) -> None:
    _ensure_dirs()
    with CORPUS_PATH.open("w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)

def append_documents(docs: List[Dict]) -> None:
    """
    Load corpus, extend with docs, save back. Also update preview CSV.
    """
    _ensure_dirs()
    corpus = load_corpus()
    # we assume incoming docs have id set properly
    corpus.extend(docs)
    save_corpus(corpus)
    _write_preview_csv(corpus)

def _write_preview_csv(corpus: List[Dict]) -> None:
    """
    Write preview CSV with columns:
      id, source_file, row_index, normalized_text (truncated to 500 chars), num_tokens
    """
    _ensure_dirs()
    fieldnames = ["id", "source_file", "row_index", "normalized_text", "num_tokens"]
    tmp_path = PREVIEW_CSV.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for d in corpus:
            normalized = d.get("normalized_text", "")
            writer.writerow({
                "id": d.get("id"),
                "source_file": d.get("source_file", ""),
                "row_index": d.get("row_index", -1),
                "normalized_text": (normalized[:500] + "...") if len(normalized) > 500 else normalized,
                "num_tokens": len(d.get("tokens", []))
            })
    # atomically replace
    tmp_path.replace(PREVIEW_CSV)
