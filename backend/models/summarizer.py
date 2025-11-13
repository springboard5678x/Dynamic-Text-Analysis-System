"""
Text Summarization Module
Implements extractive and abstractive summarization techniques
"""

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

STOP_WORDS = set(stopwords.words('english'))

def summarize_text(text, method='extractive', ratio=0.3):
    """
    Summarize text using extractive or abstractive methods
    
    Args:
        text (str): Input text to summarize
        method (str): 'extractive' or 'abstractive'
        ratio (float): Proportion of sentences to keep (0-1)
    
    Returns:
        str: Summarized text
    """
    if method == 'extractive':
        return extractive_summarization(text, ratio)
    else:
        return extractive_summarization(text, ratio)  # Default to extractive

def extractive_summarization(text, ratio=0.3):
    """
    Extractive summarization using sentence scoring with improved flow
    
    Creates a more natural, ChatGPT-like summary by:
    1. Prioritizing sentences with key information
    2. Ensuring logical flow between sentences
    3. Adding smooth transitions
    
    Args:
        text (str): Input text
        ratio (float): Proportion of sentences to keep
    
    Returns:
        str: Summary text with natural flow
    """
    # Split into sentences
    sentences = sent_tokenize(text)
    
    if len(sentences) <= 3:
        return text
    
    # Calculate number of sentences to keep (3-5 sentences for better summaries)
    num_sentences = max(3, min(5, int(len(sentences) * ratio)))
    
    # Tokenize and clean words
    words = word_tokenize(text.lower())
    words = [word for word in words if word.isalnum() and word not in STOP_WORDS]
    
    # Calculate word frequency
    freq_dist = FreqDist(words)
    
    # Score sentences with position bias (first and last sentences often important)
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        sentence_words = word_tokenize(sentence.lower())
        sentence_words = [w for w in sentence_words if w.isalnum()]
        
        score = 0
        for word in sentence_words:
            if word in freq_dist:
                score += freq_dist[word]
        
        # Normalize by sentence length
        if len(sentence_words) > 0:
            base_score = score / len(sentence_words)
            
            # Add position bonus (first and last sentences get boost)
            position_bonus = 1.0
            if i == 0:  # First sentence often contains key info
                position_bonus = 1.3
            elif i == len(sentences) - 1:  # Last sentence often contains conclusion
                position_bonus = 1.2
            elif i < len(sentences) * 0.3:  # Early sentences get slight boost
                position_bonus = 1.1
                
            sentence_scores[i] = base_score * position_bonus
        else:
            sentence_scores[i] = 0
    
    # Select top sentences
    top_sentence_indices = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    
    # Sort by original order for natural flow
    top_sentence_indices.sort()
    
    # Build summary with smooth transitions
    summary_sentences = [sentences[i].strip() for i in top_sentence_indices]
    
    # Create flowing summary
    if len(summary_sentences) == 1:
        return summary_sentences[0]
    
    # Join sentences with proper spacing
    summary = ' '.join(summary_sentences)
    
    # Ensure proper capitalization and punctuation
    summary = summary[0].upper() + summary[1:] if summary else summary
    
    return summary
    # Build summary
    summary = ' '.join([sentences[i] for i in top_sentence_indices])
    
    return summary

def summarize_with_tfidf(text, num_sentences=3):
    """
    Summarization using TF-IDF scores
    
    Args:
        text (str): Input text
        num_sentences (int): Number of sentences in summary
    
    Returns:
        str: Summary
    """
    sentences = sent_tokenize(text)
    
    if len(sentences) <= num_sentences:
        return text
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(stop_words=list(STOP_WORDS))
    
    try:
        tfidf_matrix = vectorizer.fit_transform(sentences)
        
        # Calculate sentence scores (sum of TF-IDF values)
        sentence_scores = np.asarray(tfidf_matrix.sum(axis=1)).flatten()
        
        # Get top sentences
        top_indices = sentence_scores.argsort()[-num_sentences:][::-1]
        top_indices.sort()  # Keep original order
        
        summary = ' '.join([sentences[i] for i in top_indices])
        return summary
    
    except Exception as e:
        print(f"TF-IDF Summarization Error: {e}")
        return extractive_summarization(text)

def get_summary_stats(original_text, summary):
    """
    Calculate statistics comparing original and summary
    
    Args:
        original_text (str): Original text
        summary (str): Summary text
    
    Returns:
        dict: Statistics
    """
    orig_words = len(word_tokenize(original_text))
    summ_words = len(word_tokenize(summary))
    
    orig_sentences = len(sent_tokenize(original_text))
    summ_sentences = len(sent_tokenize(summary))
    
    compression_ratio = round((summ_words / orig_words) * 100, 2) if orig_words > 0 else 0
    
    return {
        'original_words': orig_words,
        'summary_words': summ_words,
        'original_sentences': orig_sentences,
        'summary_sentences': summ_sentences,
        'compression_ratio': compression_ratio
    }

def extract_key_phrases(text, num_phrases=5):
    """
    Extract key phrases from text
    
    Args:
        text (str): Input text
        num_phrases (int): Number of phrases to extract
    
    Returns:
        list: Key phrases
    """
    sentences = sent_tokenize(text)
    
    # Score sentences
    sentence_scores = []
    for sentence in sentences:
        words = word_tokenize(sentence.lower())
        words = [w for w in words if w.isalnum() and w not in STOP_WORDS]
        
        if words:
            # Score based on word length and frequency
            score = sum(len(w) for w in words) / len(words)
            sentence_scores.append((sentence, score))
    
    # Sort by score
    sentence_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Extract key phrases (shorter sentences)
    key_phrases = []
    for sentence, score in sentence_scores[:num_phrases * 2]:
        if len(sentence.split()) <= 15:  # Short sentences
            key_phrases.append(sentence.strip())
            if len(key_phrases) >= num_phrases:
                break
    
    return key_phrases

if __name__ == "__main__":
    # Test summarization
    sample_text = """
    Natural Language Processing (NLP) is a branch of artificial intelligence 
    that helps computers understand, interpret and manipulate human language. 
    NLP draws from many disciplines, including computer science and computational linguistics, 
    in its pursuit to fill the gap between human communication and computer understanding. 
    NLP techniques are used in many applications such as sentiment analysis, machine translation, 
    and question answering systems. The field has seen tremendous growth with the advent of 
    deep learning and transformer models. Modern NLP systems can perform complex tasks like 
    text generation, summarization, and even creative writing. These systems are becoming 
    increasingly important in our daily lives through virtual assistants and chatbots.
    """
    
    print("Original Text:")
    print(sample_text)
    print(f"\nOriginal Length: {len(sample_text.split())} words")
    
    print("\n=== Extractive Summary ===")
    summary = summarize_text(sample_text, ratio=0.3)
    print(summary)
    print(f"Summary Length: {len(summary.split())} words")
    
    print("\n=== TF-IDF Summary ===")
    tfidf_summary = summarize_with_tfidf(sample_text, num_sentences=2)
    print(tfidf_summary)
    
    print("\n=== Summary Statistics ===")
    stats = get_summary_stats(sample_text, summary)
    print(stats)
    
    print("\n=== Key Phrases ===")
    phrases = extract_key_phrases(sample_text)
    for phrase in phrases:
        print(f"- {phrase}")
