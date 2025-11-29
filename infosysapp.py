# Import necessary libraries
import streamlit as st
import base64
import nltk
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re
import pickle
from transformers import T5ForConditionalGeneration, T5Tokenizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import nltk
import spacy
from spacy import displacy
import torch
from rake_nltk import Rake
import yake
from summa import keywords
from summa import keywords as summa_keywords
from gensim.corpora import Dictionary
from gensim.models import LdaModel
from gensim.models.coherencemodel import CoherenceModel
from gensim.corpora import Dictionary, MmCorpus
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

@st.cache_resource
def load_model():
    lda = LdaModel.load("models/lda_model_v1.gensim")
    dictionary = Dictionary.load("models/dictionary_v1.gensim")
    return lda, dictionary
lda_model, dictionary = load_model()

def preprocess(text):
    # Basic cleanup
    text = re.sub(r"\s+", " ", text.strip())
    
    # Tokenize and remove stopwords
    tokens = simple_preprocess(text, deacc=True, min_len=2)
    tokens = [t for t in tokens if t not in STOPWORDS and not t.isnumeric()]
    
    # Lemmatize
    tokens = [lemmatizer.lemmatize(t) for t in tokens]
    return tokens


def analyze_text(text, lda, dictionary):
    tokens = preprocess(text)  # your tokenizer
    bow = dictionary.doc2bow(tokens)
    topic_dist = lda.get_document_topics(bow, minimum_probability=0.0)

    # Confidence via entropy
    import math
    probs = [p for _, p in topic_dist]
    entropy = -sum(p * math.log(p + 1e-12) for p in probs)
    max_entropy = math.log(len(probs))
    certainty = 1.0 - (entropy / max_entropy)

    top_topics = sorted(topic_dist, key=lambda x: x[1], reverse=True)[:5]
    labeled = [{
        "topic_id": tid,
        "prob": prob,
        "keywords": [w for w, _ in lda.show_topic(tid, topn=8)]
    } for tid, prob in top_topics]

    return {
        "certainty": round(certainty, 3),
        "topics": labeled,
        "distribution": [{"topic_id": tid, "prob": prob} for tid, prob in topic_dist]
    }


# Load pre-trained sentiment analysis model and vectorizer
vectorizer_new = pickle.load(open('vectorizer_movie.pkl', 'rb'))
clf_best = pickle.load(open('Movie_sentiment.pkl', 'rb'))

# Text preprocessing function for sentiment analysis
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = nltk.word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [t for t in tokens if t not in stop_words]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(t) for t in tokens]
    return " ".join(tokens)

# Sentiment analysis function for movies domain
def Sentiment_function_movie(text):
    cleaned_text = preprocess_text(text)
    vectorized_text = vectorizer_new.transform([cleaned_text])
    ans = clf_best.predict(vectorized_text)[0]
    if ans == 1:
        return "Positive"
    else:
        return "Negative"
    
def movie_confidence_score(text):
    cleaned_text = preprocess_text(text)
    vectorized_text = vectorizer_new.transform([cleaned_text])
    classes = clf_best.classes_
    probs = clf_best.predict_proba(vectorized_text)[0]
    return probs,classes

# Text cleaning function for summaries
def clean_text(text):
    # Normalize whitespace
    text = re.sub(r'\s{2,}', ' ', text.strip())

    # Capitalize sentence starts
    text = re.sub(r'([.!?])\s+([a-z])', lambda m: m.group(1) + ' ' + m.group(2).upper(), text)
    text = text[0].upper() + text[1:] if text else text

    # Remove repeated phrases like "X and X", "X. X", "X and X."
    def dedupe_phrases(t):
        pattern = re.compile(r'\b(\w+(?:[-\s]\w+){0,4})(?:\s+and)?\s+\1(?=[\s.,;!?])', flags=re.IGNORECASE)
        prev = None
        while prev != t:
            prev = t
            t = pattern.sub(r'\1', t)
        return t

    text = dedupe_phrases(text)

    return text

