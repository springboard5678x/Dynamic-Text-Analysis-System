import { createClient } from 'npm:@supabase/supabase-js@2.57.4';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Client-Info, Apikey',
};

interface AnalysisRequest {
  text: string;
  filename: string;
}

interface KeywordScore {
  word: string;
  score: number;
}

interface Topic {
  topic: string;
  keywords: string[];
  description: string;
}

function cleanText(text: string): string {
  let cleaned = text.toLowerCase();
  cleaned = cleaned.replace(/[^a-z0-9\s]/g, ' ');
  cleaned = cleaned.replace(/\s+/g, ' ');
  return cleaned.trim();
}

function removeStopwords(words: string[]): string[] {
  const stopwords = new Set([
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
    'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
    'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
    'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just'
  ]);
  
  return words.filter(word => word.length > 2 && !stopwords.has(word));
}

function tokenize(text: string): string[] {
  return text.split(/\s+/).filter(word => word.length > 0);
}

function analyzeSentiment(text: string): { sentiment: string; score: number } {
  const positiveWords = new Set([
    'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
    'awesome', 'brilliant', 'outstanding', 'superb', 'love', 'loved',
    'happy', 'joy', 'beautiful', 'perfect', 'best', 'better', 'positive',
    'success', 'successful', 'winner', 'win', 'helpful', 'strong',
    'advantage', 'benefit', 'improve', 'improved', 'innovation', 'creative'
  ]);
  
  const negativeWords = new Set([
    'bad', 'terrible', 'awful', 'horrible', 'poor', 'worst', 'worse',
    'hate', 'hated', 'sad', 'angry', 'disappointed', 'failure', 'fail',
    'failed', 'problem', 'issue', 'wrong', 'negative', 'weak', 'loss',
    'lose', 'lost', 'difficult', 'hard', 'concern', 'risk', 'threat'
  ]);
  
  const words = tokenize(text.toLowerCase());
  let positiveCount = 0;
  let negativeCount = 0;
  
  words.forEach(word => {
    if (positiveWords.has(word)) positiveCount++;
    if (negativeWords.has(word)) negativeCount++;
  });
  
  const totalSentimentWords = positiveCount + negativeCount;
  
  if (totalSentimentWords === 0) {
    return { sentiment: 'Neutral', score: 0 };
  }
  
  const score = (positiveCount - negativeCount) / words.length;
  
  if (positiveCount > negativeCount * 1.2) {
    return { sentiment: 'Positive', score: Math.min(score * 10, 1) };
  } else if (negativeCount > positiveCount * 1.2) {
    return { sentiment: 'Negative', score: Math.max(score * 10, -1) };
  } else {
    return { sentiment: 'Neutral', score };
  }
}

function calculateTFIDF(words: string[]): KeywordScore[] {
  const wordFreq: Record<string, number> = {};
  
  words.forEach(word => {
    wordFreq[word] = (wordFreq[word] || 0) + 1;
  });
  
  const maxFreq = Math.max(...Object.values(wordFreq));
  
  const tfidf: KeywordScore[] = Object.entries(wordFreq)
    .map(([word, freq]) => ({
      word,
      score: (freq / maxFreq) * Math.log(words.length / freq)
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 10);
  
  return tfidf;
}

function detectTopics(words: string[], keywords: KeywordScore[]): Topic[] {
  const topKeywords = keywords.slice(0, 5).map(k => k.word);
  
  const businessWords = ['business', 'company', 'market', 'customer', 'product', 'sales', 'revenue', 'profit'];
  const techWords = ['technology', 'software', 'data', 'system', 'digital', 'innovation', 'platform', 'solution'];
  const healthWords = ['health', 'medical', 'patient', 'care', 'treatment', 'doctor', 'hospital', 'disease'];
  const educationWords = ['education', 'learning', 'student', 'teacher', 'school', 'training', 'knowledge', 'study'];
  
  const topics: Topic[] = [];
  
  const wordSet = new Set(words);
  
  const businessScore = businessWords.filter(w => wordSet.has(w)).length;
  const techScore = techWords.filter(w => wordSet.has(w)).length;
  const healthScore = healthWords.filter(w => wordSet.has(w)).length;
  const educationScore = educationWords.filter(w => wordSet.has(w)).length;
  
  if (businessScore >= 2) {
    topics.push({
      topic: 'Business & Commerce',
      keywords: topKeywords.filter(k => businessWords.includes(k)),
      description: 'Content related to business operations, markets, and commercial activities'
    });
  }
  
  if (techScore >= 2) {
    topics.push({
      topic: 'Technology & Innovation',
      keywords: topKeywords.filter(k => techWords.includes(k)),
      description: 'Discussion of technological solutions and digital transformation'
    });
  }
  
  if (healthScore >= 2) {
    topics.push({
      topic: 'Healthcare & Wellness',
      keywords: topKeywords.filter(k => healthWords.includes(k)),
      description: 'Medical and health-related information'
    });
  }
  
  if (educationScore >= 2) {
    topics.push({
      topic: 'Education & Learning',
      keywords: topKeywords.filter(k => educationWords.includes(k)),
      description: 'Educational content and learning materials'
    });
  }
  
  if (topics.length === 0) {
    topics.push({
      topic: 'General Content',
      keywords: topKeywords.slice(0, 3),
      description: `Primary themes include: ${topKeywords.slice(0, 3).join(', ')}`
    });
  }
  
  return topics;
}

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, {
      status: 200,
      headers: corsHeaders,
    });
  }

  try {
    const { text, filename }: AnalysisRequest = await req.json();

    if (!text || text.trim().length === 0) {
      return new Response(
        JSON.stringify({ error: 'Text content is required' }),
        {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        }
      );
    }

    const cleanedText = cleanText(text);
    const tokens = tokenize(cleanedText);
    const filteredWords = removeStopwords(tokens);
    
    const { sentiment, score: sentimentScore } = analyzeSentiment(text);
    const keywords = calculateTFIDF(filteredWords);
    const topics = detectTopics(filteredWords, keywords);
    const wordCount = tokenize(text).length;

    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    const { data, error } = await supabase
      .from('text_analyses')
      .insert({
        filename: filename || 'untitled.txt',
        original_text: text,
        cleaned_text: cleanedText,
        sentiment,
        sentiment_score: sentimentScore,
        keywords,
        topics,
        word_count: wordCount,
      })
      .select()
      .single();

    if (error) {
      throw error;
    }

    return new Response(
      JSON.stringify({
        id: data.id,
        sentiment,
        sentimentScore,
        keywords,
        topics,
        wordCount,
        cleanedText: cleanedText.substring(0, 500) + (cleanedText.length > 500 ? '...' : ''),
      }),
      {
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    );
  } catch (error) {
    console.error('Error analyzing text:', error);
    return new Response(
      JSON.stringify({ error: 'Failed to analyze text', details: error.message }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    );
  }
});