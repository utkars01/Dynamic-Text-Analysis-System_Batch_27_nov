
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
from docx import Document

def ingest_txt(path: Path) -> List[Dict]:
    
    raw_txt = path.read_text(encoding="utf-8", errors="ignore")
    return [{"text": raw_txt, "row_index": None}]

def ingest_csv(path: Path, text_column: str = "text") -> List[Dict]:
    
    df = pd.read_csv(path, dtype=str)  # read as strings to avoid dtype surprises
    if text_column not in df.columns:
        raise ValueError(f"CSV must contain a '{text_column}' column.")
    texts = []
    for idx, val in df[text_column].fillna("").astype(str).items():
        if val is None:
            continue
        v = val.strip()
        if v == "":
            continue
        texts.append({"text": v, "row_index": int(idx)})
    return texts

def ingest_docx(path: Path) -> List[Dict]:
    
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text and p.text.strip() != ""]
    full_text = "\n".join(paragraphs)
    return [{"text": full_text, "row_index": None}]

def ingest_file(path: Path, text_column: str = "text") -> List[Dict]:
    
    ext = path.suffix.lower()
    if ext == ".txt":
        return ingest_txt(path)
    elif ext == ".csv":
        return ingest_csv(path, text_column=text_column)
    elif ext == ".docx":
        return ingest_docx(path)
    else:
        raise ValueError(f"Unsupported extension: {ext}")
