from src.preprocessing import load_imdb_with_labels, preprocess_dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix
import matplotlib
matplotlib.use('Agg') # Use a non-interactive backend
import joblib
import os


def main():
    print("Loading IMDB reviews dataset...")
    df = load_imdb_with_labels()
    df = preprocess_dataset(df)
    sentiment_counts = df['label'].value_counts().sort_index()
    #1 fig
    plt.figure()
    plt.bar(sentiment_counts.index, sentiment_counts.values, color=['blue', 'orange'])
    plt.xticks(sentiment_counts.index, ['Negative', 'Positive'])
    plt.xlabel('Sentiment')
    plt.ylabel('Number of Reviews')
    plt.title('Distribution of Sentiments in IMDB Reviews Dataset')
    plt.savefig('sentiment_distribution.png')
    plt.close()

    X=df["clean_text"]

    y=df["label"]
    #training modellll
    X_train, X_test, y_train, y_test = train_test_split(X, y,
         test_size=0.3,stratify=y, random_state=42)
    print("Train size: ",X_train.shape[0])
    print("Test size: ",X_test.shape[0])
    vectorizer = TfidfVectorizer(
        max_features=5000,
        max_df=0.85,
        min_df=5,
        ngram_range=(1,2),
        stop_words='english'
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    model = LogisticRegression(
        max_iter=1000,
        solver='liblinear',
        )
    #4 fig 
    feature_names = vectorizer.get_feature_names_out()
    model.fit(X_train_tfidf, y_train)
    coef = model.coef_[0]
    top_positive_indices = np.argsort(coef)[-10:]
    top_negative_indices = np.argsort(coef)[:10]
    #positive words
    plt.figure()
    plt.barh([feature_names[i] for i in top_positive_indices], coef[top_positive_indices], color='green')
    plt.title('Top 10 Positive Words Influencing Sentiment')
    plt.xlabel('weight')
    plt.savefig('top_positive_words.png')
    plt.close()
    #negative words
    plt.figure()
    plt.barh([feature_names[i] for i in top_negative_indices], coef[top_negative_indices], color='red')
    plt.title('Top 10 Negative Words Influencing Sentiment')
    plt.xlabel('weight')
    plt.savefig('top_negative_words.png')
    plt.close()
    #prediction and evaluation
    y_pred = model.predict(X_test_tfidf)
    #2 fig
    cm=confusion_matrix(y_test, y_pred)
    plt.figure()
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Confusion Matrix')
    plt.colorbar()
    plt.xticks(np.arange(2), ['Negative', 'Positive'])
    plt.yticks(np.arange(2), ['Negative', 'Positive'])
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title('Confusion Matrix of Sentiment Classification')
    for i in range(2):
        for j in range(2):
            plt.text(j, i, cm[i, j], horizontalalignment="center", color="white" if cm[i, j] > cm.max()/2. else "black")
    plt.savefig('confusion_matrix.png')
    plt.close()
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("Accuracy Score:", accuracy_score(y_test, y_pred))
    models=["Naive Bayes(Baseline)","Logistic Regression"]
    accuracies=[0.82, accuracy_score(y_test, y_pred)] #Example accuracies
    #3 fig
    plt.figure()
    plt.bar(models, accuracies, color=['green', 'purple'])
    plt.xlabel('Models')
    plt.ylabel('Accuracy')
    plt.title('Model Accuracy Comparison')
    plt.ylim([0, 1])
    plt.savefig('model_accuracy_comparison.png')
    plt.close()
    BASE_DIR=os.path.dirname(os.path.abspath(__file__))
    joblib.dump(model, os.path.join(BASE_DIR, "sentiment_model.pkl"))
    joblib.dump(vectorizer, os.path.join(BASE_DIR, "tfidf_vectorizer.pkl"))
    print("Model and vectorizer saved to disk.")

if __name__ == "__main__":
    main()
def predict_sentiment(text):
    """
    Predict sentiment for a single input text
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    model = joblib.load(os.path.join(BASE_DIR, "sentiment_model.pkl"))
    vectorizer = joblib.load(os.path.join(BASE_DIR, "tfidf_vectorizer.pkl"))

    X = vectorizer.transform([text])
    prediction = model.predict(X)[0]
    confidence = model.predict_proba(X).max() * 100

    sentiment = "Positive" if prediction == 1 else "Negative"
    return sentiment, confidence
