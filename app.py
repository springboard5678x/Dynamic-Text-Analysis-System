# app.py — Narrative Nexus (full working version, widget-key rotation so Clear empties inputs)
# Requirements (minimal): streamlit, scikit-learn, numpy, matplotlib, wordcloud
# Optional: gensim (LDA), nltk (sentence tokenizer)
import os
import re
import pickle
from collections import Counter

import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS

# Optional: gensim & nltk support
try:
    from gensim.models import LdaModel
    from gensim.corpora import Dictionary
    from gensim.utils import simple_preprocess
    GENSIM_AVAILABLE = True
except Exception:
    GENSIM_AVAILABLE = False

try:
    import nltk
    from nltk.tokenize import sent_tokenize
    nltk.download("punkt", quiet=True)
    NLTK_AVAILABLE = True
except Exception:
    NLTK_AVAILABLE = False

# -------------------------
# Session-state safe defaults (do NOT assign widget-owned keys after widget creation)
# -------------------------
if "analysis_ready" not in st.session_state:
    st.session_state["analysis_ready"] = False
if "input_version" not in st.session_state:
    st.session_state["input_version"] = 0
if "uploader_version" not in st.session_state:
    st.session_state["uploader_version"] = 0
if "cleared_at" not in st.session_state:
    st.session_state["cleared_at"] = 0

STOPWORDS = set(ENGLISH_STOP_WORDS)

# -------------------------
# Load artifacts (cached)
# -------------------------
@st.cache_resource
def load_artifacts(models_dir="models"):
    vec, clf, le = None, None, None
    errs = []
    try:
        p = os.path.join(models_dir, "vectorizer.pkl")
        if os.path.exists(p):
            vec = pickle.load(open(p, "rb"))
    except Exception as e:
        errs.append(f"vectorizer: {e}")
    try:
        p = os.path.join(models_dir, "model.pkl")
        if os.path.exists(p):
            clf = pickle.load(open(p, "rb"))
    except Exception as e:
        errs.append(f"model: {e}")
    try:
        p = os.path.join(models_dir, "label_encoder.pkl")
        if os.path.exists(p):
            le = pickle.load(open(p, "rb"))
    except Exception as e:
        errs.append(f"label_encoder: {e}")
    return vec, clf, le, errs

@st.cache_resource
def load_lda(models_dir="models"):
    if not GENSIM_AVAILABLE:
        return None, None
    candidates = ["lda_model_v1.gensim", "lda_model_15k.gensim", "lda_model.gensim"]
    for name in candidates:
        path = os.path.join(models_dir, name)
        if os.path.exists(path):
            try:
                lda = LdaModel.load(path)
                dpath = os.path.join(models_dir, "dictionary_v1.gensim")
                if not os.path.exists(dpath):
                    dpath = os.path.join(models_dir, "dictionary.gensim")
                dictionary = Dictionary.load(dpath) if os.path.exists(dpath) else None
                if getattr(lda, "id2word", None) is None and dictionary is not None:
                    lda.id2word = dictionary
                return lda, dictionary
            except Exception:
                continue
    return None, None

vectorizer, classifier, label_encoder, load_errors = load_artifacts()
lda_model, lda_dictionary = load_lda()

# -------------------------
# Helpers
# -------------------------
def read_current_inputs():
    """
    Read the current text area or uploaded file using versioned widget keys.
    We also snapshot the last text so re-creating the widget can show previous content if needed.
    """
    input_key = f"input_text_v{st.session_state.get('input_version', 0)}"
    uploader_key = f"uploaded_file_v{st.session_state.get('uploader_version', 0)}"

    # Text area value (if present)
    text_from_area = ""
    if input_key in st.session_state:
        text_from_area = st.session_state.get(input_key) or ""

    # Uploaded file (if present)
    uploaded = st.session_state.get(uploader_key) if uploader_key in st.session_state else None
    if uploaded:
        try:
            raw = uploaded.read()
            try:
                text = raw.decode("utf-8")
            except Exception:
                text = raw.decode("latin-1", errors="ignore")
            st.session_state["last_input_snapshot"] = text
            return text
        except Exception:
            pass

    # fallback to text area
    st.session_state["last_input_snapshot"] = text_from_area
    return text_from_area

