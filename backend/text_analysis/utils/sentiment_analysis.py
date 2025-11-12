from textblob import TextBlob
from collections import Counter
import re

class SentimentAnalyzer:
    def __init__(self):
        self.sentiment_categories = {
            'positive': {'threshold': 0.1, 'count': 0},
            'neutral': {'threshold': (-0.1, 0.1), 'count': 0},
            'negative': {'threshold': -0.1, 'count': 0}
        }
    
    def analyze_sentiment(self, text):
        blob = TextBlob(text)
        return blob.sentiment.polarity
    
    def analyze_text_sentiment(self, text):
        # Split text into sentences for detailed analysis
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        sentiments = []
        sentiment_distribution = {'positive': 0, 'neutral': 0, 'negative': 0}
        
        for sentence in sentences:
            polarity = self.analyze_sentiment(sentence)
            sentiments.append(polarity)
            
            if polarity > 0.1:
                sentiment_distribution['positive'] += 1
            elif polarity < -0.1:
                sentiment_distribution['negative'] += 1
            else:
                sentiment_distribution['neutral'] += 1
        
        overall_polarity = sum(sentiments) / len(sentiments) if sentiments else 0
        
        return {
            'overall_sentiment': self._get_sentiment_label(overall_polarity),
            'overall_polarity': overall_polarity,
            'distribution': sentiment_distribution,
            'sentence_level': sentiments
        }
    
    def _get_sentiment_label(self, polarity):
        if polarity > 0.1:
            return 'positive'
        elif polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'