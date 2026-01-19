from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from gensim import corpora
from gensim.models import CoherenceModel
from gensim.models import Phrases
from gensim.models.phrases import Phraser

numt=4 #number of topics after tuning

def bigrams(texts):
    tokenized=[text.split()for text in texts]
    phrases = Phrases(tokenized, 
                      min_count=10, 
                      threshold=10
                      )
    bigram = Phraser(phrases)
    tokenized = [bigram[doc] for doc in tokenized]
    texts_bigram=[ ' '.join(doc) for doc in tokenized ]
    return texts_bigram, tokenized

def trainnmf(texts,vectorizer=None):

    texts_bigram, tokenized = bigrams(texts)

    if vectorizer is None:
        vectorizer=TfidfVectorizer(
            max_features=None,
            max_df=0.75,
            min_df=15,
            ngram_range=(1,2),
            stop_words='english'
        )
        tfidf=vectorizer.fit_transform(texts_bigram)
    else:
        tfidf=vectorizer.transform(texts_bigram)
    
    nmf=NMF(
        n_components=numt,
        init='nndsvd',
        max_iter=700,
        random_state=42,    
    )
    nmf.fit(tfidf)

    return nmf,tfidf,vectorizer,tokenized

def getnmf(nmf,vectorizer,numw=8):
    topics=[]
    feature_names = vectorizer.get_feature_names_out()
    for topic_idx,topic in enumerate(nmf.components_):
        words=[feature_names[i] for i in topic.argsort()[:-numw - 1:-1]]
        topics.append((topic_idx,words))
    return topics

def nmfcoherence(nmf,vectorizer,tokenized,numw=8):
    topics=getnmf(nmf,vectorizer,numw)

    formatted_topics=[words for _,words in topics]

    dictionary=corpora.Dictionary(tokenized)
    dictionary.filter_extremes(no_below=5, no_above=0.75)

    coherencemodel=CoherenceModel(
        topics=formatted_topics,
        texts=tokenized,
        dictionary=dictionary,
        coherence='c_v'
    )
    return coherencemodel.get_coherence()

def evaluatenmf(nmf,vectorizer,tokenized,numw=8):
    return nmfcoherence(nmf,vectorizer,tokenized,numw)

def infer_nmf_topics(nmf,vectorizer,text,numw=8):
    tfidf=vectorizer.transform([text])
    W=nmf.transform(tfidf)
    topic_id=W.argmax(axis=1)[0]

    feature_names = vectorizer.get_feature_names_out()
    topic=nmf.components_[topic_id]
    top_indices=topic.argsort()[-numw:][::-1]
    top_words=[feature_names[i] for i in top_indices]
    return topic_id, top_words