import streamlit as st
import joblib
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
import numpy as np
from collections import Counter
import plotly.graph_objects as go
import plotly.express as px

# Download required NLTK data
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Page configuration
st.set_page_config(page_title="NarrativeNexus", page_icon="📊", layout="wide")

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-weight: 600;
    }
    .insight-card {
        background-color: #f0f2f6;
        padding: 12px 14px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #1f77b4;
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 10px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 110px;
    }
    .metric-card h3 {
        margin: 0;
        color: #1f77b4;
        font-size: 2em;
        font-weight: bold;
        text-align: center;
    }
    .metric-card p {
        margin: 5px 0 0 0;
        color: #666;
        font-size: 0.9em;
    }
    .metric-card [data-testid='stHeaderActionElements'] {
        display: none !important;
    }
    h1 {
        color: #1f77b4;
        padding-bottom: 10px;
    }
    .insight-number {
        width: 34px;
        height: 34px;
        background: #1f77b4;
        color: #fff;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        flex: 0 0 34px;
    }

    .insight-text {
        flex: 1 1 auto;
        color: #333;
    }

    .recommendation-box {
        background-color: #e8f4f8;
        padding: 12px 14px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #2ecc71;
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }

    .rec-number {
        width: 34px;
        height: 34px;
        background: #2ecc71;
        color: #fff;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        flex: 0 0 34px;
    }

    .rec-text {
        flex: 1 1 auto;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title("📊 NarrativeNexus: Dynamic Text Analysis Platform")
st.markdown("**Extract themes, analyze sentiment, and generate actionable insights from your text data**")
st.markdown("---")

# Load models
@st.cache_resource
def load_models():
    try:
        with open('lda_model.pkl', 'rb') as f:
            lda_model = joblib.load(f)
        with open('sentiment_model.pkl', 'rb') as f:
            sentiment_model = joblib.load(f)
        with open('train_dictionary.pkl', 'rb') as f:
            train_dictionary = joblib.load(f)
        with open('vectorizer.pkl', 'rb') as f:
            vectorizer = joblib.load(f)
        return lda_model, train_dictionary, sentiment_model, vectorizer
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None, None, None, None

def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return nltk.corpus.wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return nltk.corpus.wordnet.VERB
    elif treebank_tag.startswith('N'):
        return nltk.corpus.wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return nltk.corpus.wordnet.ADV
    else:
        return nltk.corpus.wordnet.NOUN

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    stop_words = set(stopwords.words('english'))
    words = text.split()
    words = [word for word in words if word not in stop_words]
    tagged_tokens = nltk.pos_tag(words)
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word, get_wordnet_pos(pos)) for word, pos in tagged_tokens]
    return ' '.join(words)

def generate_insights(sentiment, topic_dist, text_data, cleaned_text):
    """Generate actionable insights based on analysis"""
    insights = []
    recommendations = []

    # Sentiment-based insights
    if sentiment in ['negative', -1]:
        insights.append("Negative sentiment detected: The text expresses dissatisfaction or concerns.")
        recommendations.append("Investigate specific pain points mentioned in the text")
        recommendations.append("Consider immediate action to address negative feedback")
    elif sentiment in ['positive', 1]:
        insights.append("Positive sentiment detected: The text reflects satisfaction and approval.")
        recommendations.append("Identify and replicate successful elements")
        recommendations.append("Use these insights for testimonials or case studies")
    else:
        insights.append("Neutral sentiment detected: The text is objective and balanced.")
        recommendations.append("Look for opportunities to enhance emotional engagement")

    # Topic-based insights
    if topic_dist:
        top_topic = max(topic_dist, key=lambda x: x[1])
        if top_topic[1] > 0.5:
            insights.append(f"Strong thematic focus: Topic {top_topic[0] + 1} dominates ({top_topic[1]:.0%} of content)")
            recommendations.append("Content is well-focused on main theme")
        elif top_topic[1] < 0.3:
            insights.append(f"Diverse topics: No single dominant theme identified")
            recommendations.append("Consider refining focus or creating separate analyses for distinct topics")

    # Text complexity insights
    words = cleaned_text.split()
    sentences = nltk.sent_tokenize(text_data)
    avg_sentence_length = len(words) / len(sentences) if sentences else 0

    if avg_sentence_length > 25:
        insights.append("Complex text structure: Long sentences detected")
        recommendations.append("Consider simplifying language for better readability")
    elif avg_sentence_length < 10:
        insights.append("Concise writing style: Short, direct sentences")
        recommendations.append("Maintain clarity while adding depth where needed")

    # Content volume insights
    word_count = len(words)
    if word_count < 50:
        insights.append("Brief content: Limited text for comprehensive analysis")
        recommendations.append("Provide more context for deeper insights")
    elif word_count > 500:
        insights.append("Comprehensive content: Rich text with substantial detail")
        recommendations.append("Consider breaking into sections for targeted analysis")

    return insights, recommendations

