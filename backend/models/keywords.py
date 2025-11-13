"""
Keyword Extraction Module
Extracts important keywords and phrases from text
"""

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

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

def extract_keywords(text, max_keywords=30, method='tfidf'):
    """
    Extract keywords from text
    
    Args:
        text (str): Input text
        max_keywords (int): Maximum number of keywords to extract
        method (str): Extraction method ('tfidf' or 'frequency')
    
    Returns:
        list: List of keyword dictionaries with text and value
    """
    if method == 'tfidf':
        return extract_keywords_tfidf(text, max_keywords)
    elif method == 'frequency':
        return extract_keywords_frequency(text, max_keywords)
    else:
        return extract_keywords_tfidf(text, max_keywords)

def extract_keywords_frequency(text, max_keywords=30):
    """
    Extract keywords based on frequency
    
    Algorithm:
    1. Tokenize text
    2. Remove stop words
    3. Count word frequencies
    4. Return top N words
    
    Args:
        text (str): Input text
        max_keywords (int): Number of keywords
    
    Returns:
        list: Keywords with frequency counts
    """
    # Tokenize and clean
    words = word_tokenize(text.lower())
    words = [word for word in words if word.isalnum() 
             and word not in STOP_WORDS 
             and len(word) > 3]
    
    # Count frequencies
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    # Format results
    keywords = []
    for word, freq in sorted_words[:max_keywords]:
        keywords.append({
            'text': word,
            'value': freq
        })
    
    return keywords

def extract_keywords_tfidf(text, max_keywords=30):
    """
    Extract keywords using TF-IDF
    
    TF-IDF gives higher scores to:
    - Frequent terms in the document (TF)
    - Rare terms across documents (IDF)
    
    Args:
        text (str): Input text
        max_keywords (int): Number of keywords
    
    Returns:
        list: Keywords with TF-IDF scores
    """
    # Split text into sentences (treat as mini-documents)
    sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
    
    if len(sentences) < 2:
        # Fall back to frequency method for very short texts
        return extract_keywords_frequency(text, max_keywords)
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=max_keywords * 2,
        stop_words=list(STOP_WORDS),
        ngram_range=(1, 2),  # Include single words and bigrams
        min_df=1,
        max_df=0.95
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(sentences)
        feature_names = vectorizer.get_feature_names_out()
        
        # Sum TF-IDF scores across all sentences
        tfidf_scores = np.asarray(tfidf_matrix.sum(axis=0)).flatten()
        
        # Get top keywords
        top_indices = tfidf_scores.argsort()[-max_keywords:][::-1]
        
        keywords = []
        for idx in top_indices:
            if idx < len(feature_names):
                # Scale value for better visualization
                scaled_value = int(tfidf_scores[idx] * 10) + 1
                keywords.append({
                    'text': feature_names[idx],
                    'value': scaled_value
                })
        
        return keywords
    
    except Exception as e:
        print(f"TF-IDF Keyword Extraction Error: {e}")
        return extract_keywords_frequency(text, max_keywords)

def extract_named_entities(text):
    """
    Extract named entities from text (requires additional NLTK data)
    
    Args:
        text (str): Input text
    
    Returns:
        list: Named entities
    """
    try:
        # Download required data
        nltk.download('averaged_perceptron_tagger', quiet=True)
        nltk.download('maxent_ne_chunker', quiet=True)
        nltk.download('words', quiet=True)
        
        # Tokenize and tag
        tokens = word_tokenize(text)
        tagged = nltk.pos_tag(tokens)
        
        # Extract named entities
        entities = nltk.ne_chunk(tagged)
        
        named_entities = []
        for subtree in entities:
            if hasattr(subtree, 'label'):
                entity_name = ' '.join([word for word, tag in subtree.leaves()])
                entity_type = subtree.label()
                named_entities.append({
                    'entity': entity_name,
                    'type': entity_type
                })
        
        return named_entities
    
    except Exception as e:
        print(f"Named Entity Extraction Error: {e}")
        return []

def get_keyword_context(text, keyword, context_window=50):
    """
    Get context around a keyword
    
    Args:
        text (str): Full text
        keyword (str): Keyword to find
        context_window (int): Number of characters before/after
    
    Returns:
        list: List of context snippets
    """
    keyword_lower = keyword.lower()
    text_lower = text.lower()
    
    contexts = []
    start = 0
    
    while True:
        index = text_lower.find(keyword_lower, start)
        if index == -1:
            break
        
        context_start = max(0, index - context_window)
        context_end = min(len(text), index + len(keyword) + context_window)
        
        context = text[context_start:context_end]
        
        # Add ellipsis if needed
        if context_start > 0:
            context = '...' + context
        if context_end < len(text):
            context = context + '...'
        
        contexts.append(context)
        start = index + 1
    
    return contexts

def extract_important_phrases(text, num_phrases=10):
    """
    Extract important noun phrases
    
    Args:
        text (str): Input text
        num_phrases (int): Number of phrases to extract
    
    Returns:
        list: Important phrases
    """
    try:
        nltk.download('averaged_perceptron_tagger', quiet=True)
        
        tokens = word_tokenize(text)
        tagged = nltk.pos_tag(tokens)
        
        # Extract noun phrases (simple pattern: adjective + noun)
        phrases = []
        for i in range(len(tagged) - 1):
            word1, tag1 = tagged[i]
            word2, tag2 = tagged[i + 1]
            
            # Adjective + Noun or Noun + Noun
            if (tag1.startswith('JJ') and tag2.startswith('NN')) or \
               (tag1.startswith('NN') and tag2.startswith('NN')):
                phrase = f"{word1} {word2}"
                if len(phrase) > 5:  # Filter short phrases
                    phrases.append(phrase.lower())
        
        # Count frequencies
        phrase_freq = {}
        for phrase in phrases:
            phrase_freq[phrase] = phrase_freq.get(phrase, 0) + 1
        
        # Sort and return top phrases
        sorted_phrases = sorted(phrase_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [{'phrase': phrase, 'frequency': freq} 
                for phrase, freq in sorted_phrases[:num_phrases]]
    
    except Exception as e:
        print(f"Phrase Extraction Error: {e}")
        return []

if __name__ == "__main__":
    # Test keyword extraction
    sample_text = """
    Machine learning and artificial intelligence are transforming the technology industry. 
    Natural language processing enables computers to understand human language. 
    Deep learning models have achieved remarkable success in various applications. 
    Computer vision and image recognition are important areas of AI research. 
    Data science combines statistics, programming, and domain expertise to extract insights from data.
    """
    
    print("=== Frequency-Based Keywords ===")
    freq_keywords = extract_keywords_frequency(sample_text, 10)
    for kw in freq_keywords:
        print(f"{kw['text']}: {kw['value']}")
    
    print("\n=== TF-IDF Keywords ===")
    tfidf_keywords = extract_keywords_tfidf(sample_text, 10)
    for kw in tfidf_keywords:
        print(f"{kw['text']}: {kw['value']}")
    
    print("\n=== Important Phrases ===")
    phrases = extract_important_phrases(sample_text)
    for phrase in phrases:
        print(f"{phrase['phrase']}: {phrase['frequency']}")
    
    print("\n=== Named Entities ===")
    entities = extract_named_entities(sample_text)
    for entity in entities:
        print(f"{entity['entity']} ({entity['type']})")
