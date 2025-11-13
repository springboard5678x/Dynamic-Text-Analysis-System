from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add models directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'models'))

from models.sentiment import analyze_sentiment
from models.topic_model import extract_topics
from models.summarizer import summarize_text
from models.keywords import extract_keywords
from models.preprocessing import preprocess_text

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'NarrativeNexus API is running'
    })

@app.route('/analyze', methods=['POST'])
def analyze_text():
    """
    Main text analysis endpoint
    Accepts text and returns comprehensive analysis
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        
        if not text.strip():
            return jsonify({'error': 'Empty text provided'}), 400
        
        # Preprocess text
        cleaned_text = preprocess_text(text)
        
        # Run all analyses
        sentiment_result = analyze_sentiment(text)
        topics = extract_topics(cleaned_text)
        summary = summarize_text(text)
        keywords = extract_keywords(cleaned_text)
        
        # Calculate basic statistics
        words = text.split()
        sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
        
        result = {
            'originalText': text,
            'cleanedText': cleaned_text,
            'sentiment': sentiment_result,
            'topics': topics,
            'summary': summary,
            'keywords': keywords,
            'wordCount': len(words),
            'sentenceCount': len(sentences),
            'status': 'success'
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'failed'
        }), 500

@app.route('/sentiment', methods=['POST'])
def sentiment_only():
    """Endpoint for sentiment analysis only"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text.strip():
            return jsonify({'error': 'Empty text'}), 400
        
        result = analyze_sentiment(text)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/topics', methods=['POST'])
def topics_only():
    """Endpoint for topic modeling only"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text.strip():
            return jsonify({'error': 'Empty text'}), 400
        
        cleaned_text = preprocess_text(text)
        topics = extract_topics(cleaned_text)
        return jsonify({'topics': topics})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/summarize', methods=['POST'])
def summarize_only():
    """Endpoint for text summarization only"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text.strip():
            return jsonify({'error': 'Empty text'}), 400
        
        summary = summarize_text(text)
        return jsonify({'summary': summary})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting NarrativeNexus Backend Server...")
    print("📊 AI/ML/NLP Models loaded successfully")
    print("🌐 Server running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