def extractive_summary(text, n=3):
    if not text:
        return ""
    if NLTK_AVAILABLE:
        sents = sent_tokenize(text)
    else:
        sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    if len(sents) <= n:
        return " ".join(sents)
    vect = TfidfVectorizer(stop_words="english")
    X = vect.fit_transform(sents)
    scores = np.asarray(X.sum(axis=1)).ravel()
    top_idx = scores.argsort()[-n:][::-1]
    top_sorted = sorted(top_idx)
    return " ".join([sents[i] for i in top_sorted])

def wordcloud_fig(text):
    if not text or not text.strip():
        return None
    wc = WordCloud(width=800, height=400, background_color="white", max_words=150, stopwords=STOPWORDS).generate(text)
    fig, ax = plt.subplots(figsize=(6,3.5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    fig.tight_layout()
    return fig

def top_words(text, topn=12):
    tokens = re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())
    tokens = [t for t in tokens if t not in STOPWORDS]
    return Counter(tokens).most_common(topn)

def doc_topic_distribution(text):
    if lda_model is None or lda_dictionary is None:
        return None
    tokens = simple_preprocess(text, deacc=True, min_len=2)
    bow = lda_dictionary.doc2bow(tokens)
    td = lda_model.get_document_topics(bow, minimum_probability=0.0)
    out = []
    for tid, prob in sorted(td, key=lambda x: x[0]):
        try:
            kws = [w for w,_ in lda_model.show_topic(tid, topn=6)]
        except Exception:
            kws = []
        out.append((tid, prob, kws))
    return out

def plot_topic_bar(topic_list):
    if not topic_list:
        return None
    labels = [f"T{t[0]}" for t in topic_list]
    probs = [t[1] for t in topic_list]
    fig, ax = plt.subplots(figsize=(6,3))
    ax.bar(labels, probs, color='tab:blue')
    ax.set_ylim(0,1)
    ax.set_title("Topic distribution")
    fig.tight_layout()
    return fig

def small_sent_pie(probs_map):
    labels = list(probs_map.keys())
    sizes = [probs_map.get(l,0) for l in labels]
    fig, ax = plt.subplots(figsize=(2.6,2.6))
    ax.pie(sizes, labels=labels, autopct=lambda p: f"{p:.0f}%" if p>0 else "", startangle=140, wedgeprops={'linewidth':0.5,'edgecolor':'white'})
    ax.axis("equal")
    fig.tight_layout()
    return fig

def explain_prediction(text):
    if vectorizer is None or classifier is None or label_encoder is None:
        return None, None, None, None, "Missing artifacts (vectorizer/model/label_encoder). Place them in ./models/"
    try:
        X = vectorizer.transform([text])
    except Exception as e:
        return None, None, None, None, f"Vectorizer transform error: {e}"
    try:
        probs = classifier.predict_proba(X)[0] if hasattr(classifier, "predict_proba") else None
        pred_idx = int(np.argmax(probs)) if probs is not None else int(classifier.predict(X)[0])
        try:
            class_names = [label_encoder.inverse_transform([c])[0] for c in classifier.classes_]
        except Exception:
            class_names = list(getattr(label_encoder, "classes_", ["Negative","Neutral","Positive"]))
        raw_label = class_names[pred_idx]
        maxp = float(np.max(probs)) if probs is not None else 1.0
        final_label = raw_label
        if probs is not None:
            if maxp < 0.55:
                final_label = "Neutral"
            try:
                neutral_idx = class_names.index("Neutral") if "Neutral" in class_names else 1
                neutral_prob = float(probs[neutral_idx])
                if raw_label in ("Positive","Negative") and (maxp < 0.75 and neutral_prob > 0.40):
                    final_label = "Neutral"
            except Exception:
                pass
        pos, neg = [], []
        try:
            try:
                feat_names = vectorizer.get_feature_names_out()
            except Exception:
                feat_names = [k for k,_ in sorted(vectorizer.vocabulary_.items(), key=lambda x: x[1])]
            coef = classifier.coef_
            row = pred_idx if pred_idx < coef.shape[0] else 0
            arr = X.toarray()[0]
            contribs = []
            for i, v in enumerate(arr):
                if v != 0:
                    score = float(v) * float(coef[row, i])
                    contribs.append((feat_names[i], v, score))
            pos = sorted(contribs, key=lambda x: x[2], reverse=True)[:8]
            neg = sorted(contribs, key=lambda x: x[2])[:6]
        except Exception:
            pos, neg = [], []
        probs_map = {name: float(p) for name, p in zip(class_names, probs)}
        return final_label, probs_map, pos, neg, None
    except Exception as e:
        return None, None, None, None, f"Model predict error: {e}"

# -------------------------
# UI: layout & sidebar (versioned keys so Clear resets)
# -------------------------
st.set_page_config(page_title="Narrative Nexus", layout="wide")
st.markdown("""
    <style>
      .stApp { background: linear-gradient(120deg, #071129 0%, #0ea5e9 60%); color: #fff; }
      .css-1d391kg { background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01)); }
      .stButton>button { border-radius: 8px; padding: 8px 10px; }
      .sidebar .stTextInput, .sidebar .stTextArea { color: #000 !important; }
    </style>
""", unsafe_allow_html=True)

# Callbacks used by buttons
def analyze_action():
    st.session_state["analysis_ready"] = True
    # ensure previous choice removed so selectbox appears fresh
    if "analysis_choice" in st.session_state:
        try:
            del st.session_state["analysis_choice"]
        except Exception:
            pass

def clear_inputs():
    # increment versions to rotate widget keys -> new empty widgets
    st.session_state["input_version"] = st.session_state.get("input_version", 0) + 1
    st.session_state["uploader_version"] = st.session_state.get("uploader_version", 0) + 1
    st.session_state["analysis_ready"] = False
    st.session_state["cleared_at"] = st.session_state.get("cleared_at", 0) + 1
    # remove any previous analysis choice if present
    if "analysis_choice" in st.session_state:
        try:
            del st.session_state["analysis_choice"]
        except Exception:
            pass

with st.sidebar:
    st.header("Narrative Nexus — Input")
    col1, col2 = st.columns([1,1])
    with col1:
        st.button("Analyze", on_click=analyze_action)
    with col2:
        st.button("Clear", on_click=clear_inputs)

    st.write("")  # spacing

    # Construct versioned widget keys
    input_key = f"input_text_v{st.session_state.get('input_version', 0)}"
    uploader_key = f"uploaded_file_v{st.session_state.get('uploader_version', 0)}"

    # Use last snapshot if available (helps on reruns)
    initial_text = st.session_state.get("last_input_snapshot", "")

    # Create widgets with versioned keys (these will be new / empty after Clear)
    st.text_area("Paste review", key=input_key, height=220, value=initial_text)
    st.file_uploader("Or upload .txt review", type=["txt"], key=uploader_key)

    st.markdown("---")
    st.markdown("**Detected files in models/**")
    md = "models"
    if os.path.exists(md):
        for f in sorted(os.listdir(md)):
            st.write(f"- {f}")
    else:
        st.write("models/ not found")

# -------------------------
# Main area
# -------------------------
st.title("Narrative Nexus")

# Show any load errors to the user
if load_errors:
    for e in load_errors:
        st.warning(e)

# Read current inputs via versioned keys
text = read_current_inputs()
if not text or not text.strip():
    st.info("Paste or upload a review, then click Analyze.")
    st.stop()

st.subheader("Review preview")
with st.expander("Show review", expanded=False):
    st.write(text[:8000] + ("..." if len(text) > 8000 else ""))

# Show selectbox only after Analyze clicked
if st.session_state.get("analysis_ready", False):
    st.markdown("### Choose analysis")
    _ = st.selectbox(
        "Choose one",
        [
            "Sentiment Detection",
            "Extractive Summary",
            "Topic Distribution",
            "Word Cloud",
            "Visualization (All)"
        ],
        key="analysis_choice"
    )
else:
    st.info("Click Analyze in the sidebar to choose an analysis.")

choice = st.session_state.get("analysis_choice")
if not choice:
    st.stop()

# -------------------------
# Analysis branches
# -------------------------
if choice == "Sentiment Detection":
    st.header("Sentiment Detection")
    final_label, probs_map, pos, neg, msg = explain_prediction(text)
    if msg:
        st.error(msg)
    else:
        st.markdown(f"### Model sentiment: **{final_label}**")
        if probs_map:
            st.pyplot(small_sent_pie(probs_map))
        if pos:
            st.markdown("**Top supporting tokens:**")
            for w, tf, s in pos:
                st.write(f"- {w} — tfidf={tf:.4f}, contrib={s:.4f}")
        if neg:
            st.markdown("**Top opposing tokens:**")
            for w, tf, s in neg:
                st.write(f"- {w} — tfidf={tf:.4f}, contrib={s:.4f}")

elif choice == "Extractive Summary":
    st.header("Extractive Summary")
    s = extractive_summary(text, n=3)
    st.markdown("**Summary:**")
    st.write(s)
    st.markdown("**Top 3 actionable insights (auto):**")
    insights = []
    t = text.lower()
    if any(k in t for k in ("mushy","stale","spoiled","disappointing","bad")):
        insights.append("Investigate product quality (texture/taste).")
    if "price" in t or "value" in t:
        insights.append("Consider pricing/value promotions.")
    if "packag" in t or "arriv" in t or "damag" in t:
        insights.append("Review packaging/shipping procedures.")
    if not insights:
        insights = ["No urgent flags detected; consider improving standout flavour or perceived value."]
    for i, it in enumerate(insights[:3], 1):
        st.write(f"{i}. {it}")

elif choice == "Topic Distribution":
    st.header("Topic Distribution")
    if not GENSIM_AVAILABLE or lda_model is None or lda_dictionary is None:
        st.warning("Topic model/dictionary missing in models/. Drop gensim LDA + dictionary files into ./models/ to enable.")
    else:
        td = doc_topic_distribution(text)
        if not td:
            st.info("No topic distribution produced for this input.")
        else:
            f = plot_topic_bar(td)
            if f:
                st.pyplot(f)
            st.markdown("**Top words per topic:**")
            for tid, prob, kws in td:
                st.write(f"Topic {tid} ({prob:.3f}): " + ", ".join(kws))

elif choice == "Word Cloud":
    st.header("Word Cloud")
    f = wordcloud_fig(text)
    if f:
        st.pyplot(f)
    else:
        st.info("Text too short to create a word cloud.")

elif choice == "Visualization (All)":
    st.header("Visualization Dashboard")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Sentiment")
        final_label, probs_map, pos, neg, msg = explain_prediction(text)
        if msg:
            st.info(msg)
        else:
            if probs_map:
                st.pyplot(small_sent_pie(probs_map))
            st.markdown(f"**Model sentiment:** {final_label}")
    with c2:
        st.subheader("Top words")
        freq = top_words(text, topn=10)
        if freq:
            words, counts = zip(*freq)
            fig, ax = plt.subplots(figsize=(5,2.5))
            ax.barh(words[::-1], counts[::-1])
            ax.set_title("Top words")
            ax.invert_yaxis()
            fig.tight_layout()
            st.pyplot(fig)
        else:
            st.info("No top words.")
    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Topic distribution")
        if GENSIM_AVAILABLE and lda_model is not None and lda_dictionary is not None:
            td = doc_topic_distribution(text)
            if td:
                f = plot_topic_bar(td)
                if f:
                    st.pyplot(f)
                st.markdown("**Top words per topic:**")
                for tid, prob, kws in td:
                    st.write(f"Topic {tid} ({prob:.3f}): " + ", ".join(kws))
        else:
            st.info("Topic model not available.")
    with c4:
        st.subheader("Word cloud")
        f = wordcloud_fig(text)
        if f:
            st.pyplot(f)
        else:
            st.info("Text too short.")