# Summary generation function
def dual_summary(text, max_input_length=700, max_output_length=200, min_length=70, length_penalty=1.2, num_beams=6, num_sentences=3):
    # Abstractive summary
    input_text = "summarize: " + text.strip().replace("\n", " ")
    inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=max_input_length, truncation=True)
    summary_ids = model.generate(
        inputs,
        max_length=max_output_length,
        min_length=min_length,
        length_penalty=length_penalty,
        num_beams=num_beams,
        no_repeat_ngram_size=3,  # Prevent fragment repetition
        early_stopping=True
    )
    abstractive = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    abstractive = clean_text(abstractive)


    # Extractive summary
    sentences = sent_tokenize(text)
    if len(sentences) <= num_sentences:
        extractive = " ".join(sentences)
    else:
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(sentences)
        scores = np.asarray(X.sum(axis=1)).ravel()
        top_indices = scores.argsort()[-num_sentences:][::-1]
        top_sentences = [sentences[i] for i in sorted(top_indices)]
        extractive = " ".join(top_sentences)

    return {"abstractive": abstractive, "extractive": extractive}

# Visualization functions
def plot_word_freq(text):
    tokens = nltk.word_tokenize(text.lower())
    words = [w for w in tokens if w.isalpha() and w not in nltk.corpus.stopwords.words('english')]
    freq = Counter(words).most_common(20)
    labels, counts = zip(*freq)
    fig, ax = plt.subplots()
    ax.barh(labels, counts)
    ax.invert_yaxis()
    st.pyplot(fig)

def plot_sentence_lengths(text):
    sentences = nltk.sent_tokenize(text)
    lengths = [len(s.split()) for s in sentences]
    fig, ax = plt.subplots()
    ax.hist(lengths, bins=10, color='skyblue')
    ax.set_title("Sentence Length Distribution")
    st.pyplot(fig)

nlp = spacy.load("en_core_web_sm")
def show_ner(text):
    doc = nlp(text)
    html = displacy.render(doc, style="ent", jupyter=False)
    st.components.v1.html(html, height=600, width=1000, scrolling=True)

def plot_pos_distribution(text):
    doc = nlp(text)
    pos_counts = Counter([token.pos_ for token in doc])
    labels, counts = zip(*pos_counts.items())
    fig, ax = plt.subplots()
    ax.barh(labels, counts, color='orchid')
    ax.set_title("Part-of-Speech Distribution")
    ax.set_xlabel("Frequency")
    ax.set_ylabel("POS Tags")
    st.pyplot(fig)

# Load fine-tuned T5 model and tokenizer
model = T5ForConditionalGeneration.from_pretrained(r"C:\Users\ABIR GHOSH\Desktop\ML_Projects\my_t5_model\my_t5_model", trust_remote_code=True)
tokenizer = T5Tokenizer.from_pretrained(r"C:\Users\ABIR GHOSH\Desktop\ML_Projects\my_t5_model\my_t5_model")
# device = torch.device("cpu")
# model.to(device)

# Set background image
def set_background(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    st.markdown(f"""
        <style>
        html, body {{
            height: 100%;
            margin: 0;
            padding: 0;
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
        }}
        .stApp {{
            background: transparent;
            padding-top: 0rem;
        }}
        header, footer, [data-testid="stHeader"], [data-testid="stToolbar"] {{
            background: transparent;
        }}
        [data-testid="stSidebar"] > div:first-child {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
        }}
        </style>
    """, unsafe_allow_html=True)

# Keyword display box
def display_keywords_box(title, keywords):
    st.markdown(f"### {title}")
    box_style = """
    <div style='
        background-color: #f0f8ff;
        color: #000000;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #d3d3d3;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        font-size: 16px;
        line-height: 1.6;
    '>
    """
    keyword_list = "<br>".join([f"• {kw}" for kw in keywords])
    st.markdown(box_style + keyword_list + "</div>", unsafe_allow_html=True)

# Title of the app
st.set_page_config(page_title="AI Text Analysis", layout="wide")
st.markdown("""
    <h1 style='text-align: center; margin-top: -60px ; color: White;'>Dynamic AI Text Analysis Platform</h1>
""", unsafe_allow_html=True)
st.markdown("""
    <p style='text-align: center; color: White;'>Unlock the power of intelligent language insights with a visually unified, enterprise-grade interface. 
    This platform blends cutting-edge machine learning with modular UI design to deliver fast, reproducible text analysis — 
    from sentiment diagnostics to advanced linguistic modeling.</p>
""", unsafe_allow_html=True)
set_background("bac.png")

# Sidebar for navigation
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.5);
        border-right: 2px solid blue;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    /* Restore full interactivity to the sidebar toggle */
    [data-testid="collapsedControl"] {
        background: transparent !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        z-index: 1000 !important;
        display: block !important;
    }

    /* Style the arrow itself */
    [data-testid="collapsedControl"] svg {
        fill: white !important;
        stroke: white !important;
        opacity: 1 !important;
        filter: none !important;
        box-shadow: none !important;
        pointer-events: auto !important;
    }
    </style>
