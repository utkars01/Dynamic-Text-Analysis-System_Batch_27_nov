import os
os.environ["TRANSFORMERS_NO_TF"]="1"
import pandas as pd
import numpy as np
import nltk
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline

# Download tokenizer (first time only)
nltk.download("punkt")

# ================= CONFIG =================
INPUT_CSV = "imdb_reviews_with_topics.csv"
OUTPUT_DIR = "summaries"
SAMPLES_PER_GROUP = 50     # prevents RAM overload
EXTRACTIVE_SENTENCES = 3

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ================= EXTRACTIVE SUMMARY =================
def extractive_summary(text, n_sentences=3):
    sentences = sent_tokenize(text)

    if len(sentences) <= n_sentences:
        return text

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(sentences)
    scores = tfidf.sum(axis=1).A1

    ranked = sorted(
        ((score, idx, sent) for idx, (score, sent) in enumerate(zip(scores, sentences))),
        reverse=True
    )

    selected = sorted(ranked[:n_sentences], key=lambda x: x[1])
    return " ".join(sent for _, _, sent in selected)


# ================= ABSTRACTIVE SUMMARY =================
print("Loading abstractive summarizer (T5-small)...")
abstractive_model = pipeline(
    "summarization",
    model="t5-small",
    tokenizer="t5-small",
    framework="pt"
    )

def abstractive_summary(text):
    text = text[:2000]  # VERY IMPORTANT (RAM safety)
    summary = abstractive_model(
        "summarize: " + text,
        max_length=120,
        min_length=10,
        do_sample=False
    )
    return summary[0]["summary_text"]


# ================= MAIN LOGIC =================
def generate_summaries(df):
    topics = sorted(df["topic"].unique())

    for topic in topics:
        for label, sentiment in [(0, "negative"), (1, "positive")]:
            subset = df[
                (df["topic"] == topic) &
                (df["label"] == label)
            ]

            if subset.empty:
                continue

            sampled_texts = subset["text"].sample(
                min(SAMPLES_PER_GROUP, len(subset)),
                random_state=42
            ).tolist()

            combined_text = " ".join(sampled_texts)

            # -------- Extractive --------
            extractive = extractive_summary(
                combined_text,
                n_sentences=EXTRACTIVE_SENTENCES
            )

            extractive_path = f"{OUTPUT_DIR}/topic_{topic}_{sentiment}_extractive.txt"
            with open(extractive_path, "w", encoding="utf-8") as f:
                f.write(extractive)

            # -------- Abstractive --------
            abstractive = abstractive_summary(combined_text)

            abstractive_path = f"{OUTPUT_DIR}/topic_{topic}_{sentiment}_abstractive.txt"
            with open(abstractive_path, "w", encoding="utf-8") as f:
                f.write(abstractive)

            print(f"Saved summaries for Topic {topic} | {sentiment.capitalize()}")


# ================= RUN =================
if __name__ == "__main__":
    print("Loading dataset with topics and sentiment...")
    df = pd.read_csv(INPUT_CSV)

    generate_summaries(df)

    print("\n✅ All summaries saved successfully in the 'summaries/' folder.")

def summarize_text(text):
    """
    Generate abstractive summary for UI usage.
    Returns None if text is already concise.
    """

    # Skip summarization for short inputs
    if len(text.split()) < 40:
        return None

    # Token-aware truncation (SAFE)
    inputs = abstractive_model.tokenizer(
        "summarize: " + text,
        max_length=512,
        truncation=True,
        return_tensors="pt"
    )

    summary_ids = abstractive_model.model.generate(
        inputs["input_ids"],
        max_new_tokens=120,      # output length ONLY
        min_new_tokens=30,
        do_sample=False,
        no_repeat_ngram_size=2
    )

    summary = abstractive_model.tokenizer.decode(
        summary_ids[0],
        skip_special_tokens=True
    )

    return summary.strip()


