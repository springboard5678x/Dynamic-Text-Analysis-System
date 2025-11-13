/// <reference types="react-scripts" />
/// <reference types="react" />
/// <reference types="react-dom" />

declare module 'sentiment' {
  interface SentimentResult {
    score: number;
    comparative: number;
    tokens: string[];
    words: string[];
    positive: string[];
    negative: string[];
  }

  class Sentiment {
    analyze(text: string): SentimentResult;
  }

  export = Sentiment;
}

declare module 'natural' {
  export class TfIdf {
    addDocument(document: string): void;
    listTerms(documentIndex: number): Array<{ term: string; tfidf: number }>;
  }
}
