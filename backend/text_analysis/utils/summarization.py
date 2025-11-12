from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import nltk
import torch
import logging
import re

logger = logging.getLogger(__name__)

nltk.download('punkt')

class TextSummarizer:
    def __init__(self):
        try:
            self.model_name = "facebook/bart-large-cnn"
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self.abstractive_summarizer = pipeline(
                "summarization", 
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("Abstractive summarizer loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load abstractive summarizer: {e}")
            self.abstractive_summarizer = None
    
    def extractive_summary(self, text, sentences_count=5):
        try:
            if len(text.strip()) < 100:
                return "Text too short for meaningful extractive summary."
                
            # Clean text first
            text = self._clean_text(text)
            
            # Use TextRank for better results with various text lengths
            parser = PlaintextParser.from_string(text, Tokenizer("english"))
            summarizer = TextRankSummarizer()
            
            # Adjust sentence count based on text length
            word_count = len(text.split())
            if word_count < 500:
                sentences_count = min(3, sentences_count)
            elif word_count > 2000:
                sentences_count = min(8, sentences_count)
            
            summary = summarizer(parser.document, sentences_count)
            result = ' '.join(str(sentence) for sentence in summary)
            
            if not result.strip():
                return self.simple_extractive_fallback(text, sentences_count)
                
            return result
            
        except Exception as e:
            logger.error(f"Extractive summarization failed: {e}")
            # Fallback to simple extractive method
            return self.simple_extractive_fallback(text, sentences_count)
    
    def abstractive_summary(self, text, max_length=150, min_length=50):
        if self.abstractive_summarizer is None:
            logger.warning("Abstractive summarizer not available")
            return "Abstractive summarization service is currently unavailable."
            
        try:
            # Clean and preprocess text
            text = self._clean_text(text)
            word_count = len(text.split())
            
            logger.info(f"Abstractive summary requested: {word_count} words")
            
            if len(text.strip()) < 50:
                logger.warning("Text too short for abstractive summarization")
                return "Text too short for abstractive summarization."
            
            # Calculate optimal length based on input text
            if word_count < 200:
                max_length = 80
                min_length = 30
            elif word_count > 2000:
                max_length = 200
                min_length = 80
            
            # For short to medium texts, try direct summarization first
            if word_count <= 800:
                logger.info(f"Attempting direct abstractive summarization for {word_count} words")
                try:
                    summary = self.abstractive_summarizer(
                        text,
                        max_length=max_length,
                        min_length=min_length,
                        do_sample=False,
                        truncation=True
                    )
                    result = summary[0]['summary_text'].strip()
                    if result and len(result.split()) > 5:
                        logger.info(f"Direct abstractive summary successful: {len(result.split())} words")
                        return result
                    else:
                        logger.warning("Direct abstractive summary produced empty result, falling back to chunking")
                except Exception as e:
                    logger.warning(f"Direct abstractive summarization failed, falling back to chunking: {e}")
            
            # Use chunked approach for longer texts or when direct method fails
            logger.info(f"Using chunked summarization for {word_count} words")
            result = self._safe_chunked_abstractive_summary(text, max_length, min_length)
            
            logger.info(f"Abstractive summary result: {len(result.split())} words")
            return result
            
        except Exception as e:
            logger.error(f"Abstractive summarization failed: {e}")
            # Return a clear message instead of falling back to extractive
            return "Unable to generate abstractive summary. Please try with different text."
    
    def _safe_chunked_abstractive_summary(self, text, max_length=150, min_length=50):
        """Safe chunked summarization with multiple fallbacks"""
        try:
            logger.info("Attempting sentence-based chunking...")
            result = self._sentence_based_chunking(text, max_length, min_length)
            if result and len(result.split()) > 10 and not result.startswith("Unable"):
                logger.info("Sentence-based chunking successful")
                return result
            
            logger.info("Attempting paragraph-based chunking...")
            result = self._paragraph_based_chunking(text, max_length, min_length)
            if result and len(result.split()) > 10 and not result.startswith("Unable"):
                logger.info("Paragraph-based chunking successful")
                return result
            
            logger.info("Attempting hybrid summarization...")
            result = self._hybrid_summarization(text, max_length, min_length)
            if result and len(result.split()) > 10:
                logger.info("Hybrid summarization successful")
                return result
            
            logger.error("All abstractive methods failed")
            return "Unable to generate abstractive summary with available methods."
            
        except Exception as e:
            logger.error(f"All chunking methods failed: {e}")
            return "Unable to generate summary due to text complexity or length limitations."
    
    def _sentence_based_chunking(self, text, max_length=150, min_length=50):
        """Chunk by sentences for better coherence"""
        try:
            # Split into sentences
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 10]  # Reduced threshold
            
            if not sentences:
                logger.warning("No meaningful sentences found for chunking")
                return None
            
            logger.info(f"Processing {len(sentences)} sentences for chunking")
            
            # Create chunks of 2-4 sentences each (more conservative)
            chunks = []
            current_chunk = []
            current_word_count = 0
            
            for sentence in sentences:
                sentence_words = len(sentence.split())
                
                if current_word_count + sentence_words > 300 and current_chunk:  # Reduced chunk size
                    chunks.append(' '.join(current_chunk))
                    current_chunk = [sentence]
                    current_word_count = sentence_words
                else:
                    current_chunk.append(sentence)
                    current_word_count += sentence_words
            
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            
            # Limit number of chunks to process
            chunks = chunks[:6]  # Reduced from 8 to 6
            
            logger.info(f"Created {len(chunks)} chunks for processing")
            
            # Summarize each chunk
            chunk_summaries = []
            for i, chunk in enumerate(chunks):
                try:
                    if len(chunk.split()) > 20:  # Reduced threshold
                        logger.info(f"Summarizing chunk {i+1}/{len(chunks)} ({len(chunk.split())} words)")
                        chunk_summary = self.abstractive_summarizer(
                            chunk,
                            max_length=min(80, max_length),  # Reduced max length
                            min_length=min(20, min_length),  # Reduced min length
                            do_sample=False,
                            truncation=True
                        )
                        if chunk_summary and chunk_summary[0]['summary_text'].strip():
                            summary_text = chunk_summary[0]['summary_text'].strip()
                            chunk_summaries.append(summary_text)
                            logger.info(f"Successfully summarized chunk {i+1}: {len(summary_text.split())} words")
                        else:
                            logger.warning(f"Chunk {i+1} produced empty summary")
                except Exception as e:
                    logger.warning(f"Failed to summarize chunk {i+1}: {e}")
                    continue
            
            if not chunk_summaries:
                logger.warning("No chunks were successfully summarized")
                return None
            
            # Combine chunk summaries
            combined_text = ' '.join(chunk_summaries)
            logger.info(f"Combined chunk summaries: {len(combined_text.split())} words")
            
            # If combined text is reasonable, return as is
            if len(combined_text.split()) <= 250:
                return combined_text
            
            # Final summarization pass for very long combined text
            try:
                logger.info("Performing final summarization pass")
                final_summary = self.abstractive_summarizer(
                    combined_text,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False,
                    truncation=True
                )
                result = final_summary[0]['summary_text'] if final_summary else combined_text
                logger.info(f"Final summary: {len(result.split())} words")
                return result
            except Exception as e:
                logger.warning(f"Final summarization pass failed, returning combined text: {e}")
                return combined_text
                
        except Exception as e:
            logger.error(f"Sentence-based chunking failed: {e}")
            return None
    
    def _paragraph_based_chunking(self, text, max_length=150, min_length=50):
        """Chunk by paragraphs for structured documents"""
        try:
            # Split by paragraphs
            paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 30]  # Reduced threshold
            
            if not paragraphs:
                return None
            
            logger.info(f"Processing {len(paragraphs)} paragraphs for chunking")
            
            # Process substantial paragraphs only
            chunk_summaries = []
            for i, paragraph in enumerate(paragraphs[:4]):  # Reduced from 6 to 4
                try:
                    if len(paragraph.split()) > 30:  # Reduced threshold
                        logger.info(f"Summarizing paragraph {i+1}/{len(paragraphs[:4])}")
                        chunk_summary = self.abstractive_summarizer(
                            paragraph,
                            max_length=min(100, max_length),  # Reduced max length
                            min_length=min(30, min_length),   # Reduced min length
                            do_sample=False,
                            truncation=True
                        )
                        if chunk_summary and chunk_summary[0]['summary_text'].strip():
                            summary_text = chunk_summary[0]['summary_text'].strip()
                            chunk_summaries.append(summary_text)
                            logger.info(f"Successfully summarized paragraph {i+1}: {len(summary_text.split())} words")
                except Exception as e:
                    logger.warning(f"Failed to summarize paragraph {i+1}: {e}")
                    continue
            
            if not chunk_summaries:
                return None
            
            result = ' '.join(chunk_summaries)
            logger.info(f"Paragraph-based summary: {len(result.split())} words")
            return result
            
        except Exception as e:
            logger.error(f"Paragraph-based chunking failed: {e}")
            return None
    
    def _hybrid_summarization(self, text, max_length=150, min_length=50):
        """Combine extractive and abstractive methods - FIXED to avoid returning extractive directly"""
        try:
            # First get extractive summary to reduce length
            logger.info("Starting hybrid summarization: getting extractive summary")
            extractive = self.extractive_summary(text, sentences_count=6)  # Reduced sentence count
            
            if not extractive or "unable" in extractive.lower() or extractive == text:
                logger.warning("Extractive summary failed or is same as original text")
                return "Unable to generate hybrid summary."
            
            # Ensure extractive is different from original and substantial
            if len(extractive.split()) < 10 or extractive == text:
                logger.warning("Extractive summary too short or identical to original")
                return "Unable to generate meaningful hybrid summary."
            
            logger.info(f"Extractive summary obtained: {len(extractive.split())} words")
            
            # Apply abstractive summarization to the extractive result
            try:
                logger.info("Applying abstractive summarization to extractive result")
                summary = self.abstractive_summarizer(
                    extractive,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False,
                    truncation=True
                )
                if summary and summary[0]['summary_text'].strip():
                    result = summary[0]['summary_text'].strip()
                    logger.info(f"Hybrid summarization successful: {len(result.split())} words")
                    
                    # Ensure the result is different from the extractive input
                    if result != extractive and len(result.split()) > 5:
                        return result
                    else:
                        logger.warning("Hybrid result same as extractive input")
                        return "Generated summary was not sufficiently different from extractive summary."
                else:
                    logger.warning("Abstractive step in hybrid summarization produced empty result")
                    return "Unable to generate meaningful abstractive summary from extractive content."
            except Exception as e:
                logger.error(f"Abstractive step in hybrid summarization failed: {e}")
                return "Abstractive processing failed in hybrid approach."
                    
        except Exception as e:
            logger.error(f"Hybrid summarization failed: {e}")
            return "Hybrid summarization unavailable."
    
    def _clean_text(self, text):
        """Clean text for better processing"""
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove very short lines or fragments
        lines = text.split('\n')
        cleaned_lines = [line.strip() for line in lines if len(line.strip()) > 10]
        
        # Remove common problematic patterns
        text = ' '.join(cleaned_lines)
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = re.sub(r'\[.*?\]', '', text)  # Remove brackets content
        text = re.sub(r'\(.*?\)', '', text)  # Remove parentheses content
        
        return text.strip()
    
    def simple_extractive_fallback(self, text, sentences_count=3):
        """Simple fallback summarization using sentence scoring"""
        try:
            # Split into meaningful sentences
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 15]  # Reduced threshold
            
            if len(sentences) <= sentences_count:
                return text
            
            # Score sentences by length and keyword density
            scored_sentences = []
            for i, sentence in enumerate(sentences):
                if len(sentence.strip()) > 15:  # Reduced threshold
                    # Score based on length and position
                    word_count = len(sentence.split())
                    position_score = 1 - (i / len(sentences))  # Favor earlier sentences
                    length_score = min(1.0, word_count / 40)  # Adjusted normalization
                    score = (length_score * 0.6) + (position_score * 0.4)
                    scored_sentences.append((score, sentence.strip()))
            
            if not scored_sentences:
                return text
            
            # Sort by score and take top sentences
            scored_sentences.sort(reverse=True, key=lambda x: x[0])
            top_sentences = [s[1] for s in scored_sentences[:sentences_count]]
            
            result = '. '.join(top_sentences) + '.'
            return result if len(result.split()) > 5 else text  # Reduced threshold
            
        except Exception as e:
            logger.error(f"Simple extractive fallback failed: {e}")
            # Last resort: return first few sentences
            sentences = text.split('. ')
            return '. '.join(sentences[:min(2, len(sentences))]) + '.'  # Reduced count