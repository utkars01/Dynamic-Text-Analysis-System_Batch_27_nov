from pathlib import Path
import joblib
import numpy as np
import json

# Path: app/models/sentiment/
MODEL_DIR = Path(__file__).resolve().parent.parent / "models" / "sentiment"

_lr_model = None
_tfidf = None
_label_map = None


def _load_assets():
    global _lr_model, _tfidf, _label_map

    if _lr_model is None:
        # sklearn artifacts
        _lr_model = joblib.load(MODEL_DIR / "logistic_model.pkl")
        _tfidf = joblib.load(MODEL_DIR / "tfidf_vectorizer.pkl")

        # JSON label map
        with open(MODEL_DIR / "label_map.json", "r", encoding="utf-8") as f:
            _label_map = json.load(f)

        # ensure keys are ints (JSON makes them strings)
        _label_map = {int(k): v for k, v in _label_map.items()}


def infer_sentiment(texts: list[str]) -> list[dict]:
    _load_assets()

    X = _tfidf.transform(texts)
    probs = _lr_model.predict_proba(X)
    preds = _lr_model.predict(X)

    classes = _lr_model.classes_  # e.g. [-1, 0, 1]

    results = []
    for pred, prob in zip(preds, probs):
        pred = int(pred)  # already the true label

        results.append({
            "sentiment": _label_map[pred],  # ✅ DIRECT
            "confidence": float(np.max(prob)),
            "scores": {
                _label_map[int(cls)]: float(prob[i])
                for i, cls in enumerate(classes)
            }
        })

    return results

