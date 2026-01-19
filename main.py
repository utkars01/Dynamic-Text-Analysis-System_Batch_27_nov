from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
import re
import PyPDF2
import docx
import io
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# Download NLTK resources
for res in ['punkt', 'stopwords', 'wordnet', 'omw-1.4', 'vader_lexicon']:
    try:
        nltk.download(res, quiet=True)
    except:
        pass

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models
vectorizer = joblib.load('tfidf.pkl')
nmf_model = joblib.load('nmf_25.pkl')
tokenizer = AutoTokenizer.from_pretrained("bart-cnn-finetuned")
model = AutoModelForSeq2SeqLM.from_pretrained("bart-cnn-finetuned")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
sia = SentimentIntensityAnalyzer()

TOPIC_LABELS = {
    "Topic 0": "Family and Relationships", "Topic 1": "Club Football",
    "Topic 2": "East Asian Culture and Politics", "Topic 3": "Law Enforcement and Crime",
    "Topic 4": "Air Travel and Aviation", "Topic 5": "Party Politics and Political Leadership",
    "Topic 6": "Healthcare and Medicine", "Topic 7": "Economy and Finance",
    "Topic 8": "Education and Schooling", "Topic 9": "Political Institutions and Political Parties",
    "Topic 10": "Law and Justice - Court and Trials", "Topic 11": "International Politics and Conflict",
    "Topic 12": "Weather and Natural Disasters", "Topic 13": "Technology and Social Media",
    "Topic 14": "Women and Society", "Topic 15": "Transport and Traffic Accidents/Incidents",
    "Topic 16": "Celebrity, Fashion, and Elite Public", "Topic 17": "Middle Eastern Conflicts",
    "Topic 18": "Pets and Animals", "Topic 19": "Ukraine and Russia - Conflict",
    "Topic 20": "Manchester United Football Club", "Topic 21": "Afghanistan and Pakistan - Military Conflicts",
    "Topic 22": "Infectious Disease Outbreaks and Public Health", "Topic 23": "International Football",
    "Topic 24": "Middle Eastern Politics"
}

TOPIC_KEYWORDS = {
    "Topic 0": "child mother family baby parent girl daughter boy father son",
    "Topic 1": "league club season liverpool goal chelsea premier arsenal player game",
    "Topic 2": "china chinese beijing japan hong government country kong japanese xinhua",
    "Topic 3": "police officer said man arrested shooting shot suspect investigation gun",
    "Topic 4": "flight plane passenger airline airport pilot aircraft air crew said",
    "Topic 5": "mr labour minister cameron mp party tory prime said miliband",
    "Topic 6": "patient hospital cancer doctor nh health treatment drug dr care",
    "Topic 7": "cent tax price year bank uk rate government pay million",
    "Topic 8": "school student teacher pupil education university college high parent transcript",
    "Topic 9": "obama president republican house clinton state senate democrat white american",
    "Topic 10": "court judge case prison trial said sentence victim justice charge",
    "Topic 11": "korea north korean south kim nuclear pyongyang jong missile seoul",
    "Topic 12": "water said storm weather snow area city island wind rain",
    "Topic 13": "apple user google app phone company device iphone facebook mobile",
    "Topic 14": "woman like say people im film think dont life really",
    "Topic 15": "car driver vehicle road driving crash accident race speed bus",
    "Topic 16": "prince royal queen duchess william palace duke princess kate harry",
    "Topic 17": "syria syrian isi iraq iraqi rebel group islamic government force",
    "Topic 18": "dog animal pet cat owner puppy vet home zoo rspca",
    "Topic 19": "ukraine russia russian putin ukrainian moscow crimea kiev separatist donetsk",
    "Topic 20": "van united gaal manchester rooney louis trafford uniteds persie player",
    "Topic 21": "afghanistan pakistan taliban afghan attack military said force soldier troop",
    "Topic 22": "ebola virus health outbreak disease liberia africa sierra leone infected",
    "Topic 23": "cup england world game match team player win final tournament",
    "Topic 24": "israel israeli palestinian iran gaza hamas nuclear iranian netanyahu said"
}

class TextInput(BaseModel):
    text: str

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def preprocess_text(text):
    text = clean_text(text)
    tokens = word_tokenize(text)
    tokens = [lemmatizer.lemmatize(tok) for tok in tokens if tok not in stop_words]
    return " ".join(tokens)

@app.post("/api/topic")
async def analyze_topic(input_data: TextInput):
    try:
        processed = preprocess_text(input_data.text)
        tfidf_vec = vectorizer.transform([processed])
        topic_dist = nmf_model.transform(tfidf_vec)
        dominant_idx = np.argmax(topic_dist)
        topic_key = f"Topic {dominant_idx}"
        topic_label = TOPIC_LABELS.get(topic_key, "Unknown")
        
        # Generate word cloud
        wordcloud_base64 = None
        topic_keywords_str = TOPIC_KEYWORDS.get(topic_key, "")
        if topic_keywords_str:
            topic_word_set = set(topic_keywords_str.split())
            input_word_set = set(clean_text(input_data.text).split())
            matched_words = topic_word_set.intersection(input_word_set)
            
            if matched_words:
                matched_str = " ".join(matched_words)
                wordcloud = WordCloud(
                    width=800,
                    height=400,
                    background_color='#1e1b4b',
                    colormap='plasma',
                    contour_color='#6366f1',
                    contour_width=2
                ).generate(matched_str)
                
                fig, ax = plt.subplots(figsize=(10, 5))
                fig.patch.set_facecolor('#1e1b4b')
                ax.set_facecolor('#1e1b4b')
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis("off")
                
                buffer = BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight', facecolor='#1e1b4b')
                buffer.seek(0)
                wordcloud_base64 = base64.b64encode(buffer.read()).decode()
                plt.close(fig)
        
        # Get top 5 topics
        topic_weights = topic_dist[0]
        top_indices = topic_weights.argsort()[-5:][::-1]
        top_distribution = [
            {
                "label": TOPIC_LABELS.get(f"Topic {i}", f"Topic {i}")[:40],
                "score": float(topic_weights[i])
            }
            for i in top_indices
        ]
        
        return {
            "label": topic_label,
            "key": topic_key,
            "score": float(topic_dist[0][dominant_idx]),
            "wordcloud": wordcloud_base64,
            "distribution": top_distribution
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sentiment")
async def analyze_sentiment(input_data: TextInput):
    try:
        sentiment = sia.polarity_scores(input_data.text)
        compound = sentiment['compound']
        if compound >= 0.05:
            sentiment_label = "Positive"
        elif compound <= -0.05:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Neutral"
        
        return {
            "label": sentiment_label,
            "compound": float(compound),
            "positive": float(sentiment['pos']),
            "neutral": float(sentiment['neu']),
            "negative": float(sentiment['neg'])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/summary")
async def generate_summary(input_data: TextInput):
    try:
        inputs = tokenizer(input_data.text, return_tensors="pt", max_length=1024, truncation=True).to(device)
        summary_ids = model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=150,
            min_length=40,
            num_beams=4,
            length_penalty=2.0,
            early_stopping=True
        )
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = ""
        
        if file.content_type == "text/plain":
            text = content.decode("utf-8")
        elif file.content_type == "application/pdf":
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = "".join([page.extract_text() or "" for page in reader.pages])
        elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(io.BytesIO(content))
            text = "\n".join([para.text for para in doc.paragraphs])
        
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
