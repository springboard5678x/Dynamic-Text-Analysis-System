import Sentiment from 'sentiment';

const sentiment = new Sentiment();

// Configuration
const USE_PYTHON_BACKEND = true; // Set to false to use JavaScript implementation
const BACKEND_URL = 'http://localhost:5000';

// Stop words for filtering
const stopWords = new Set([
  'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with', 
  'to', 'for', 'of', 'as', 'by', 'that', 'this', 'it', 'from', 'are', 'was', 'be', 
  'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 
  'should', 'may', 'might', 'can', 'shall', 'must', 'ought', 'i', 'you', 'he', 
  'she', 'we', 'they', 'what', 'when', 'where', 'who', 'why', 'how', 'all', 'each',
  'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
  'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now'
]);

export interface AnalysisResult {
  originalText: string;
  cleanedText: string;
  sentiment: {
    score: number;
    label: string;
    positive: number;
    negative: number;
    neutral: number;
  };
  topics: Array<{ word: string; weight: number }>;
  summary: string;
  wordCount: number;
  sentenceCount: number;
  keywords: Array<{ text: string; value: number }>;
}

// Text preprocessing
export const preprocessText = (text: string): string => {
  // Remove special characters but keep basic punctuation
  let cleaned = text.replace(/[^\w\s.,!?-]/g, ' ');
  
  // Remove extra whitespace
  cleaned = cleaned.replace(/\s+/g, ' ').trim();
  
  // Convert to lowercase for analysis
  return cleaned.toLowerCase();
};

// Sentiment Analysis
export const analyzeSentiment = (text: string) => {
  const result = sentiment.analyze(text);
  
  const score = result.score;
  let label = 'Neutral';
  let positive = 0;
  let negative = 0;
  let neutral = 100;
  
  if (score > 0) {
    label = 'Positive';
    positive = Math.min(100, (score / text.split(' ').length) * 100 + 50);
    neutral = 100 - positive;
  } else if (score < 0) {
    label = 'Negative';
    negative = Math.min(100, (Math.abs(score) / text.split(' ').length) * 100 + 50);
    neutral = 100 - negative;
  }
  
  return {
    score,
    label,
    positive: Math.round(positive),
    negative: Math.round(negative),
    neutral: Math.round(neutral)
  };
};

// Simple TF-IDF implementation for browser
const calculateTFIDF = (text: string): { [key: string]: number } => {
  const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
  const words = text.toLowerCase().split(/\s+/);
  
  // Calculate term frequency (TF)
  const termFrequency: { [key: string]: number } = {};
  words.forEach(word => {
    if (word.length > 3 && !stopWords.has(word)) {
      termFrequency[word] = (termFrequency[word] || 0) + 1;
    }
  });
  
  // Calculate document frequency (DF)
  const documentFrequency: { [key: string]: number } = {};
  sentences.forEach(sentence => {
    const uniqueWords = new Set(sentence.toLowerCase().split(/\s+/));
    uniqueWords.forEach(word => {
      if (word.length > 3 && !stopWords.has(word)) {
        documentFrequency[word] = (documentFrequency[word] || 0) + 1;
      }
    });
  });
  
  // Calculate TF-IDF
  const tfidf: { [key: string]: number } = {};
  Object.keys(termFrequency).forEach(term => {
    const tf = termFrequency[term] / words.length;
    const idf = Math.log(sentences.length / (documentFrequency[term] || 1));
    tfidf[term] = tf * idf;
  });
  
  return tfidf;
};

// Topic Modeling using custom TF-IDF
export const extractTopics = (text: string): Array<{ word: string; weight: number }> => {
  const tfidfScores = calculateTFIDF(text);
  
  // Sort and get top 10 topics
  const topics = Object.entries(tfidfScores)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([word, weight]) => ({ word, weight: Math.round(weight * 1000) / 1000 }));
  
  return topics;
};

// Text Summarization (Extractive)
export const summarizeText = (text: string): string => {
  const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
  
  if (sentences.length <= 3) {
    return text;
  }
  
  // Score sentences based on keyword frequency
  const words = preprocessText(text).split(/\s+/);
  const wordFreq: { [key: string]: number } = {};
  
  words.forEach(word => {
    if (word.length > 4) {
      wordFreq[word] = (wordFreq[word] || 0) + 1;
    }
  });
  
  // Score each sentence
  const sentenceScores = sentences.map(sentence => {
    const sentenceWords = preprocessText(sentence).split(/\s+/);
    const score = sentenceWords.reduce((sum, word) => sum + (wordFreq[word] || 0), 0);
    return { sentence: sentence.trim(), score };
  });
  
  // Get top 3 sentences
  const topSentences = sentenceScores
    .sort((a, b) => b.score - a.score)
    .slice(0, Math.min(3, Math.ceil(sentences.length * 0.3)))
    .map(s => s.sentence);
  
  return topSentences.join('. ') + '.';
};

// Extract keywords for word cloud
export const extractKeywords = (text: string): Array<{ text: string; value: number }> => {
  const words = preprocessText(text).split(/\s+/);
  const wordFreq: { [key: string]: number } = {};
  
  words.forEach(word => {
    if (word.length > 3 && !stopWords.has(word)) {
      wordFreq[word] = (wordFreq[word] || 0) + 1;
    }
  });
  
  return Object.entries(wordFreq)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 30)
    .map(([text, value]) => ({ text, value }));
};

// Main analysis function
export const analyzeText = async (text: string): Promise<AnalysisResult> => {
  // Try Python backend first if enabled
  if (USE_PYTHON_BACKEND) {
    try {
      const response = await fetch(`${BACKEND_URL}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Using Python Backend - Better ML algorithms!');
        return data;
      } else {
        console.warn('⚠️ Python backend not available, falling back to JavaScript');
      }
    } catch (error) {
      console.warn('⚠️ Python backend error, falling back to JavaScript:', error);
    }
  }

  // Fallback to JavaScript implementation
  console.log('📊 Using JavaScript implementation');
  const cleanedText = preprocessText(text);
  const sentimentResult = analyzeSentiment(text);
  const topics = extractTopics(cleanedText);
  const summary = summarizeText(text);
  const keywords = extractKeywords(cleanedText);
  
  const words = text.split(/\s+/);
  const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
  
  return {
    originalText: text,
    cleanedText,
    sentiment: sentimentResult,
    topics,
    summary,
    wordCount: words.length,
    sentenceCount: sentences.length,
    keywords
  };
};
