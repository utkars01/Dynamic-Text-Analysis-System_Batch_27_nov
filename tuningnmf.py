from src.preprocessing import load_imdb_rottentomatoes, preprocess_dataset
from src.NMF import trainnmf, getnmf, evaluatenmf
from gensim.models import CoherenceModel
from gensim.models import LdaModel
from gensim import corpora
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from multiprocessing import freeze_support  
import matplotlib.pyplot as plt


def main():
    print("Loading IMDB dataset and Rotten Tomatoes dataset...")

    df = load_imdb_rottentomatoes()
    # Use a small sample (VERY IMPORTANT for speed)
    df = df.sample(n=1000, random_state=42)
    df=preprocess_dataset(df)

    texts = df["clean_text"].tolist()
    tokenized=[text.split()for text in texts]

    from gensim.models import Phrases
    from gensim.models.phrases import Phraser
    phrases = Phrases(tokenized, min_count=10, threshold=10)
    bigram = Phraser(phrases)
    tokenized = [bigram[doc] for doc in tokenized]

    texts_bigram=[ ' '.join(doc) for doc in tokenized ]

    domain_stopwords = [
        "movie","film","story","character","characters",
        "scene","scenes","actor","actors","acting",
        "director","watch","watching","one"
    ]
    #NMF
    vectoriser=TfidfVectorizer(
        max_features=None,
        max_df=0.75,
        min_df=15,
        ngram_range=(1,2),
        stop_words='english'
    )
    tfidf=vectoriser.fit_transform(texts_bigram)

    k_vals=[]
    coherences=[]

    for k in range(2,7):
        nmf=NMF(
            n_components=k,
            init='nndsvd',
            max_iter=700,
            random_state=42,    
        )
        nmf.fit(tfidf)
        coh=evaluatenmf(nmf,vectoriser,tokenized)
        print(f"NMF Coherence for {k} topics: {coh}")
        k_vals.append(k)
        coherences.append(coh)

    plt.figure()
    plt.plot(k_vals,coherences,marker='o')
    plt.xlabel("Number of topics")
    plt.ylabel("Coherence c_v")
    plt.title("NMF coherence plot")
    plt.grid(True)
    plt.savefig("nmf_coherence_plot.png", dpi=300)
    plt.show()

if __name__ == "__main__":
    freeze_support()
    main()