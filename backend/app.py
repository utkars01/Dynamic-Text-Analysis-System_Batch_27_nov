from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import joblib
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize

# ================= FASTAPI INIT =================
app = FastAPI(
    title="AI Narrative Nexus API",
    version="1.0.0"
)

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= NLTK =================
nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("vader_lexicon")
nltk.download("punkt")

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()
sid = SentimentIntensityAnalyzer()

# ================= LOAD MODELS =================
tfidf_vectorizer = joblib.load("models/tfidf_vectorizer.pkl")
nmf_model = joblib.load("models/nmf_topic_model.pkl")

topic_names = {
    0: "Opinions",
    1: "Bad Acting",
    2: "TV Shows",
    3: "Performance",
    4: "Worst Movies",
    5: "Story & Plot",
    6: "Film Work",
    7: "Memories",
    8: "Comedy",
    9: "Family",
    10: "Horror",
    11: "Adaptations"
}

# ================= REQUEST SCHEMA =================
class ReviewRequest(BaseModel):
    text: str

# ================= UTILITIES =================
def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"<.*?>", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)

    tokens = [
        lemmatizer.lemmatize(word)
        for word in text.split()
        if word not in stop_words and len(word) > 2
    ]
    return " ".join(tokens)


def classify_sentiment(score: float) -> str:
    if score >= 0.45:
        return "Positive"
    elif score <= -0.45:
        return "Negative"
    return "Neutral"


def recommendation(sent_score: float, topic_conf: float) -> str:
    if sent_score >= 0.6:
        return "Recommended 🎯"
    elif sent_score >= 0.3 and topic_conf >= 20:
        return "Worth Watching 👍"
    elif sent_score >= 0.3:
        return "Positive but Uncertain 🤔"
    elif -0.2 < sent_score < 0.2:
        return "Mixed / Depends ⚖️"
    return "Not Recommended 🚫"


def summarize_review(text: str, max_sentences: int = 3) -> str:
    sentences = sent_tokenize(text)
    if len(sentences) <= max_sentences:
        return text

    clean_words = clean_text(text).split()
    freq = Counter(clean_words)

    sentence_scores = {}
    for sent in sentences:
        for word in clean_text(sent).split():
            if word in freq:
                sentence_scores[sent] = sentence_scores.get(sent, 0) + freq[word]

    top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)
    return " ".join(top_sentences[:max_sentences])

# ================= HEALTH =================
@app.get("/")
def health():
    return {"status": "AI Narrative Nexus API is running"}

# ================= ANALYZE TEXT =================
@app.post("/analyze")
def analyze_review(data: ReviewRequest):
    if not data.text.strip():
        return {"error": "Empty review text"}

    raw_text = data.text[:3000]

    clean_str = clean_text(raw_text)
    words = clean_str.split()
    word_frequencies = dict(Counter(words).most_common(25))

    sent_score = sid.polarity_scores(raw_text)["compound"]
    sentiment_label = classify_sentiment(sent_score)

    vector = tfidf_vectorizer.transform([clean_str])
    topic_dist = nmf_model.transform(vector)[0]

    total = topic_dist.sum() or 1.0
    topic_percentages = {
        topic_names[i]: round((score / total) * 100, 2)
        for i, score in enumerate(topic_dist)
        if score > 0.01
    }

    primary_topic = max(topic_percentages, key=topic_percentages.get)
    topic_confidence = topic_percentages[primary_topic]

    topic_breakdown = dict(
        sorted(topic_percentages.items(), key=lambda x: x[1], reverse=True)[:5]
    )

    decision = recommendation(sent_score, topic_confidence)
    summary = summarize_review(raw_text)

    return {
        "summary": summary,
        "sentiment": sentiment_label,
        "sentiment_score": round(sent_score, 3),
        "decision": decision,
        "primary_topic": primary_topic,
        "topic_breakdown": topic_breakdown,
        "word_frequencies": word_frequencies
    }

# ================= ANALYZE FILE =================
@app.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode(errors="ignore")

    clean_str = clean_text(text)
    words = clean_str.split()
    word_freq = dict(Counter(words).most_common(30))

    sent_score = sid.polarity_scores(text)["compound"]
    sentiment_label = classify_sentiment(sent_score)

    vector = tfidf_vectorizer.transform([clean_str])
    topic_dist = nmf_model.transform(vector)[0]

    total = topic_dist.sum() or 1.0
    topic_percentages = {
        topic_names[i]: round((score / total) * 100, 2)
        for i, score in enumerate(topic_dist)
    }

    primary_topic = max(topic_percentages, key=topic_percentages.get)
    topic_confidence = topic_percentages[primary_topic]

    topic_breakdown = dict(
        sorted(topic_percentages.items(), key=lambda x: x[1], reverse=True)[:3]
    )

    decision = recommendation(sent_score, topic_confidence)

    return {
        "summary": summarize_review(text),
        "sentiment": sentiment_label,
        "sentiment_score": round(sent_score, 3),
        "decision": decision,
        "primary_topic": primary_topic,
        "topic_breakdown": topic_breakdown,
        "word_frequencies": word_freq
    }
