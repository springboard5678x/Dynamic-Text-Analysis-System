"""
Sentiment Analysis Module
Uses TextBlob and VADER for sentiment analysis
"""

from textblob import TextBlob
import nltk

# Download VADER lexicon if not already present
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

from nltk.sentiment import SentimentIntensityAnalyzer

# Initialize VADER sentiment analyzer
vader = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    """
    Perform comprehensive sentiment analysis using multiple methods
    
    Args:
        text (str): Input text to analyze
    
    Returns:
        dict: Sentiment analysis results
    """
    # TextBlob sentiment analysis
    blob = TextBlob(text)
    textblob_polarity = blob.sentiment.polarity  # -1 to 1
    textblob_subjectivity = blob.sentiment.subjectivity  # 0 to 1
    
    # VADER sentiment analysis
    vader_scores = vader.polarity_scores(text)
    
    # Combine both methods for more accurate results
    # Use VADER as primary, TextBlob as secondary
    compound_score = vader_scores['compound']
    
    # Determine sentiment label
    if compound_score >= 0.05:
        label = 'Positive'
    elif compound_score <= -0.05:
        label = 'Negative'
    else:
        label = 'Neutral'
    
    # Calculate percentage distribution
    positive_pct = int(vader_scores['pos'] * 100)
    negative_pct = int(vader_scores['neg'] * 100)
    neutral_pct = int(vader_scores['neu'] * 100)
    
    # Ensure percentages sum to 100
    total = positive_pct + negative_pct + neutral_pct
    if total != 100 and total > 0:
        diff = 100 - total
        neutral_pct += diff
    
    result = {
        'score': round(compound_score, 3),
        'label': label,
        'positive': positive_pct,
        'negative': negative_pct,
        'neutral': neutral_pct,
        'textblob_polarity': round(textblob_polarity, 3),
        'textblob_subjectivity': round(textblob_subjectivity, 3),
        'vader_scores': {
            'positive': round(vader_scores['pos'], 3),
            'negative': round(vader_scores['neg'], 3),
            'neutral': round(vader_scores['neu'], 3),
            'compound': round(vader_scores['compound'], 3)
        },
        'confidence': calculate_confidence(vader_scores['compound']),
        'analysis_method': 'VADER + TextBlob'
    }
    
    return result

def calculate_confidence(compound_score):
    """
    Calculate confidence level based on compound score
    
    Args:
        compound_score (float): VADER compound score
    
    Returns:
        str: Confidence level
    """
    abs_score = abs(compound_score)
    
    if abs_score >= 0.7:
        return 'Very High'
    elif abs_score >= 0.5:
        return 'High'
    elif abs_score >= 0.2:
        return 'Medium'
    else:
        return 'Low'

def analyze_sentiment_by_sentence(text):
    """
    Analyze sentiment for each sentence
    
    Args:
        text (str): Input text
    
    Returns:
        list: List of sentiment results per sentence
    """
    blob = TextBlob(text)
    sentences = blob.sentences
    
    results = []
    for i, sentence in enumerate(sentences):
        sent_str = str(sentence)
        vader_score = vader.polarity_scores(sent_str)
        
        results.append({
            'sentence_number': i + 1,
            'sentence': sent_str,
            'compound_score': round(vader_score['compound'], 3),
            'sentiment': get_sentiment_label(vader_score['compound'])
        })
    
    return results

def get_sentiment_label(score):
    """Get sentiment label from score"""
    if score >= 0.05:
        return 'Positive'
    elif score <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'

if __name__ == "__main__":
    # Test sentiment analysis
    test_texts = [
        "I absolutely love this product! It's amazing and works perfectly.",
        "This is terrible. I'm very disappointed with the quality.",
        "The weather is okay today. Nothing special.",
        "Natural Language Processing is a fascinating field of study that combines linguistics and computer science."
    ]
    
    for text in test_texts:
        print(f"\nText: {text}")
        result = analyze_sentiment(text)
        print(f"Sentiment: {result['label']} (Score: {result['score']})")
        print(f"Distribution: Positive={result['positive']}%, Negative={result['negative']}%, Neutral={result['neutral']}%")
        print(f"Confidence: {result['confidence']}")
