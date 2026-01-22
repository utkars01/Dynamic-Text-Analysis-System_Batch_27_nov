from gensim import corpora
from gensim.models import LdaModel
from gensim.models.coherencemodel import CoherenceModel

def train_lda(texts, num_topics=5):
    tokens = [t.split() for t in texts if t.strip()]
    dictionary = corpora.Dictionary(tokens)
    corpus = [dictionary.doc2bow(t) for t in tokens]

    lda = LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=num_topics,
        passes=5,
        random_state=42
    )

    lda.save("models/lda_model.model")
    dictionary.save("models/lda_dictionary.dict")

    coherence_model = CoherenceModel(
        model=lda,
        texts=tokens,
        dictionary=dictionary,
        coherence='c_v'
    )

    coherence_score = coherence_model.get_coherence()

    return lda, lda.print_topics(), coherence_score