def create_topic_distribution_chart(probs, num_topics):
    """Create interactive topic distribution chart"""
    fig = go.Figure(data=[
        go.Bar(x=[f'Topic {i+1}' for i in range(num_topics)],
               y=probs,
               marker_color='#1f77b4',
               text=[f'{p:.1%}' for p in probs],
               textposition='auto')
    ])
    fig.update_layout(
        title='Topic Distribution',
        xaxis_title='Topics',
        yaxis_title='Probability',
        height=400,
        template='plotly_white'
    )
    return fig

def create_sentiment_chart(labels, proba):
    """Create interactive sentiment distribution chart"""
    colors = {'Positive': '#2ecc71', 'Negative': '#e74c3c', 'Neutral': '#95a5a6'}
    bar_colors = [colors.get(str(label), '#1f77b4') for label in labels]

    fig = go.Figure(data=[
        go.Bar(x=labels,
               y=proba,
               marker_color=bar_colors,
               text=[f'{p:.1%}' for p in proba],
               textposition='auto')
    ])
    fig.update_layout(
        title='Sentiment Distribution',
        xaxis_title='Sentiment',
        yaxis_title='Probability',
        height=400,
        template='plotly_white'
    )
    return fig

def main():
    # Load models
    lda_model, train_dictionary, sentiment_model, vectorizer = load_models()

    if lda_model is None or sentiment_model is None:
        st.warning("⚠️ Please ensure all model files are in the same folder as this script.")
        return

    # Sidebar
    st.sidebar.header("📝 Input Options")
    input_method = st.sidebar.radio("Choose input method:", ["Text Input", "File Upload"])

    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info("NarrativeNexus uses advanced NLP techniques including LDA topic modeling, sentiment analysis, and extractive summarization to provide comprehensive text insights.")

    text_data = ""

    if input_method == "Text Input":
        text_data = st.text_area("Enter your text here:", height=200,
                                 placeholder="Paste your text for analysis...")
    else:
        uploaded_file = st.file_uploader("Upload a text file", type=['txt'])
        if uploaded_file is not None:
            if uploaded_file.type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                try:
                    import docx
                    doc = docx.Document(uploaded_file)
                    text_data = '\n'.join([para.text for para in doc.paragraphs])
                except:
                    st.error("Please install python-docx: pip install python-docx")
            else:
                text_data = uploaded_file.read().decode('utf-8', errors='replace')
            st.text_area("File Content:", text_data, height=150)

    # Analysis button
    if st.button("🔍 Analyze Text", type="primary"):
        if text_data.strip():
            with st.spinner("Analyzing your text..."):
                # Preprocess text
                cleaned_text = preprocess_text(text_data)

                # Quick Stats
                st.subheader("📈 Text Statistics")
                col1, col2, col3, col4 = st.columns(4)

                words = cleaned_text.split()
                sentences = nltk.sent_tokenize(text_data)

                with col1:
                    st.markdown(f'''
                    <div class="metric-card">
                        <h3>{len(words)}</h3>
                        <p>Total Words</p>
                    </div>
                    ''', unsafe_allow_html=True)

                with col2:
                    st.markdown(f'''
                    <div class="metric-card">
                        <h3>{len(sentences)}</h3>
                        <p>Sentences</p>
                    </div>
                    ''', unsafe_allow_html=True)

                with col3:
                    st.markdown(f'''
                    <div class="metric-card">
                        <h3>{   len(text_data)}</h3>
                        <p>Characters</p>
                    </div>
                    ''', unsafe_allow_html=True)

                with col4:
                    avg_word_len = sum(len(word) for word in words) / len(words) if words else 0
                    st.markdown(f'''
                    <div class="metric-card">
                        <h3>{   avg_word_len:.1f}</h3>
                        <p>Avg Word Length</p>
                    </div>
                    ''', unsafe_allow_html=True)

                st.markdown("---")

                # Main Analysis
                col1, col2 = st.columns(2)

                sentiment = None
                topic_dist = None

                # Topic Modeling
                with col1:
                    st.subheader("🎯 Topic Modeling")
                    try:
                        processed_tokens = cleaned_text.split()
                        text_vectorized = [train_dictionary.doc2bow(processed_tokens)]
                        topic_dist = lda_model.get_document_topics(text_vectorized[0], minimum_probability=0)

                        num_topics = lda_model.num_topics
                        probs = [0] * num_topics
                        for topic_id, prob in topic_dist:
                            probs[topic_id] = prob

                        top_topic_idx = max(topic_dist, key=lambda x: x[1])

                        st.success(f"**Dominant Topic:** Topic {top_topic_idx[0] + 1} ({top_topic_idx[1]:.1%})")

                        # Interactive chart
                        fig = create_topic_distribution_chart(probs, num_topics)
                        st.plotly_chart(fig, use_container_width=True)

                    except Exception as e:
                        st.error(f"Topic modeling error: {e}")

                # Sentiment Analysis
                with col2:
                    st.subheader("😊 Sentiment Analysis")
                    try:
                        cleaned_text_vectorized = vectorizer.transform([cleaned_text])
                        sentiment = sentiment_model.predict(cleaned_text_vectorized)[0]

                        sentiment_emoji = {
                            'positive': '😊 Positive',
                            'negative': '😞 Negative',
                            'neutral': '😐 Neutral',
                            1: '😊 Positive',
                            0: '😐 Neutral',
                            -1: '😞 Negative'
                        }

                        st.success(f"**Detected Sentiment:** {sentiment_emoji.get(sentiment, sentiment)}")

                        if hasattr(sentiment_model, 'predict_proba'):
                            proba = sentiment_model.predict_proba(cleaned_text_vectorized)[0]
                            labels = sentiment_model.classes_ if hasattr(sentiment_model, 'classes_') else ['Negative', 'Neutral', 'Positive']

                            # Interactive chart
                            fig = create_sentiment_chart(labels, proba)
                            st.plotly_chart(fig, use_container_width=True)

                    except Exception as e:
                        st.error(f"Sentiment analysis error: {e}")

                st.markdown("---")

                # Word Cloud
                st.subheader("☁️ Key Terms Visualization")
                try:
                    wordcloud = WordCloud(width=800, height=400,
                                         background_color='white',
                                         colormap='viridis',
                                         max_words=50).generate(cleaned_text)
                    fig, ax = plt.subplots(figsize=(8, 4))
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis('off')
                    plt.tight_layout(pad=5)
                    st.pyplot(fig)
                except Exception as e:
                    st.error(f"Word cloud error: {e}")

                st.markdown("---")

                # Top Keywords
                st.subheader("🔑 Top Keywords")
                word_freq = Counter(cleaned_text.split())
                top_words = word_freq.most_common(10)

                if top_words:
                    keywords_df = pd.DataFrame(top_words, columns=['Keyword', 'Frequency'])

                    fig = go.Figure(data=[
                        go.Bar(x=keywords_df['Keyword'],
                               y=keywords_df['Frequency'],
                               marker_color='#ff7f0e',
                               text=keywords_df['Frequency'],
                               textposition='auto')
                    ])
                    fig.update_layout(
                        xaxis_title='Keywords',
                        yaxis_title='Frequency',
                        height=400,
                        template='plotly_white'
                    )
                    st.plotly_chart(fig, use_container_width=True)

                st.markdown("---")

                # Summary
                st.subheader("📄 Extractive Summary")
                try:
                    from sentence_transformers import SentenceTransformer
                    from sklearn.metrics.pairwise import cosine_similarity

                    sentences = nltk.sent_tokenize(text_data)

                    if len(sentences) >= 3:
                        sbert_model = SentenceTransformer('all-MiniLM-L6-v2')
                        sentence_embeddings = sbert_model.encode(sentences)

                        sim_matrix = cosine_similarity(sentence_embeddings)
                        sentence_scores = np.zeros(sim_matrix.shape[0])
                        for i in range(sim_matrix.shape[0]):
                            for j in range(sim_matrix.shape[0]):
                                if i != j:
                                    sentence_scores[i] += sim_matrix[i][j]

                        num_summary_sentences = min(3, max(1, len(sentences) // 4))
                        top_sentence_indices = np.argsort(sentence_scores)[::-1][:num_summary_sentences]
                        top_sentence_indices = sorted(top_sentence_indices)
                        summary = " ".join([sentences[i] for i in top_sentence_indices])

                        st.info(summary)
                    else:
                        st.info(text_data)

                except Exception as e:
                    st.warning(f"Summary generation requires: pip install sentence-transformers")

                st.markdown("---")

                # Actionable Insights & Recommendations
                st.subheader("💡 Actionable Insights & Recommendations")

                insights, recommendations = generate_insights(sentiment, topic_dist, text_data, cleaned_text)

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**📊 Key Insights:**")
                    for i, insight in enumerate(insights, 1):
                        st.markdown(
                            f'<div class="insight-card"><span class="insight-number">{i}</span><div class="insight-text">{insight}</div></div>',
                            unsafe_allow_html=True
                        )

                with col2:
                    st.markdown("**🎯 Recommendations:**")
                    for i, rec in enumerate(recommendations, 1):
                        st.markdown(
                            f'<div class="recommendation-box"><span class="rec-number">{i}</span><div class="rec-text">{rec}</div></div>',
                            unsafe_allow_html=True
                        )

                st.markdown("---")

                # Export Results
                st.subheader("📥 Export Results")

                sentiment_emoji = {
                    'positive': 'Positive',
                    'negative': 'Negative',
                    'neutral': 'Neutral',
                    1: 'Positive',
                    0: 'Neutral',
                    -1: 'Negative'
                }

                # Create downloadable report
                report = f"""
NarrativeNexus Analysis Report
{'='*50}

TEXT STATISTICS:
- Total Words: {len(words)}
- Sentences: {len(sentences)}
- Characters: {len(text_data)}

SENTIMENT: {sentiment_emoji.get(sentiment, sentiment)}

TOP KEYWORDS: {', '.join([w for w, _ in top_words[:5]])}

KEY INSIGHTS:
{chr(10).join([f'{i}. {insight}' for i, insight in enumerate(insights, 1)])}

RECOMMENDATIONS:
{chr(10).join([f'{i}. {r}' for i, r in enumerate(recommendations, 1)])}
"""
                st.download_button(
                    label="📄 Download Report",
                    data=report,
                    file_name="analysis_report.txt",
                    mime="text/plain",
                    key="download_report"
                )

        else:
            st.warning("⚠️ Please enter or upload some text to analyze.")

if __name__ == "__main__":
    main()