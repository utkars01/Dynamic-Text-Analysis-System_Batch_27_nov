# News Summarizer - React + FastAPI

A full-stack news analysis application with topic modeling, sentiment analysis, and AI summarization.

## Setup Instructions

### Backend (FastAPI)

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make sure model files are in the backend directory:
   - `tfidf.pkl`
   - `nmf_25.pkl`
   - `bart-cnn-finetuned/` folder

4. Run the FastAPI server:
```bash
python main.py
```

Backend will run on `http://localhost:8000`

### Frontend (React)

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies (if not already done):
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

Frontend will run on `http://localhost:5173`

## Usage

1. Start both backend and frontend servers
2. Open `http://localhost:5173` in your browser
3. Either paste text or upload a file (.txt, .docx, .pdf)
4. Click "Summarize Now"
5. View results:
   - **Topic Analysis**: Detected theme and confidence score
   - **Sentiment Analysis**: Overall sentiment with distribution
   - **Summarization**: AI-generated summary

## API Endpoints

- `POST /api/analyze` - Analyze text (topic, sentiment, summary)
- `POST /api/upload` - Upload and extract text from file

## Tech Stack

**Frontend:**
- React + Vite
- Tailwind CSS
- Fetch API

**Backend:**
- FastAPI
- Transformers (BART)
- NLTK (VADER sentiment)
- Scikit-learn (NMF topic modeling)
