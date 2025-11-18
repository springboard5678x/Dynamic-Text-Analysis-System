import os
import pickle
import re
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# ---------------------------------------
# Flask Setup
# ---------------------------------------
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

# ---------------------------------------
# Load Models
# ---------------------------------------
with open(os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl"), "rb") as f:
    tfidf_vectorizer = pickle.load(f)

with open(os.path.join(MODEL_DIR, "trained_model.pkl"), "rb") as f:
    sentiment_model = pickle.load(f)

print("MODEL CLASSES:", sentiment_model.classes_)  # [0,1,2]


# ---------------------------------------
# Helper: Map class number → text label
# ---------------------------------------
def map_sentiment(label_id):
    mapping = {0: "Negative", 1: "Neutral", 2: "Positive"}
    return mapping.get(label_id, "Neutral")


# ---------------------------------------
# Clean Wordcloud (Top TF-IDF words)
# ---------------------------------------
def get_wordcloud(text):
    X = tfidf_vectorizer.transform([text])
    indices = X.nonzero()[1]
    scores = X.data

    if len(scores) == 0:
        return []

    order = scores.argsort()[::-1][:30]
    words = tfidf_vectorizer.get_feature_names_out()[indices[order]]

    return [
        {"text": words[i], "weight": float(scores[order][i])}
        for i in range(len(order))
    ]


# ---------------------------------------
# Fixed Food Topics (Not TF-IDF words!)
# ---------------------------------------
TOPIC_KEYWORDS = {
    "Taste & Flavor": [
        "taste", "flavor", "delicious", "bland", "sweet", "bitter", "spicy",
        "artificial", "weird", "off taste"
    ],
    "Freshness": [
        "fresh", "stale", "expired", "rotten", "soggy", "old", "crisp"
    ],
    "Packaging": [
        "packaging", "packet", "seal", "box", "wrapper", "opened", "damaged"
    ],
    "Delivery Experience": [
        "delivery", "arrived", "shipping", "late", "delay"
    ],
    "Texture": [
        "texture", "soft", "hard", "chewy", "crunchy", "crumbly"
    ],
    "Price & Value": [
        "price", "expensive", "cheap", "worth", "value", "overpriced"
    ],
}


def get_topics(text):
    text_low = text.lower()
    scores = {}

    for topic, keywords in TOPIC_KEYWORDS.items():
        score = sum(1 for w in keywords if w in text_low)
        scores[topic] = score

    max_score = max(scores.values()) if scores else 1

    topics = []
    for topic, score in scores.items():
        if score > 0:
            topics.append({
                "label": topic,
                "score": round(score / max_score, 2)
            })

    if not topics:
        topics = [{"label": "General Experience", "score": 1.0}]

    return topics


# ---------------------------------------
# Extractive Summary
# ---------------------------------------
def extractive_summary(text):
    sentences = [s.strip() for s in re.split(r"[.!?]", text) if len(s.strip()) > 6]

    if len(sentences) <= 2:
        return text.strip()

    X = tfidf_vectorizer.transform(sentences)
    scores = X.sum(axis=1).A.ravel()

    idx = scores.argsort()[::-1][:2]
    idx = sorted(idx)

    return ". ".join([sentences[i] for i in idx]) + "."


# ---------------------------------------
# Offline Abstractive Summary (Clean)
# ---------------------------------------
def abstractive_summary(text):
    parts = text.split(". ")
    parts = [p.strip() for p in parts if len(p.strip()) > 5]

    intro = "This review discusses the customer's overall experience regarding the product."
    middle = " ".join(parts[:2]) if len(parts) >= 2 else parts[0]
    end = "Overall, the summary reflects the general sentiment and observations."

    return f"{intro} {middle}. {end}"


# ---------------------------------------
# Insights & Recommendations
# ---------------------------------------
def generate_insights(text, sentiment):
    text_low = text.lower()

    insights = []
    recs = []

    # Sentiment logic
    if sentiment == "Positive":
        insights.append("Customer is satisfied with the overall product experience.")
        recs.append("Highlight positive comments for marketing benefits.")
    elif sentiment == "Neutral":
        insights.append("Customer gives mixed or moderate feedback.")
        recs.append("Encourage more detailed feedback to understand preferences.")
    else:
        insights.append("Customer expresses dissatisfaction and concerns.")
        recs.append("Investigate the issues mentioned to improve product quality.")

    # Topic-specific insights
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(w in text_low for w in keywords):
            insights.append(f"{topic} was discussed in the review.")

    if "stale" in text_low or "expired" in text_low:
        recs.append("Improve freshness and storage conditions.")

    if "packaging" in text_low or "seal" in text_low:
        recs.append("Strengthen packaging quality to avoid damage.")

    if "delivery" in text_low:
        recs.append("Improve delivery speed and accuracy.")

    if not recs:
        recs.append("Monitor customer feedback for more insights.")

    return insights, recs


# ---------------------------------------
# Routes
# ---------------------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"status": "error", "message": "Empty review"}), 400

    # Sentiment
    X = tfidf_vectorizer.transform([text])
    pred_class = sentiment_model.predict(X)[0]
    sentiment_label = map_sentiment(pred_class)

    # Probabilities
    probs = sentiment_model.predict_proba(X)[0]
    prob_dict = {
        map_sentiment(sentiment_model.classes_[i]): float(probs[i])
        for i in range(len(probs))
    }

    topics = get_topics(text)
    wc = get_wordcloud(text)
    ext_sum = extractive_summary(text)
    abs_sum = abstractive_summary(text)
    insights, recs = generate_insights(text, sentiment_label)

    return jsonify({
        "status": "success",
        "sentiment": sentiment_label,
        "probabilities": prob_dict,
        "topics": topics,
        "wordcloud": wc,
        "extractive_summary": ext_sum,
        "abstractive_summary": abs_sum,
        "insights": insights,
        "recommendations": recs
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
