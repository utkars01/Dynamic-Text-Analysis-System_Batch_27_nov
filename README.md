# 🧠 AI Text Analysis Platform

**Dynamic-Text-Analysis-System_Batch_27_nov**

A professional AI-powered NLP dashboard built using **Python** and **Streamlit** to analyze large-scale text data, discover hidden topics, understand sentiment, and generate executive-ready insights with downloadable reports.

---

## 📌 Project Overview

The **AI Text Analysis Platform** is an end-to-end text analytics system designed to process unstructured textual data such as:

- Customer reviews  
- Employee feedback  
- Survey responses  
- Free-form documents  

The system automatically performs topic modeling, sentiment analysis, and visual analytics, helping users convert raw text into meaningful insights with minimal effort.

This project is suitable for:

- Academic final submissions  
- HR analytics  
- Business intelligence  
- NLP learning and experimentation  

---

## 🖥️ Application Workflow

### Home Page
- Introduction to the platform  
- Who can use the system  
- How the system works  

### Input Selection
- Upload a CSV file with text columns  
- OR enter manual text for analysis  

### AI Analysis
- Topic modeling using **TF-IDF + NMF**  
- Sentiment classification (Positive / Neutral / Negative)  

### Results Dashboard
- Topic modeling table  
- Topic share donut chart  
- Document distribution bar chart  
- Sentiment distribution chart  
- Topic × Sentiment stacked bar chart  
- Word cloud visualization  

### Executive Summary
- Automatically generated textual summary  
- Highlights dominant topic and overall sentiment  

### Download Report
- One-click DOCX report  
- Includes tables, charts, word cloud, and insights  

---

## ✨ Key Features

- CSV and text input support  
- Automatic topic discovery  
- Sentiment analysis using VADER  
- Interactive visualizations  
- Word cloud generation  
- Executive summary auto-generation  
- Professional dark-themed UI  
- Website-style layout with animations  
- One-click DOCX report download  

---

## 🧠 NLP Techniques Used

- **TF-IDF Vectorization** – Feature extraction  
- **NMF (Non-negative Matrix Factorization)** – Topic modeling  
- **VADER Sentiment Analysis** – Polarity scoring  

---

## 🛠️ Tech Stack

- **Programming Language:** Python  
- **UI Framework:** Streamlit  

**NLP & ML**
- scikit-learn  
- nltk (VADER)  

**Visualization**
- Plotly  
- Matplotlib  
- WordCloud  

**Reporting**
- python-docx  

---

## 📁 Repository Structure

```
Dynamic-Text-Analysis-System/
│
├── app.py                  # Streamlit application
├── text analysis.ipynb     # Model training & experimentation
├── requirements.txt        # Python dependencies
├── .gitignore              # Ignored files
├── LICENSE                 # Project license
└── README.md               # Project documentation
```

---

## 🧪 Tested Datasets

- WineMag Dataset  
- Amazon Reviews Dataset  
- Generic CSV files with text columns  

The application is dataset-agnostic and works with most CSV files containing textual data.

---

## ▶️ How to Run the Project

### 1️⃣ Install Dependencies
```
pip install -r requirements.txt
```

### 2️⃣ Run the Application
```
streamlit run app.py
```

### 3️⃣ Open in Browser
```
http://localhost:8501
```

---

## 🎯 Use Cases

- HR feedback analysis  
- Customer sentiment monitoring  
- Academic NLP projects  
- Market research  
- Text analytics learning  

---

## 📜 License

This project is licensed under the **MIT License**.

