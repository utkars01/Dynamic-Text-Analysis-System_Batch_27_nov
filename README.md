# 🍽️ Food Review Analysis Platform

A dynamic text analysis system built with **Streamlit** that allows users to upload or paste reviews, then performs:
- Sentiment Analysis (positive/negative/neutral with charts)
- Topic Modeling (dominant keywords + wordcloud)
- Summarization (abstractive summary of the review)
- One‑click DOCX Report (mirrors UI visuals)

---

## 🚀 Features
- Upload `.txt`, `.csv`, `.docx` files or paste text directly
- Sentiment analysis with **gauge + bar chart (with % labels)**
- Dominant topic keywords with **wordcloud visualization**
- Abstractive summary using transformer models
- Insights + recommendations generated automatically
- Downloadable DOCX report (summary, sentiment chart, wordcloud, dominant keywords, insights, recommendations)

---
**UI Overview**
![UI Overview](Dynamic-Text-Analysis-System_Batch_27_nov\text_analysis_platform\assets\ui_overview.png)
**Sentiment Analysis**
![Sentiment Analysis](Dynamic-Text-Analysis-System_Batch_27_nov\text_analysis_platform\assets\sentiment_ui.png)
**Topic modeling**
![Topic Modeling](Dynamic-Text-Analysis-System_Batch_27_nov\text_analysis_platform\assets\topic_modeling_ui.png)
**Summary and Insights**
![Summary and Insights](Dynamic-Text-Analysis-System_Batch_27_nov\text_analysis_platform\assets\summary_insights_ui.png)

## 📖 Usage
- Upload a file or paste text in the input box.
- Click 🚀 Analyze Text.
- Explore results in tabs:
- ❤️ Sentiment Analysis
- ☁️ Topic Analysis
- 📝 Summary & Insights
- 📄 Report
- Download the DOCX report.

---


## 📂 Project Structure

text_analysis_platform/ 
 ├── app.py                  # Streamlit app 
 ├── reporting.py            
 ├── summarizer.py           
 ├── validation.py           # Input checks 
 ├── sentiment_analysis.ipynb 
 ├── topic_modeling.ipynb 
 ├── requirements.txt        # Dependencies 
 ├── assets/                 
 +     


## 🛠️ Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/springboard5678x/Dynamic-Text-Analysis-System_Batch_27_nov.git
   cd Dynamic-Text-Analysis-System_Batch_27_nov
2. Install dependencies:
pip install -r requirements.txt

3. Download spaCy model:
python -m spacy download en_core_web_sm

4. Download NLTK stopwords (in Python):
import nltk
nltk.download("stopwords")


▶️ Run the App
streamlit run text_analysis_platform/app.py

📝 License
This project is licensed under the MIT License — see the LICENSE file for details




