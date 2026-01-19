import streamlit as st
import PyPDF2
import joblib
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF

from sentimentanalysis import predict_sentiment
from summarization import summarize_text


# ================= SESSION STATE =================
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False

if "cancel" not in st.session_state:
    st.session_state.cancel = False

if "running" not in st.session_state:
    st.session_state.running = False

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="AI Text Analysis Dashboard",
    page_icon="🧠",
    layout="wide"
)
def loading_card(text="Processing..."):
    return st.markdown(
        f"""
        <div style="
            background:#020617;
            border:1px solid #1e293b;
            border-radius:12px;
            padding:16px;
            margin:10px 0;
            animation:pulse 1.5s infinite;
        ">
            ⏳ {text}
        </div>
        <style>
        @keyframes pulse {{
            0% {{ opacity: 0.4; }}
            50% {{ opacity: 1; }}
            100% {{ opacity: 0.4; }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ================= CUSTOM CSS =================
st.markdown("""
<style>
/* ================= APP BACKGROUND ================= */
.stApp {
    background: linear-gradient(135deg, #020617, #0f172a);
    color: #e5e7eb;
}

/* ================= HEADINGS & TEXT ================= */
h1, h2, h3, p, span {
    color: #e5e7eb !important;
}

/* ================= TEXT AREA ================= */
textarea {
    background-color: #020617 !important;
    color: #ffffff !important;
    font-size: 18px !important;
    border-radius: 14px !important;
    border: 1px solid #1e293b !important;
}

/* ================= BUTTON ================= */
.stButton > button {
    background-color: #2563eb !important;
    color: white !important;
    font-size: 20px !important;
    border-radius: 12px !important;
    padding: 12px !important;
}

/* ================= KEYWORD CHIPS ================= */
.chip {
    display: inline-block;
    background-color: #1e293b;
    color: #ffffff;
    padding: 8px 14px;
    margin: 6px;
    border-radius: 999px;
    font-size: 16px;
}

/* ================= METRIC LABELS ================= */
div[data-testid="stMetricLabel"],
div[data-testid="stMetricLabel"] span {
    font-size: 26px !important;
    font-weight: 600 !important;
    color: #e5e7eb !important;
    opacity: 1 !important;
}

/* ================= METRIC VALUES ================= */
div[data-testid="stMetricValue"],
div[data-testid="stMetricValue"] span {
    font-size: 42px !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    opacity: 1 !important;
}

/* ================= CAPTIONS ================= */
small {
    color: #cbd5f5 !important;
    font-size: 20px !important;
    font-weight: 500 !important;
    line-height: 1.6 !important;
    opacity: 1 !important;
}

/* ================= FILE UPLOADER (DARK FIX – SURE SHOT) ================= */

/* ================= FILE UPLOADER (DARK FIX) ================= */

/* The main container box */
[data-testid="stFileUploader"] {
    background-color: #020617 !important;
    border: 2px dashed #1e293b !important; /* Makes it look more like an upload zone */
    border-radius: 14px !important;
    padding: 20px !important;
}

/* Fixes the "Drag and drop file here" and "Limit 200MB" text */
[data-testid="stFileUploader"] section {
    background-color: #020617 !important;
    color: #ffffff !important;
}

/* Targets all labels and helper text inside the uploader */
[data-testid="stFileUploader"] label, 
[data-testid="stFileUploader"] p, 
[data-testid="stFileUploader"] small {
    color: #ffffff !important;
}

/* The 'Browse files' button styling */
[data-testid="stFileUploader"] button {
    background-color: #1e293b !important;
    color: #ffffff !important;
    border: 1px solid #334155 !important;
}

/* Specific fix for the 'Drag and drop' text which is often stubborn */
[data-testid="stWebSidebar"] [data-testid="stFileUploader"] div div {
    color: white !important;
}

/* Hover effect */
[data-testid="stFileUploader"] button:hover {
    background-color: #334155 !important;
    color: #ffffff !important;
}
/* ================= DOWNLOAD BUTTON FIX ================= */
[data-testid="stDownloadButton"] > button {
    background-color: #1e293b !important; /* Dark Slate background */
    color: #ffffff !important;           /* White text */
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    width: 100% !important;              /* Makes it match the Analyze button width */
    transition: background-color 0.3s ease;
}

/* Hover effect for download button */
[data-testid="stDownloadButton"] > button:hover {
    background-color: #334155 !important;
    border-color: #60a5fa !important;    /* Light blue border on hover */
    color: #ffffff !important;
}

</style>
""", unsafe_allow_html=True)



# ================= TITLE =================
st.markdown("<h1 style='text-align:center;'>🧠INSIGHTIQ. </h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center;'>Get Insights Instantly</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Analyze text for sentiment, keywords, themes, and summaries.</p>", unsafe_allow_html=True)


# ================= PDF EXTRACTION =================
def extract_pdf_text(pdf):
    reader = PyPDF2.PdfReader(pdf)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + " "
    return text


# ================= KEYWORD EXTRACTION =================
@st.cache_resource
def load_vectorizer():
    return joblib.load("tfidf_vectorizer.joblib")

vectorizer = load_vectorizer()

def extract_document_keywords(text, top_k=8):
    tfidf = vectorizer.transform([text])
    scores = tfidf.toarray()[0]
    feature_names = vectorizer.get_feature_names_out()
    top_indices = scores.argsort()[-top_k:][::-1]
    return [feature_names[i] for i in top_indices if scores[i] > 0]


# ================= PARAGRAPH-LEVEL TOPIC MODELING =================
def paragraph_level_theme(text, top_words=6):
    paragraphs = [
        p.strip() for p in text.split("\n")
        if len(p.split()) > 40
    ]

    if len(paragraphs) < 2:
        paragraphs = [text]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(paragraphs)

    nmf = NMF(n_components=1, random_state=42)
    nmf.fit(tfidf)

    topic = nmf.components_[0]
    feature_names = vectorizer.get_feature_names_out()

    top_indices = topic.argsort()[-top_words:][::-1]
    words = [feature_names[i] for i in top_indices]

    return words



# ================= VISUALS =================
def plot_topic_bar(words):
    y = list(range(len(words)))[::-1]
    values = np.arange(len(words), 0, -1)

    fig, ax = plt.subplots(figsize=(4, 2))

    ax.barh(y, values, color="#60a5fa")
    ax.set_yticks(y)
    ax.set_yticklabels(words)
    ax.set_xlabel("Relative Importance")
    ax.set_title("Key Theme Words")
    plt.tight_layout()
    return fig


def plot_keyword_wordcloud(words):
    wc = WordCloud(
        width=700,
        height=350,
        background_color="black",
        colormap="cool"
    ).generate(" ".join(words))
    return wc


# ================= SUMMARY FIX =================
def capitalize_sentences(text):
    text = re.sub(r"\s+([.,!?])", r"\1", text)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return " ".join(s.capitalize() for s in sentences if s.strip())


# ================= INPUT =================
st.markdown("## 📥 Enter Text")

col1, col2 = st.columns([2, 1])

with col1:
    text_input = st.text_area(
        "✍️ Type or paste text",
        height=260,
        placeholder="Enter reviews, articles, reports, etc."
    )

with col2:
    uploaded_file = st.file_uploader("📄 Upload PDF", type=["pdf"])

analyze_disabled = st.session_state.running

button_label = "🔄 Analyzing..." if st.session_state.running else "🔍 Analyze Text"
if st.button(
    button_label,
    use_container_width=True,
    disabled=analyze_disabled
):
    st.session_state.cancel = False
    st.session_state.running = True

    if text_input.strip():
        st.session_state.final_text = text_input
        st.session_state.analyzed = True
    elif uploaded_file:
        st.session_state.final_text = extract_pdf_text(uploaded_file)
        st.session_state.analyzed = True
    else:
        st.warning("Please enter text or upload a PDF.")
        st.session_state.running = False
# ================= SENTIMENT PLOTTING =================

def plot_length_comparison(original_len, summary_len):
    labels = ["Input Text", "Summary"]
    values = [original_len, summary_len]

    fig, ax = plt.subplots(figsize=(4, 2.5))
    ax.bar(labels, values, color=["#60a5fa", "#34d399"])
    ax.set_ylabel("Number of Words")
    ax.set_title("Text Length Comparison")

    for i, v in enumerate(values):
        ax.text(i, v + 2, str(v), ha="center", fontweight="bold")

    plt.tight_layout()
    return fig
def plot_sentiment_pie(sentiment, confidence):
    labels = ["Positive", "Negative"]
    values = (
        [confidence, 100 - confidence]
        if sentiment == "Positive"
        else [100 - confidence, confidence]
    )

    fig, ax = plt.subplots(figsize=(3, 3), dpi=150)
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    ax.pie(
        values,
        autopct="%1.1f%%",
        startangle=90,
        colors=["#22c55e", "#ef4444"],
        textprops={"color": "white", "fontsize": 10},
         wedgeprops={"linewidth": 0}
    )

    ax.axis("equal")
    return fig
# ================= INSIGHT GENERATION =================
def generate_insight(sentiment, confidence, keywords, theme_words):
    if sentiment == "Positive":
        opening = "The text presents a favorable overall impression."
    else:
        opening = "The text highlights dissatisfaction or concerns."

    reliability = (
        "This assessment is highly reliable."
        if confidence >= 70
        else "This assessment should be interpreted cautiously."
    )

    keyword_part = (
        f"Key signals such as {', '.join(keywords[:3])} strongly influenced this outcome."
        if keywords else
        "Specific wording in the text influenced this outcome."
    )

    theme_part = (
        f"The discussion mainly revolves around {', '.join(theme_words[:2])}."
        if theme_words else
        "A dominant topic emerges across the text."
    )

    action = (
        "This insight can help evaluate opinions, feedback quality, or audience perception."
    )

    return f" What this means: {opening} {reliability} {keyword_part} {theme_part} {action}"

def clean_text_for_pdf(text):
    if text is None:
        return ""

    replacements = {
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "–": "-",
        "—": "-",
        "…": "...",
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    # Final safety: remove any remaining unsupported chars
    return text.encode("latin-1", errors="ignore").decode("latin-1")

# ================= IMPORT FPDF =================
from fpdf import FPDF
# ================= PDF REPORT GENERATION =================
def generate_pdf_report(text, sentiment, confidence, keywords, theme_words, summary, insight):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "AI Text Analysis Report", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "", 12)

    pdf.multi_cell(0, 8, f"Overall Verdict: {sentiment}")
    pdf.multi_cell(0, 8, f"Confidence Level: {confidence:.2f}%")

    pdf.ln(3)
    pdf.multi_cell(0, 8, "Keywords:")
    pdf.multi_cell(0, 8, clean_text_for_pdf(", ".join(keywords)))

    pdf.ln(3)
    pdf.multi_cell(0, 8, "Core Topics:")
    pdf.multi_cell(0, 8, clean_text_for_pdf(", ".join(theme_words)))

    pdf.ln(3)
    pdf.multi_cell(0, 8, "Summary:")
    pdf.multi_cell(0, 8, clean_text_for_pdf(summary))

    pdf.ln(3)
    pdf.multi_cell(0, 8, "Insight:")
    pdf.multi_cell(0, 8, clean_text_for_pdf(insight))

    return pdf.output(dest="S").encode("latin-1")


# ================= DASHBOARD =================
if st.session_state.analyzed and st.session_state.running:
    # ---------- Cancel Button ----------
    cancel_col1, cancel_col2 = st.columns([4, 1])

    with cancel_col2:
        if st.button("❌ Cancel Analysis"):
            st.session_state.cancel = True


    final_text = st.session_state.final_text



    # ---------- Animated Loader ----------
    loader = loading_card("Initializing analysis...")

    # ---------- Progress ----------
    progress = st.progress(0)
    status = st.empty()

    # ---------- STEP 1 ----------
    if st.session_state.cancel:
        loader.empty()
        status.warning("❌ Analysis cancelled")
        progress.progress(0)
        st.session_state.running = False
        st.session_state.cancel = False
        st.stop()

    status.info("🔍 Analyzing sentiment...")
    sentiment, confidence = predict_sentiment(final_text)
    progress.progress(25)

    # ---------- STEP 2 ----------
    if st.session_state.cancel:
        loader.empty()
        status.warning("❌ Analysis cancelled")
        progress.progress(0)
        st.session_state.running = False
        st.session_state.cancel = False
        st.stop()

    status.info("🔑 Extracting keywords...")
    keywords = extract_document_keywords(final_text)
    progress.progress(45)

    # ---------- STEP 3 ----------
    if st.session_state.cancel:
        loader.empty()
        status.warning("❌ Analysis cancelled")
        progress.progress(0)
        st.session_state.running = False
        st.session_state.cancel = False
        st.stop()

    status.info("✂️ Generating summary...")
    summary = summarize_text(final_text)
    progress.progress(70)

        # ---------- STEP 4 ----------
    if st.session_state.cancel:
        loader.empty()
        status.warning("❌ Analysis cancelled")
        progress.progress(0)
        st.session_state.running = False
        st.session_state.cancel = False
        st.stop()

    status.info("📌 Identifying core topics...")
    theme_words = paragraph_level_theme(final_text)
    progress.progress(90)

        # ---------- DONE ----------
    loader.empty()
    status.success("✅ Analysis complete")
    progress.progress(100)
    st.session_state.sentiment = sentiment
    st.session_state.confidence = confidence
    st.session_state.keywords = keywords
    st.session_state.summary = summary
    st.session_state.theme_words = theme_words
    st.session_state.running = False
# ================= DISPLAY RESULTS =================
if st.session_state.analyzed and not st.session_state.running:
    if len(final_text.split()) < 40:
        st.warning("Text is too short for reliable theme analysis. Results may be limited.")
    sentiment = st.session_state.sentiment
    confidence = st.session_state.confidence
    keywords = st.session_state.keywords
    summary = st.session_state.summary
    theme_words = st.session_state.theme_words
    # ================= SENTIMENT =================
    st.markdown("## 😊 Overall Verdict")
    st.caption("A quick understanding of how the text feels overall.")


    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown("### Overall Sentiment")
        st.metric("Sentiment", sentiment,label_visibility="collapsed")
        st.markdown("### Confidence Level")
        st.metric("Confidence", f"{confidence:.2f}%", label_visibility="collapsed")

        fig_pie=plot_sentiment_pie(sentiment, confidence)
        st.pyplot(fig_pie,width=350)
        st.caption("This sentiment reflects the overall emotional tone of the text.")



    # ================= KEYWORDS =================
    with col2:
        st.markdown("## 🔑 Keywords detected")
        st.caption("These words strongly influence the verdict and theme.")


        wc = plot_keyword_wordcloud(keywords)
        st.image(wc.to_array(), width=450)


    # ================= THEMES =================
    st.markdown("## 📌 Core Topics Identified")
    st.caption("The primary idea the text consistently focuses on.")


    st.pyplot(plot_topic_bar(theme_words), use_container_width=False)
    # ================= SUMMARY =================
    st.markdown("## ✂️ Short Summary(TL;DR)")

    if summary is None:
        st.info("The input text is already concise. A summary is not required.")
    else:
        summary = capitalize_sentences(summary)
        st.success(summary)

        with st.expander("### 📊 Text Length Comparison"):

            fig_len = plot_length_comparison(
                len(final_text.split()),
                len(summary.split())
            )
            col1,col2,col3=st.columns([1,2,1])
            with col2:
                st.pyplot(fig_len,use_container_width=False)
            # ================= INSIGHT GENERATION =================
    insight_text = generate_insight(
    sentiment,
    confidence,
    keywords,
    theme_words
    )
    st.markdown("## 🧠 What this means for you")
    st.info(insight_text)
    # ================= PDF REPORT DOWNLOAD =================
    pdf_bytes = generate_pdf_report(
    final_text,
    sentiment,
    confidence,
    keywords,
    theme_words,
    summary,
    insight_text
)

    st.download_button(
        label="📄 Download Report as PDF",
        data=pdf_bytes,
        file_name="text_analysis_report.pdf",
        mime="application/pdf"
    )