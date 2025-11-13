"""
Topic Modeling Module
Implements LDA, NMF, and TF-IDF for topic extraction
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

STOP_WORDS = list(stopwords.words('english'))

def extract_topics(text, n_topics=10, method='tfidf'):
    """
    Extract topics from text using various methods
    
    Args:
        text (str): Input text
        n_topics (int): Number of topics to extract
        method (str): Method to use ('tfidf', 'lda', 'nmf')
    
    Returns:
        list: List of topics with weights
    """
    if method == 'tfidf':
        return extract_topics_tfidf(text, n_topics)
    elif method == 'lda':
        return extract_topics_lda(text, n_topics)
    elif method == 'nmf':
        return extract_topics_nmf(text, n_topics)
    else:
        return extract_topics_tfidf(text, n_topics)

def extract_topics_tfidf(text, n_topics=10):
    """
    Extract topics using TF-IDF
    
    TF-IDF (Term Frequency-Inverse Document Frequency):
    - TF: How frequently a term appears in a document
    - IDF: How unique/important the term is across documents
    - Formula: TF-IDF = TF × IDF
    
    Args:
        text (str): Input text
        n_topics (int): Number of topics to extract
    
    Returns:
        list: Topics with TF-IDF scores
    """
    # Split text into sentences (treat each as a document)
    sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
    
    if len(sentences) < 2:
        # If too few sentences, use word-based approach
        words = word_tokenize(text.lower())
        words = [w for w in words if w.isalnum() and w not in STOP_WORDS and len(w) > 3]
        
        # Count frequencies
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort and return top topics
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        topics = [{'word': word, 'weight': round(freq / len(words), 4)} 
                 for word, freq in sorted_words[:n_topics]]
        
        return topics
    
    # Use TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=100,
        stop_words=STOP_WORDS,
        ngram_range=(1, 2),  # Include bigrams
        min_df=1,
        max_df=0.95
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(sentences)
        feature_names = vectorizer.get_feature_names_out()
        
        # Sum TF-IDF scores across all documents
        tfidf_scores = np.asarray(tfidf_matrix.sum(axis=0)).flatten()
        
        # Get top terms
        top_indices = tfidf_scores.argsort()[-n_topics:][::-1]
        
        topics = []
        for idx in top_indices:
            if idx < len(feature_names):
                topics.append({
                    'word': feature_names[idx],
                    'weight': round(float(tfidf_scores[idx]), 4)
                })
        
        return topics
    
    except Exception as e:
        print(f"TF-IDF Error: {e}")
        return []

def extract_topics_lda(text, n_topics=5):
    """
    Extract topics using Latent Dirichlet Allocation (LDA)
    
    LDA is a probabilistic model that:
    - Assumes documents are mixtures of topics
    - Topics are distributions over words
    - Uses Bayesian inference to discover hidden topics
    
    Args:
        text (str): Input text
        n_topics (int): Number of topics to discover
    
    Returns:
        list: Topics discovered by LDA
    """
    sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
    
    if len(sentences) < n_topics:
        n_topics = max(1, len(sentences) - 1)
    
    # Use CountVectorizer for LDA
    vectorizer = CountVectorizer(
        max_features=100,
        stop_words=STOP_WORDS,
        min_df=1,
        max_df=0.95
    )
    
    try:
        doc_term_matrix = vectorizer.fit_transform(sentences)
        feature_names = vectorizer.get_feature_names_out()
        
        # Apply LDA
        lda = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            max_iter=20
        )
        lda.fit(doc_term_matrix)
        
        # Extract top words from each topic
        topics = []
        for topic_idx, topic in enumerate(lda.components_):
            top_indices = topic.argsort()[-5:][::-1]
            top_words = [feature_names[i] for i in top_indices if i < len(feature_names)]
            
            for word_idx, word in enumerate(top_words):
                topics.append({
                    'word': word,
                    'weight': round(float(topic[top_indices[word_idx]]), 4),
                    'topic_number': topic_idx + 1
                })
        
        # Sort by weight and return top 10
        topics = sorted(topics, key=lambda x: x['weight'], reverse=True)[:10]
        
        return topics
    
    except Exception as e:
        print(f"LDA Error: {e}")
        return extract_topics_tfidf(text, 10)

def extract_topics_nmf(text, n_topics=5):
    """
    Extract topics using Non-negative Matrix Factorization (NMF)
    
    NMF decomposes the document-term matrix into:
    - Document-topic matrix
    - Topic-term matrix
    - Assumes non-negative values
    
    Args:
        text (str): Input text
        n_topics (int): Number of topics
    
    Returns:
        list: Topics discovered by NMF
    """
    sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
    
    if len(sentences) < n_topics:
        n_topics = max(1, len(sentences) - 1)
    
    # Use TF-IDF for NMF
    vectorizer = TfidfVectorizer(
        max_features=100,
        stop_words=STOP_WORDS,
        min_df=1,
        max_df=0.95
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(sentences)
        feature_names = vectorizer.get_feature_names_out()
        
        # Apply NMF
        nmf = NMF(
            n_components=n_topics,
            random_state=42,
            max_iter=200
        )
        nmf.fit(tfidf_matrix)
        
        # Extract top words from each topic
        topics = []
        for topic_idx, topic in enumerate(nmf.components_):
            top_indices = topic.argsort()[-5:][::-1]
            top_words = [feature_names[i] for i in top_indices if i < len(feature_names)]
            
            for word_idx, word in enumerate(top_words):
                topics.append({
                    'word': word,
                    'weight': round(float(topic[top_indices[word_idx]]), 4),
                    'topic_number': topic_idx + 1
                })
        
        # Sort by weight and return top 10
        topics = sorted(topics, key=lambda x: x['weight'], reverse=True)[:10]
        
        return topics
    
    except Exception as e:
        print(f"NMF Error: {e}")
        return extract_topics_tfidf(text, 10)

if __name__ == "__main__":
    # Test topic modeling
    sample_text = """
    Machine learning is a subset of artificial intelligence that focuses on 
    building systems that can learn from data. Natural language processing is 
    another important field that deals with human language understanding. 
    Deep learning has revolutionized both fields with neural networks. 
    Computer vision and image recognition are also important AI applications.
    """
    
    print("=== TF-IDF Topics ===")
    tfidf_topics = extract_topics_tfidf(sample_text)
    for topic in tfidf_topics:
        print(f"{topic['word']}: {topic['weight']}")
    
    print("\n=== LDA Topics ===")
    lda_topics = extract_topics_lda(sample_text, n_topics=3)
    for topic in lda_topics:
        print(f"{topic['word']}: {topic['weight']} (Topic {topic.get('topic_number', '')})")
    
    print("\n=== NMF Topics ===")
    nmf_topics = extract_topics_nmf(sample_text, n_topics=3)
    for topic in nmf_topics:
        print(f"{topic['word']}: {topic['weight']} (Topic {topic.get('topic_number', '')})")
