from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging
import re
from collections import Counter

logger = logging.getLogger(__name__)

class TopicModeler:
    def __init__(self, n_topics='auto', method='lda', max_features=1000):
        self.n_topics = n_topics
        self.method = method
        self.max_features = max_features
        self.vectorizer = None
        self.model = None
        self.feature_names = None
        
    def calculate_optimal_topics(self, documents):
        """Calculate optimal number of topics"""
        if isinstance(documents, str):
            documents = [documents]
        
        # Combine all documents for analysis
        combined_text = ' '.join(documents) if len(documents) > 1 else documents[0]
        
        # Calculate text statistics
        word_count = len(combined_text.split())
        sentence_count = len(re.split(r'[.!?]+', combined_text))
        unique_words = len(set(combined_text.lower().split()))
        
        logger.info(f"Text stats - Words: {word_count}, Sentences: {sentence_count}, Unique words: {unique_words}")
        
        # Generate topics based on text length
        if word_count < 200:
            return max(2, min(3, word_count // 50))
        elif word_count < 800:
            base_topics = 4
            additional_topics = max(0, (word_count - 200) // 150)
            return min(6, base_topics + additional_topics)
        elif word_count < 2000:
            base_topics = 5
            additional_topics = max(0, (word_count - 800) // 200)
            return min(8, base_topics + additional_topics)
        else:
            base_topics = 7
            additional_topics = max(0, (word_count - 2000) // 400)
            return min(12, base_topics + additional_topics)
    
    def prepare_documents(self, documents):
        """Prepare documents for topic modeling"""
        if isinstance(documents, str):
            documents = [documents]
        
        # Ensure we have enough documents
        if len(documents) < 1:
            raise ValueError("No documents provided for topic modeling")
            
        return documents
    
    def create_vectorizer(self, documents):
        """Create and configure vectorizer with improved settings"""
        # Calculate document statistics
        doc_lengths = [len(doc.split()) for doc in documents]
        total_words = sum(doc_lengths)
        num_docs = len(documents)
        
        # Dynamic configuration based on document characteristics
        if num_docs == 1:
            # Single document - use more lenient parameters
            max_df = 0.99
            min_df = 1
            max_features = min(1000, total_words // 2)
        elif num_docs < 5:
            # Few documents
            max_df = 0.95
            min_df = 1
            max_features = min(800, total_words // 3)
        else:
            # Multiple documents
            max_df = 0.90
            min_df = 2 if num_docs > 10 else 1
            max_features = min(2000, total_words // 4)
        
        # Ensure reasonable bounds
        max_features = max(50, min(max_features, self.max_features))
        
        logger.info(f"Vectorizer config - docs: {num_docs}, max_df: {max_df}, min_df: {min_df}, max_features: {max_features}")
        
        self.vectorizer = CountVectorizer(
            max_df=max_df, 
            min_df=min_df, 
            max_features=max_features,
            stop_words='english',
            lowercase=True,
            analyzer='word',
            ngram_range=(1, 2)  # Use bigrams more conservatively
        )
        
        return self.vectorizer
    
    def fit(self, documents):
        """Fit topic model to documents"""
        try:
            documents = self.prepare_documents(documents)
            logger.info(f"Processing {len(documents)} documents for topic modeling")
            
            # Calculate optimal topics if auto mode
            if self.n_topics == 'auto':
                optimal_topics = self.calculate_optimal_topics(documents)
                logger.info(f"Auto-calculated optimal topics: {optimal_topics}")
            else:
                optimal_topics = self.n_topics
            
            # Create appropriate vectorizer
            self.create_vectorizer(documents)
            
            # Vectorize documents
            logger.info("Vectorizing documents...")
            dtm = self.vectorizer.fit_transform(documents)
            self.feature_names = self.vectorizer.get_feature_names_out()
            
            logger.info(f"Vocabulary size: {len(self.feature_names)}")
            logger.info(f"Document-term matrix shape: {dtm.shape}")
            
            # Calculate maximum possible topics
            max_possible_topics = min(optimal_topics, dtm.shape[0] * 2, dtm.shape[1] // 3)
            if max_possible_topics < 1:
                max_possible_topics = 1
                
            if max_possible_topics < optimal_topics:
                logger.warning(f"Reduced topics from {optimal_topics} to {max_possible_topics} due to data constraints")
            
            # Adjust topics based on vocabulary size
            if len(self.feature_names) < 30:
                max_possible_topics = min(3, max_possible_topics)
            elif len(self.feature_names) < 70:
                max_possible_topics = min(5, max_possible_topics)
            
            # Ensure minimum of 2 topics for any non-trivial text
            if len(documents) > 0 and dtm.shape[1] > 10:
                max_possible_topics = max(2, max_possible_topics)
            
            logger.info(f"Final topic count: {max_possible_topics}")
            
            # Train model
            if self.method.lower() == 'lda':
                self.model = LatentDirichletAllocation(
                    n_components=max_possible_topics,
                    random_state=42,
                    max_iter=50,
                    learning_method='online',
                    batch_size=128,
                    evaluate_every=5
                )
                logger.info("Training LDA model...")
            else:  # nmf
                self.model = NMF(
                    n_components=max_possible_topics,
                    random_state=42,
                    max_iter=500,
                    alpha_W=0.05,
                    alpha_H=0.05,
                    l1_ratio=0.3
                )
                logger.info("Training NMF model...")
            
            # Fit the model
            self.model.fit(dtm)
            logger.info("Topic modeling completed successfully")
            
            # Calculate model quality metrics
            coherence = self.calculate_coherence(documents)
            logger.info(f"Model coherence: {coherence:.4f}")
            
            return self.get_topics()
            
        except Exception as e:
            logger.error(f"Error in topic modeling: {str(e)}")
            # Fallback to basic topics
            return self.get_fallback_topics(documents)
    
    def calculate_coherence(self, documents, top_n=10):
        """Calculate topic coherence using cosine similarity"""
        try:
            if self.model is None or self.vectorizer is None:
                return 0.0
                
            dtm = self.vectorizer.transform(documents)
            coherence_scores = []
            
            for topic_idx, topic in enumerate(self.model.components_):
                # Get top words for this topic
                top_words_idx = topic.argsort()[-top_n:][::-1]
                top_words = [self.feature_names[i] for i in top_words_idx]
                
                # Calculate word vectors for top words
                word_vectors = []
                valid_words = []
                
                for word in top_words:
                    if word in self.vectorizer.vocabulary_:
                        word_idx = self.vectorizer.vocabulary_[word]
                        word_vector = dtm[:, word_idx].toarray().flatten()
                        word_vectors.append(word_vector)
                        valid_words.append(word)
                
                # Calculate coherence if we have at least 2 valid words
                if len(word_vectors) >= 2:
                    # Create similarity matrix
                    similarity_matrix = cosine_similarity(word_vectors)
                    np.fill_diagonal(similarity_matrix, 0)  # Remove self-similarity
                    
                    # Calculate average similarity
                    n_pairs = len(word_vectors) * (len(word_vectors) - 1)
                    if n_pairs > 0:
                        coherence = np.sum(similarity_matrix) / n_pairs
                        coherence_scores.append(coherence)
                else:
                    coherence_scores.append(0.0)
            
            return np.mean(coherence_scores) if coherence_scores else 0.0
            
        except Exception as e:
            logger.warning(f"Could not calculate coherence: {str(e)}")
            return 0.0
    
    def get_topics(self, n_words=10):
        """Extract topics with their top words"""
        if self.model is None or self.feature_names is None:
            raise ValueError("Model not trained. Call fit() first.")
        
        topics = []
        for topic_idx, topic in enumerate(self.model.components_):
            # Get top words for this topic
            top_words_idx = topic.argsort()[-n_words:][::-1]
            top_words = [self.feature_names[i] for i in top_words_idx]
            top_weights = [float(topic[i]) for i in top_words_idx]
            
            # Calculate topic strength (sum of top word weights)
            topic_strength = float(np.sum(topic[top_words_idx]))
            
            # Create human-readable label
            topic_label = f"Topic {topic_idx + 1}: {', '.join(top_words[:3])}"
            
            topics.append({
                'topic_id': topic_idx + 1,
                'words': top_words,
                'weights': top_weights,
                'strength': topic_strength,
                'label': topic_label,
                'dominant_words': top_words[:5]
            })
        
        # Sort topics by strength (most prominent first)
        topics.sort(key=lambda x: x['strength'], reverse=True)
        
        # Reassign topic IDs after sorting
        for new_idx, topic in enumerate(topics):
            topic['topic_id'] = new_idx + 1
            topic['label'] = f"Topic {new_idx + 1}: {', '.join(topic['words'][:3])}"
        
        logger.info(f"Generated {len(topics)} topics sorted by strength")
        return topics
    
    def get_fallback_topics(self, documents, n_words=8):
        """Generate fallback topics using word frequency"""
        logger.info("Generating fallback topics using word frequency")
        
        try:
            # Use enhanced word frequency analysis
            from collections import Counter
            import re
            
            # Combine all documents
            combined_text = ' '.join(documents) if isinstance(documents, list) else documents
            
            # Enhanced text cleaning
            words = re.findall(r'\b[a-zA-Z]{3,20}\b', combined_text.lower())
            
            # Remove stopwords
            stop_words = set([
                'the', 'and', 'for', 'with', 'this', 'that', 'are', 'was', 'were', 
                'have', 'has', 'had', 'been', 'will', 'would', 'could', 'should',
                'about', 'from', 'their', 'there', 'which', 'were', 'what', 'when',
                'where', 'how', 'why', 'who', 'whom', 'whose', 'into', 'through'
            ])
            filtered_words = [word for word in words if word not in stop_words]
            
            # Get most common words with frequencies
            word_freq = Counter(filtered_words)
            total_words = len(filtered_words)
            
            # Calculate number of topics
            if total_words < 100:
                n_topics = max(2, min(4, total_words // 25))
            elif total_words < 500:
                n_topics = max(3, min(6, total_words // 80))
            else:
                n_topics = max(4, min(8, total_words // 150))
            
            # Get meaningful words (appear at least twice and not too frequent)
            meaningful_words = [
                word for word, count in word_freq.most_common(100)
                if count >= 2 and count / total_words < 0.15
            ]
            
            # Create topics by grouping related words
            topics = []
            if meaningful_words:
                words_per_topic = max(4, len(meaningful_words) // n_topics)
                
                for i in range(n_topics):
                    start_idx = i * words_per_topic
                    end_idx = start_idx + words_per_topic
                    topic_words = meaningful_words[start_idx:end_idx]
                    
                    if topic_words:
                        # Calculate topic strength based on word frequencies
                        topic_strength = sum(word_freq[word] for word in topic_words) / total_words
                        
                        topics.append({
                            'topic_id': i + 1,
                            'words': topic_words,
                            'weights': [1.0 - (j * 0.1) for j in range(len(topic_words))],
                            'strength': topic_strength,
                            'label': f"Topic {i + 1}: {', '.join(topic_words[:3])}",
                            'dominant_words': topic_words[:3],
                            'is_fallback': True
                        })
            
            # If no meaningful topics found, provide more diverse defaults
            if not topics:
                # Create multiple default topics
                default_topic_sets = [
                    ['product', 'quality', 'service', 'experience', 'value'],
                    ['customer', 'support', 'help', 'response', 'friendly'],
                    ['price', 'cost', 'affordable', 'worth', 'money'],
                    ['features', 'design', 'easy', 'use', 'interface']
                ]
                
                for i, topic_words in enumerate(default_topic_sets):
                    topics.append({
                        'topic_id': i + 1,
                        'words': topic_words,
                        'weights': [1.0, 0.8, 0.6, 0.4, 0.2],
                        'strength': 1.0 - (i * 0.1),
                        'label': f"Topic {i + 1}: {', '.join(topic_words[:3])}",
                        'dominant_words': topic_words[:3],
                        'is_fallback': True
                    })
            
            logger.info(f"Generated {len(topics)} fallback topics")
            return topics
            
        except Exception as e:
            logger.error(f"Error generating fallback topics: {str(e)}")
            # Ultimate fallback with multiple topics
            return [
                {
                    'topic_id': 1,
                    'words': ['product', 'quality', 'service', 'good', 'excellent'],
                    'weights': [1.0, 0.8, 0.6, 0.4, 0.2],
                    'strength': 1.0,
                    'label': "Topic 1: product quality service",
                    'dominant_words': ['product', 'quality', 'service'],
                    'is_fallback': True
                },
                {
                    'topic_id': 2,
                    'words': ['customer', 'support', 'experience', 'help', 'friendly'],
                    'weights': [1.0, 0.8, 0.6, 0.4, 0.2],
                    'strength': 0.8,
                    'label': "Topic 2: customer support experience",
                    'dominant_words': ['customer', 'support', 'experience'],
                    'is_fallback': True
                }
            ]
    
    def transform(self, documents):
        """Transform new documents to topic distributions"""
        if self.model is None:
            raise ValueError("Model not trained. Call fit() first.")
        
        documents = self.prepare_documents(documents)
        dtm = self.vectorizer.transform(documents)
        topic_distributions = self.model.transform(dtm)
        
        return topic_distributions
    
    def get_document_topics(self, documents):
        """Get topic distributions for documents"""
        try:
            topic_distributions = self.transform(documents)
            
            results = []
            for doc_idx, distribution in enumerate(topic_distributions):
                top_topic_idx = np.argmax(distribution)
                top_topic_strength = distribution[top_topic_idx]
                
                # Get top 3 topics for this document
                top_topics_idx = distribution.argsort()[-3:][::-1]
                top_topics = []
                
                for idx in top_topics_idx:
                    top_topics.append({
                        'topic_id': idx + 1,
                        'strength': float(distribution[idx])
                    })
                
                results.append({
                    'document_index': doc_idx,
                    'topic_distribution': distribution.tolist(),
                    'dominant_topic': top_topic_idx + 1,
                    'dominant_topic_strength': float(top_topic_strength),
                    'top_topics': top_topics
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting document topics: {e}")
            return []


class AdvancedTopicModeler:
    """Enhanced topic modeler with multiple methods and evaluation"""
    
    def __init__(self):
        self.models = {}
        self.vectorizers = {}
        self.results = {}
        
    def create_lda_model(self, n_topics=5, **kwargs):
        """Create LDA model with given parameters"""
        model = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            max_iter=20,
            learning_method='online',
            **kwargs
        )
        return model
    
    def create_nmf_model(self, n_topics=5, **kwargs):
        """Create NMF model with given parameters"""
        model = NMF(
            n_components=n_topics,
            random_state=42,
            max_iter=300,
            **kwargs
        )
        return model
    
    def evaluate_coherence(self, model, vectorizer, documents, top_n=10):
        """Calculate topic coherence (simplified version)"""
        try:
            dtm = vectorizer.transform(documents)
            feature_names = vectorizer.get_feature_names_out()
            
            coherence_scores = []
            for topic_idx, topic in enumerate(model.components_):
                top_words_idx = topic.argsort()[-top_n:][::-1]
                top_words = [feature_names[i] for i in top_words_idx]
                
                # Simple coherence: average pairwise similarity of top words
                word_vectors = []
                for word in top_words:
                    word_idx = vectorizer.vocabulary_.get(word)
                    if word_idx is not None:
                        word_vectors.append(dtm[:, word_idx].toarray().flatten())
                
                if len(word_vectors) > 1:
                    similarity_matrix = cosine_similarity(word_vectors)
                    np.fill_diagonal(similarity_matrix, 0)
                    coherence = np.mean(similarity_matrix)
                    coherence_scores.append(coherence)
                else:
                    coherence_scores.append(0.0)
            
            return np.mean(coherence_scores) if coherence_scores else 0.0
            
        except Exception as e:
            logger.warning(f"Could not calculate coherence: {str(e)}")
            return 0.0
    
    def compare_models(self, documents, methods=['lda', 'nmf'], topic_range=range(2, 8)):
        """Compare different models and topic numbers"""
        results = {}
        
        for method in methods:
            results[method] = {}
            for n_topics in topic_range:
                try:
                    # Create vectorizer
                    vectorizer = CountVectorizer(
                        max_df=0.95, 
                        min_df=1, 
                        max_features=1000,
                        stop_words='english'
                    )
                    
                    dtm = vectorizer.fit_transform(documents)
                    
                    # Skip if not enough features
                    if dtm.shape[1] < n_topics:
                        continue
                    
                    # Create and fit model
                    if method == 'lda':
                        model = self.create_lda_model(n_topics=n_topics)
                    else:
                        model = self.create_nmf_model(n_topics=n_topics)
                    
                    model.fit(dtm)
                    
                    # Calculate metrics
                    coherence = self.evaluate_coherence(model, vectorizer, documents)
                    
                    results[method][n_topics] = {
                        'coherence': coherence,
                        'model': model,
                        'vectorizer': vectorizer
                    }
                    
                except Exception as e:
                    logger.warning(f"Failed to train {method} with {n_topics} topics: {str(e)}")
                    continue
        
        return results


def find_optimal_topics(documents, max_topics=10, method='lda'):
    """Find optimal number of topics using simple metrics"""
    try:
        vectorizer = CountVectorizer(max_df=0.95, min_df=1, max_features=1000, stop_words='english')
        
        if isinstance(documents, str):
            documents = [documents]
        
        dtm = vectorizer.fit_transform(documents)
        
        # Check if we have enough features
        if dtm.shape[1] < 2:
            return 1
        
        best_score = -1
        best_n_topics = min(3, dtm.shape[1] - 1)
        
        for n_topics in range(2, min(max_topics + 1, dtm.shape[1])):
            try:
                if method == 'lda':
                    model = LatentDirichletAllocation(
                        n_components=n_topics, 
                        random_state=42,
                        max_iter=10
                    )
                else:
                    model = NMF(
                        n_components=n_topics, 
                        random_state=42,
                        max_iter=200
                    )
                
                topic_distributions = model.fit_transform(dtm)
                
                # Use silhouette score if we have multiple documents
                if topic_distributions.shape[0] > 1:
                    dominant_topics = np.argmax(topic_distributions, axis=1)
                    if len(np.unique(dominant_topics)) > 1:
                        score = silhouette_score(topic_distributions, dominant_topics)
                    else:
                        score = 0
                else:
                    score = 0.5  # Single document case
                    
                if score > best_score:
                    best_score = score
                    best_n_topics = n_topics
                    
            except Exception as e:
                logger.warning(f"Could not evaluate {n_topics} topics: {str(e)}")
                continue
        
        logger.info(f"Optimal topics found: {best_n_topics} with score: {best_score:.4f}")
        return max(1, best_n_topics)
    
    except Exception as e:
        logger.error(f"Error finding optimal topics: {str(e)}")
        return 3  # Default fallback


def create_topic_modeler(documents, method='lda', auto_select_topics=True):
    """Convenience function to create and configure topic modeler"""
    
    if auto_select_topics:
        # Use auto mode to dynamically determine topics
        modeler = TopicModeler(n_topics='auto', method=method)
    else:
        # For manual control, calculate based on text length
        if isinstance(documents, str):
            word_count = len(documents.split())
            n_topics = max(2, min(8, word_count // 150))
        else:
            total_words = sum(len(doc.split()) for doc in documents)
            n_topics = max(2, min(10, total_words // 200))
        
        modeler = TopicModeler(n_topics=n_topics, method=method)
    
    return modeler