from src.preprocessing import load_imdb_with_labels, preprocess_dataset
#from src.LDA import train_lda, get_lda, evaluate_lda
from src.NMF import trainnmf, getnmf, evaluatenmf

def main():
    print("Loading IMDB dataset...")
    df = load_imdb_with_labels()

    # Use a small sample (VERY IMPORTANT for speed)
    df = df.sample(n=1000, random_state=42).reset_index(drop=True)

    print("Preprocessing text...")
    df = preprocess_dataset(df)
    texts = df["clean_text"].tolist()

    # ================= LDA =================
    """print("\n--- LDA MODEL ---")
    lda, corpus, dictionary, tokenized = train_lda(texts, num=7)

    topic_coh, overall_coh, lda_perp = evaluate_lda(
        lda, tokenized, dictionary, corpus
    )

    for tid, words, score in topic_coh:
        print(f"LDA Topic {tid} (Coherence: {score:}): {words}")

    print(f"\nLDA Coherence: {overall_coh:}")
    print(f"LDA Perplexity: {lda_perp:}")"""

    # ================= NMF =================
    print("\n--- NMF MODEL ---")
    nmf, tfidf, vectorizer, tokenized = trainnmf(texts)
    import joblib
    joblib.dump(nmf, "nmf_model.joblib")
    joblib.dump(vectorizer, "tfidf_vectorizer.joblib")
    nmf_topics = getnmf(nmf, vectorizer, numw=8)
    for idx, words in nmf_topics:
        print(f"NMF Topic {idx}: {words}")
    nmf_coh = evaluatenmf(nmf, vectorizer, tokenized, numw=8)
    print("NMF Coherence:", nmf_coh)

    #------STORE TOPIC ASSIGNMENT------
    W=nmf.transform(tfidf)
    df['topic']=W.argmax(axis=1)
    print('Topic assignment added to dataframe.')
    print(df[['text','topic']].head())

    #--------SAVE DF WITH TOPICS TO CSV--------
    df.to_csv('imdb_reviews_with_topics.csv',index=False)
    print("Dataframe with topic assignments saved to 'imdb_reviews_with_topics.csv'.")

    print("Topic Distribution:")
    print(df['topic'].value_counts().sort_index())


if __name__ == "__main__":
    main()

