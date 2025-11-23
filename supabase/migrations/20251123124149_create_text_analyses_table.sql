/*
  # Create text_analyses table for NarrativeNexus

  1. New Tables
    - `text_analyses`
      - `id` (uuid, primary key) - Unique identifier for each analysis
      - `user_id` (uuid, nullable) - User who performed the analysis (for future auth)
      - `filename` (text) - Original filename of uploaded document
      - `original_text` (text) - Raw uploaded text content
      - `cleaned_text` (text) - Preprocessed and cleaned text
      - `sentiment` (text) - Overall sentiment: Positive, Negative, or Neutral
      - `sentiment_score` (numeric) - Confidence score for sentiment (-1 to 1)
      - `keywords` (jsonb) - Extracted keywords with TF-IDF scores
      - `topics` (jsonb) - Detected topics with descriptions
      - `word_count` (integer) - Total word count
      - `created_at` (timestamptz) - Timestamp of analysis
      
  2. Security
    - Enable RLS on `text_analyses` table
    - Add policy for public read access (since auth is optional initially)
    - Add policy for public insert access
    
  3. Indexes
    - Index on created_at for efficient time-based queries
    - Index on sentiment for filtering by sentiment type
*/

CREATE TABLE IF NOT EXISTS text_analyses (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid,
  filename text NOT NULL,
  original_text text NOT NULL,
  cleaned_text text NOT NULL,
  sentiment text NOT NULL CHECK (sentiment IN ('Positive', 'Negative', 'Neutral')),
  sentiment_score numeric NOT NULL,
  keywords jsonb DEFAULT '[]'::jsonb,
  topics jsonb DEFAULT '[]'::jsonb,
  word_count integer DEFAULT 0,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE text_analyses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access to analyses"
  ON text_analyses FOR SELECT
  TO public
  USING (true);

CREATE POLICY "Allow public insert of analyses"
  ON text_analyses FOR INSERT
  TO public
  WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_text_analyses_created_at ON text_analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_text_analyses_sentiment ON text_analyses(sentiment);