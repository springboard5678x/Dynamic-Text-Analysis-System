import re
import math
import heapq
import nltk
import streamlit as st
import numpy as np
from typing import List
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

try:
    lemmatizer = WordNetLemmatizer()
    STOPWORDS = set(nltk.corpus.stopwords.words("english"))
except Exception:
    lemmatizer = None
    STOPWORDS = set()

_TRANSFORMERS_AVAILABLE = False

def try_enable_transformers():
    global _TRANSFORMERS_AVAILABLE
    if _TRANSFORMERS_AVAILABLE:
        return True, None
    try:
        from transformers import pipeline, AutoTokenizer
        import torch
        _TRANSFORMERS_AVAILABLE = True
        return True, None
    except Exception as e:
        _TRANSFORMERS_AVAILABLE = False
        return False, f"Transformers unavailable ({str(e)[:50]})"

_SENT_SPLIT_RE = re.compile(r'(?<=[.!?])\s+')

def split_sentences(text: str) -> List[str]:
    sents = [s.strip() for s in _SENT_SPLIT_RE.split(text) if s.strip()]
    return sents or [text.strip()]

def word_tokens(text: str) -> List[str]:
    return [w.lower() for w in re.findall(r"\w+", text)]

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    t = text.lower()
    t = t.translate(str.maketrans("", "", r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""))
    toks = [lemmatizer.lemmatize(w) for w in t.split() if w and w not in STOPWORDS] if lemmatizer else t.split()
    return " ".join(toks)

def extractive_reduce(text: str, ratio: float = 0.3, min_sentences: int = 1, max_sentences: int = 6) -> str:
    sentences = split_sentences(text)
    if len(sentences) <= 1:
        return text

    word_freq = {}
    for sent in sentences:
        for w in word_tokens(sent):
            if w not in STOPWORDS:
                word_freq[w] = word_freq.get(w, 0) + 1
    if not word_freq:
        return " ".join(sentences[:min_sentences])

    max_freq = max(word_freq.values())
    for w in word_freq:
        word_freq[w] /= max_freq

    scores = []
    for i, sent in enumerate(sentences):
        words = word_tokens(sent)
        score = sum(word_freq.get(w, 0) for w in words) / (len(words) + 1e-6)
        scores.append((score, i, sent))

    keep = max(min_sentences, min(max_sentences, math.ceil(len(sentences) * ratio)))
    top = heapq.nlargest(keep, scores, key=lambda x: (x[0], -x[1]))
    top_sorted = sorted(top, key=lambda x: x[1])
    return " ".join(s for (_score, _i, s) in top_sorted)

@st.cache_resource(show_spinner=False)
def make_abstractive_pipeline(model_name: str = "t5-small"):
    avail, err = try_enable_transformers()
    if not avail:
        raise RuntimeError(err or "models not available")
    from transformers import pipeline
    import torch as _torch
    device = 0 if _torch.cuda.is_available() else -1
    return pipeline("summarization", model=model_name, tokenizer=model_name, device=device)

def trim_for_model(text: str, model_name: str, fraction_of_model_max: float = 0.9) -> str:
    avail, err = try_enable_transformers()
    if not avail:
        return text
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model_max = getattr(tokenizer, "model_max_length", 512) or 1024
    budget = max(64, int(model_max * fraction_of_model_max))
    sentences = split_sentences(text)
    if not sentences:
        return text

    def token_count(s: str) -> int:
        return len(tokenizer.encode(s, add_special_tokens=False, truncation=False))

    joined = " ".join(sentences)
    if token_count(joined) <= budget:
        return joined

    trimmed_sents, current_tokens = [], 0
    for sent in sentences:
        sent_tokens = token_count(sent)
        if current_tokens + sent_tokens + 2 <= budget:
            trimmed_sents.append(sent)
            current_tokens += sent_tokens
        elif current_tokens == 0:
            ids = tokenizer.encode(sent, add_special_tokens=False)[:budget]
            return tokenizer.decode(ids, skip_special_tokens=True)
    return " ".join(trimmed_sents)

def abstractive_summarize_text(text: str, model_name: str = "t5-small", max_length: int = 120, min_length: int = 20, use_reduced: bool = True) -> str:
    avail, err = try_enable_transformers()
    if not avail:
        raise RuntimeError(err or "models not available")
    reduced = extractive_reduce(text, ratio=0.25, min_sentences=1, max_sentences=6) if use_reduced else text
    trimmed = trim_for_model(reduced, model_name)
    summarizer = make_abstractive_pipeline(model_name)
    out = summarizer(trimmed, max_length=max_length, min_length=min_length, do_sample=False)
    if isinstance(out, list) and out:
        return out[0].get("summary_text", "").strip()
    return str(out)

def extract_keywords(text: str, top_n: int = 8) -> List[str]:
    tfidf = TfidfVectorizer(stop_words='english', max_features=5000)
    X = tfidf.fit_transform([text])
    scores = zip(tfidf.get_feature_names_out(), np.asarray(X.sum(axis=0)).ravel())
    sorted_keywords = sorted(scores, key=lambda x: x[1], reverse=True)
    return [k for k, _ in sorted_keywords[:top_n]]

def extract_topics(text: str, n_topics: int = 1, n_words: int = 6) -> List[str]:
    tfidf = TfidfVectorizer(stop_words='english', max_features=1000)
    X = tfidf.fit_transform([text])
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=0)
    lda.fit(X)
    terms = tfidf.get_feature_names_out()
    topics = []
    for comp in lda.components_:
        top_terms = [terms[i] for i in comp.argsort()[:-n_words - 1:-1]]
        topics.append(", ".join(top_terms))
    return topics

def generate_recommendations(text: str, sentiment_label: str, keywords: List[str], topics: List[str]) -> List[str]:
    recs = []
    low_sent = sentiment_label.lower()
    if "negative" in low_sent:
        recs.append("⚠️ Text indicates dissatisfaction — consider deeper root-cause analysis.")
    elif "neutral" in low_sent:
        recs.append("🟡 Neutral tone — possible lack of engagement or clarity.")
    elif "positive" in low_sent:
        recs.append("✅ Positive insights — maintain and amplify these strengths.")
    if any(word in text.lower() for word in ["delay", "slow", "issue", "problem"]):
        recs.append("📊 Operational delays detected — optimize workflow or communication.")
    if "customer" in text.lower():
        recs.append("💬 Customer-focused improvement recommended.")
    if not recs:
        recs.append("ℹ️ No specific action detected — consider contextual review.")
    return recs
