export interface KeywordScore {
  word: string;
  score: number;
}

export interface Topic {
  topic: string;
  keywords: string[];
  description: string;
}

export interface AnalysisResult {
  id: string;
  sentiment: 'Positive' | 'Negative' | 'Neutral';
  sentimentScore: number;
  keywords: KeywordScore[];
  topics: Topic[];
  wordCount: number;
  cleanedText: string;
}
