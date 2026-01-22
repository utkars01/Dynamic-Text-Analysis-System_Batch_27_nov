from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def extractive_summary(texts, n=5):
    tfidf = TfidfVectorizer(stop_words="english").fit_transform(texts)
    scores = np.array(tfidf.sum(axis=1)).flatten()
    return texts.iloc[scores.argsort()[-n:]]
