from gensim.models import LdaModel
from gensim import corpora
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent

LDA_DIR = BASE_DIR / "models" / "lda"


lda_model = LdaModel.load(str(LDA_DIR / "lda_15_topics.gensim"))
dictionary = corpora.Dictionary.load(str(LDA_DIR / "lda_dictionary.gensim"))

with open(LDA_DIR / "topic_labels.json", "r") as f:
    TOPIC_LABELS = json.load(f)


def infer_topics(tokens, top_n=3):
    
    bow = dictionary.doc2bow(tokens)
    topics = lda_model.get_document_topics(bow)

    topics = sorted(topics, key=lambda x: x[1], reverse=True)[:top_n]

    return [
        {
            "topic_id": tid,
            "label": TOPIC_LABELS.get(str(tid), f"Topic {tid}"),
            "probability": round(float(prob), 4)
        }
        for tid, prob in topics
    ]