""", unsafe_allow_html=True)


st.sidebar.markdown("""
    <h1 style='margin-top: -40px; color: solid White;'>Text Input and Settings</h1>
""", unsafe_allow_html=True)
st.markdown("""
    <style>
    [data-testid="stSidebar"] textarea {
        background-color: white !important;
        color: black !important;
        border: 2px solid #ccc;
        padding: 10px;
        font-size: 20px;
        caret-color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar text area
text_input = st.sidebar.text_area("Enter text for analysis", height=200)
st.markdown("""
    <style>
    /* Outer file uploader container */
    [data-testid="stFileUploader"] {
        background-color: transparent !important;
        padding: 0;
        border: none;
    }

    /* Drag-and-drop zone wrapper */
    [data-testid="stFileDropzone"] div:first-child {
        background-color: white !important;
        border: 2px dashed #999 !important;
        border-radius: 8px;
        padding: 20px;
    }

    /* Optional: style the cloud icon */
    [data-testid="stFileDropzone"] svg {
        fill: #333 !important;
    }

    /* Optional: style the drag text */
    [data-testid="stFileDropzone"] p {
        color: black !important;
        font-weight: bold;
    }

    /* Style the Browse Files button */
    [data-testid="stFileUploader"] button {
        background-color: white !important;
        color: black !important;
        border: 1px solid #999 !important;
        font-weight: bold;
    }
    
    * Reduce font size and cursor size inside sidebar text area */
    section[data-testid="stSidebar"] textarea {
        font-size: 13px !important;      /* Smaller font */
        line-height: 1.4 !important;     /* Tighter spacing */
        caret-color: #333 !important;    /* Cursor color */
        height: 200px !important;        /* Ensure consistent height */
    }

    /* Optional: reduce padding and border radius */
    section[data-testid="stSidebar"] textarea {
        padding: 6px !important;
        border-radius: 6px !important;
    }

    </style>
""", unsafe_allow_html=True)

# Sidebar file uploader
file_upload = uploaded_file = st.sidebar.file_uploader("Or upload a file", type=["txt"])

# Initialize session state
if "analysis_type" not in st.session_state:
    st.session_state.analysis_type = None

# Sidebar button styles
st.sidebar.markdown("""
<style>
/* Style only analysis buttons inside the sidebar */
section[data-testid="stSidebar"] div.stButton > button {
    background-color: #1E90FF !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 8px !important;
    height: 45px !important;
    width: 100% !important;
    max-width: 100% !important;      /* Override Streamlit's default */
    display: block !important;
    margin: 0 auto !important;       /* Center if needed */
    box-sizing: border-box !important;
}

/* Reset file uploader button to default */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
    background-color: white !important;
    color: black !important;
    border: 1px solid #999 !important;
    font-weight: bold !important;
    border-radius: 6px !important;
    padding: 0.5em 1em !important;
}
</style>
""", unsafe_allow_html=True)

# Sidebar buttons
with st.sidebar:
    st.markdown("### 🔍 Choose Analysis Type")

    if st.button("Sentiment Analysis"):
        st.session_state.analysis_type = "sentiment"

    if st.button("Topic Modeling"):
        st.session_state.analysis_type = "topic"

    if st.button("Keyword Extraction"):
        st.session_state.analysis_type = "keywords"

    if st.button("Summary Generation"):
        st.session_state.analysis_type = "summary"

    if st.button("Visualization"):
        st.session_state.analysis_type = "visual"

    if st.button("Word Cloud"):
        st.session_state.analysis_type = "wordcloud"

# Main area content
if st.session_state.analysis_type == "sentiment":
    st.markdown("## 🧠 Analysis Output")
    st.subheader("Sentiment Analysis Results")
    input_text = ""
    if uploaded_file is not None:
        try:
            input_text = uploaded_file.read().decode("utf-8").strip()
        except Exception as e:
            st.error(f"Could not read uploaded file: {e}")
            input_text = ""

    elif text_input:
        input_text = text_input.strip()

    if input_text:
        domain = ["-- Select a domain --","🎬 Movies","🛍️ Products","🐦 Social Media","📈 Finance","📰 News","🏥 Healthcare","📞 Customer Support"]
        choose_domain = st.selectbox("Select Domain for Sentiment Analysis", domain,index=0)
        if choose_domain == "-- Select a domain --":
            pass
        elif choose_domain == "🎬 Movies":
            st.info("This model is trained on IMDB Movies Reviews dataset to classify reviews as Positive or Negative.")
            sentiment_result = Sentiment_function_movie(input_text)
            st.markdown(f"### Sentiment Result : {sentiment_result}")
            # Future implementations for other domains can be added here.     
        else:
            st.warning("Sentiment analysis model is currently only available for the Movies domain.")
    else:
        st.warning("Please provide text input or upload a file to generate sentiment analysis.")

elif st.session_state.analysis_type == "topic":
    st.markdown("## 🧠 Analysis Output")
    st.subheader("Topic Modeling Results")
    input_text = ""
    if uploaded_file is not None:
        try:
            input_text = uploaded_file.read().decode("utf-8").strip()
        except Exception as e:
            st.error(f"Could not read uploaded file: {e}")
            input_text = ""
    
    elif text_input:
        input_text = text_input.strip()
    
    if input_text.strip():
        result = analyze_text(input_text, lda_model, dictionary)
        st.markdown("**Top Topics:**")
        for t in result["topics"]:
            st.write(f"Topics : " + ", ".join(t["keywords"]))
    else:
        st.warning("Please provide text input or upload a file to generate topic modeling.")

elif st.session_state.analysis_type == "keywords":
    st.markdown("## 🧠 Analysis Output")
    st.subheader("Keyword Extraction Results")
    input_text = ""

    if uploaded_file is not None:
        try:
            input_text = uploaded_file.read().decode("utf-8").strip()
        except Exception as e:
            st.error(f"Could not read uploaded file: {e}")
            input_text = ""

    elif text_input:
        input_text = text_input.strip()

    if input_text:
        st.info("""This tool supports three keyword extraction models : 
                
        - 🪓 RAKE (Rapid Automatic Keyword Extraction) : An unsupervised, domain-independent algorithm that identifies key phrases by analyzing word frequency and co-occurrence patterns.
        - ⚡ YAKE (Yet Another Keyword Extractor) : A lightweight, unsupervised method that extracts keywords based on statistical features such as casing, word position, frequency, and relatedness to context.
        - 🧠 TextRank : A graph-based algorithm inspired by PageRank, which ranks words and phrases based on their relationships within the text to identify the most significant keywords.

        """)
        model_rake = st.checkbox("🪓 RAKE")
        model_yake = st.checkbox("⚡ YAKE")
        model_text_rank = st.checkbox("🧠 TextRank")

        if model_rake:
            rake = Rake()
            rake.extract_keywords_from_text(input_text)
            raw_phrases = rake.get_ranked_phrases()[1:11]
            cleaned_phrases = [phrase.strip().strip('.,:;"\'') for phrase in raw_phrases]
            display_keywords_box("🪓 RAKE Keywords", cleaned_phrases)

        if model_yake:
            kw_extractor = yake.KeywordExtractor(top=10, stopwords=None)
            keywords_yake = [kw for kw, _ in kw_extractor.extract_keywords(input_text)]
            display_keywords_box("⚡ YAKE Keywords", keywords_yake)

        if model_text_rank:
            tr_keywords = summa_keywords.keywords(input_text).split('\n')[:10]
            display_keywords_box("🧠 TextRank Keywords", tr_keywords)

    else:
        st.warning("Please provide text input or upload a file to generate keywords.")
    
elif st.session_state.analysis_type == "summary":
    st.markdown("## 🧠 Analysis Output")
    st.subheader("Summary Generation")
    st.info("""This tool uses a **hybrid summarization approach** combining both **abstractive** and **extractive** techniques:

    - ✂️ Extractive Summary: Generated using TF-IDF scoring, which selects the most informative sentences from the original text based on term relevance.
    - 🧠 Abstractive Summary: Powered by a fine-tuned T5-small transformer model, trained to rephrase and condense content into a more natural, human-like summary.

    Whether you're analyzing documents, articles, or reports — this dual strategy ensures both factual coverage and semantic clarity.
    """)
    # Step 1: Collect input from file or text box
    input_text = ""

    if uploaded_file is not None:
        try:
            input_text = uploaded_file.read().decode("utf-8").strip()
        except Exception as e:
            st.error(f"Could not read uploaded file: {e}")
            input_text = ""

    elif text_input:
        input_text = text_input.strip()

    # Step 2: Validate input and generate summary
    if input_text:
        summary_result = dual_summary(input_text)

        st.markdown("## 🧠 Summary Output")

        with st.expander("✂️ Extractive Summary", expanded=True):
            st.write(summary_result["extractive"])

        with st.expander("🧠 Abstractive Summary", expanded=True):
            st.write(summary_result["abstractive"])
    else:
        st.warning("Please provide text input or upload a file to generate a summary.")

    st.markdown("""
    <style>
        /* Force white font for SpaCy NER rendering */
        span.ent {
            color: white !important;
        }

        /* Optional: make entity labels bold and readable */
        span.ent span.label {
            font-weight: bold !important;
            background: #1E90FF !important;
            color: white !important;
            padding: 2px 4px;
            border-radius: 4px;
        }
    </style>
    """, unsafe_allow_html=True)

elif st.session_state.analysis_type == "visual":
    st.markdown("## 🧠 Analysis Output")
    st.subheader("📊 Text Visualizations")
    input_text = ""

    if uploaded_file is not None:
        try:
            input_text = uploaded_file.read().decode("utf-8").strip()
        except Exception as e:
            st.error(f"Could not read uploaded file: {e}")
    elif text_input:
        input_text = text_input.strip()

    if not input_text:
        st.warning("Please provide input via text box or file upload.")
    
    if input_text:

        show_word_freq = st.checkbox("🔠 Word Frequency")
        show_sentence_length = st.checkbox("📏 Sentence Length Distribution")
        show_ner_check = st.checkbox("🧠 Named Entity Recognition")
        show_pos = st.checkbox("🔤 Part-of-Speech Distribution")

        if show_word_freq:
            st.subheader("🔠 Word Frequency")
            st.info("Displays the 20 most common words in the text, excluding stopwords.")
            plot_word_freq(input_text)

        if show_sentence_length:
            st.subheader("📏 Sentence Length Distribution")
            st.info("Tokenize sentences and plot their lengths. Reveals verbosity or conciseness")
            plot_sentence_lengths(input_text)

        if show_ner_check:
            st.subheader("🧠 Named Entity Recognition")
            st.info("Highlights entities like persons, organizations, locations in the text.")
            show_ner(input_text)

        if show_pos:
            st.subheader("🔤 Part-of-Speech Distribution")
            st.info("Shows the frequency of different parts of speech in the text.")
            plot_pos_distribution(input_text)

elif st.session_state.analysis_type == "wordcloud":
    st.markdown("## 🧠 Analysis Output")
    st.subheader("Word Cloud")
    st.info("This WordCloud highlights the most frequent words in the input text.\nLarger words appear more often and may indicate key themes or topics.")
    input_text = ""

    if uploaded_file is not None:
        try:
            input_text = uploaded_file.read().decode("utf-8").strip()
        except Exception as e:
            st.error(f"Could not read uploaded file: {e}")
            input_text = ""

    elif text_input:
        input_text = text_input.strip()
    
    if input_text:
        # Generate word cloud
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            colormap='viridis',
            max_words=200
        ).generate(input_text)

        # Display using matplotlib
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)
    
    else:
        st.warning("Please provide text input or upload a file to generate a word cloud.")

elif st.session_state.analysis_type is None:
    st.warning("Please select an analysis type from the sidebar after entering text or uploading a file.")