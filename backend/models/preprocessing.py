"""
Text Preprocessing Module
Handles text cleaning, normalization, and tokenization
"""

import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Get English stop words
STOP_WORDS = set(stopwords.words('english'))

def preprocess_text(text, remove_stopwords=True, lemmatize=True):
    """
    Comprehensive text preprocessing
    
    Args:
        text (str): Input text to preprocess
        remove_stopwords (bool): Whether to remove stop words
        lemmatize (bool): Whether to lemmatize words
    
    Returns:
        str: Preprocessed text
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^a-zA-Z0-9\s.,!?]', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Tokenization
    tokens = word_tokenize(text)
    
    # Remove stopwords if requested
    if remove_stopwords:
        tokens = [word for word in tokens if word not in STOP_WORDS and word not in string.punctuation]
    
    # Lemmatization if requested
    if lemmatize:
        tokens = [lemmatizer.lemmatize(word) for word in tokens]
    
    # Rejoin tokens
    preprocessed_text = ' '.join(tokens)
    
    return preprocessed_text

def tokenize_sentences(text):
    """Split text into sentences"""
    return sent_tokenize(text)

def tokenize_words(text):
    """Split text into words"""
    return word_tokenize(text)

def remove_stopwords(tokens):
    """Remove stop words from token list"""
    return [word for word in tokens if word.lower() not in STOP_WORDS]

def get_word_frequency(text):
    """
    Calculate word frequency distribution
    
    Args:
        text (str): Input text
    
    Returns:
        dict: Word frequency dictionary
    """
    tokens = word_tokenize(text.lower())
    tokens = [word for word in tokens if word.isalnum() and word not in STOP_WORDS]
    
    freq_dist = {}
    for token in tokens:
        freq_dist[token] = freq_dist.get(token, 0) + 1
    
    # Sort by frequency
    sorted_freq = dict(sorted(freq_dist.items(), key=lambda x: x[1], reverse=True))
    
    return sorted_freq

if __name__ == "__main__":
    # Test preprocessing
    sample_text = """
    Natural Language Processing (NLP) is a field of artificial intelligence 
    that focuses on the interaction between computers and humans using natural language.
    The ultimate objective of NLP is to read, decipher, understand, and make sense of 
    human languages in a manner that is valuable.
    """
    
    print("Original Text:")
    print(sample_text)
    print("\nPreprocessed Text:")
    print(preprocess_text(sample_text))
    print("\nWord Frequency:")
    print(get_word_frequency(sample_text))
