import os
import django
import tempfile
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrative_nexus.settings')
django.setup()

from .models import TextAnalysis
from .utils.preprocessing import TextPreprocessor, read_file_content
from .utils.topic_modeling import TopicModeler, AdvancedTopicModeler
from .utils.sentiment_analysis import SentimentAnalyzer
from .utils.summarization import TextSummarizer
from .utils.visualization import VisualizationGenerator
from .views import TextAnalysisViewSet


class TextPreprocessingTests(TestCase):
    """Test text preprocessing functionality"""
    
    def setUp(self):
        self.preprocessor = TextPreprocessor()
        self.sample_text = "Hello World! This is a test document. It contains multiple sentences."
        self.dirty_text = "Hello!!! World...   This   has   extra   spaces!!!"
    
    def test_clean_text(self):
        """Test text cleaning"""
        cleaned = self.preprocessor.clean_text(self.dirty_text)
        self.assertNotIn('!', cleaned)
        self.assertNotIn('.', cleaned)
        self.assertEqual(cleaned, 'hello world this has extra spaces')
    
    def test_tokenize_and_lemmatize(self):
        """Test tokenization and lemmatization"""
        tokens = self.preprocessor.tokenize_and_lemmatize(self.sample_text)
        self.assertIsInstance(tokens, list)
        self.assertTrue(all(isinstance(token, str) for token in tokens))
        # Stopwords should be removed
        self.assertNotIn('is', tokens)
        self.assertNotIn('a', tokens)
    
    def test_preprocess_text(self):
        """Test complete preprocessing pipeline"""
        processed = self.preprocessor.preprocess_text(self.sample_text)
        self.assertIsInstance(processed, str)
        self.assertTrue(len(processed) > 0)


class TopicModelingTests(TestCase):
    """Test topic modeling functionality"""
    
    def setUp(self):
        self.documents = [
            "Machine learning is a subset of artificial intelligence",
            "Deep learning uses neural networks with multiple layers",
            "Natural language processing helps computers understand human language",
            "Computer vision enables machines to interpret visual information",
            "Data science involves statistics programming and domain knowledge",
            "Artificial intelligence mimics human intelligence in machines"
        ]
        self.modeler = TopicModeler(n_topics=3, method='lda')
    
    def test_topic_modeler_initialization(self):
        """Test topic modeler initialization"""
        self.assertEqual(self.modeler.n_topics, 3)
        self.assertEqual(self.modeler.method, 'lda')
        self.assertFalse(self.modeler.is_fitted)
    
    def test_topic_modeling_fit(self):
        """Test fitting topic model"""
        topics = self.modeler.fit(self.documents)
        
        self.assertTrue(self.modeler.is_fitted)
        self.assertIsInstance(topics, list)
        self.assertEqual(len(topics), 3)
        
        # Check topic structure
        for topic in topics:
            self.assertIn('topic_id', topic)
            self.assertIn('words', topic)
            self.assertIn('weights', topic)
            self.assertIn('coherence_score', topic)
            self.assertIsInstance(topic['words'], list)
            self.assertIsInstance(topic['weights'], list)
            self.assertEqual(len(topic['words']), len(topic['weights']))
    
    def test_topic_modeling_invalid_input(self):
        """Test topic modeling with invalid input"""
        with self.assertRaises(ValueError):
            self.modeler.fit([])
        
        with self.assertRaises(ValueError):
            self.modeler.fit(['', '   ', ''])
    
    def test_predict_topics(self):
        """Test topic prediction for new documents"""
        self.modeler.fit(self.documents)
        new_docs = ["Machine learning and deep learning", "Computer vision applications"]
        predictions = self.modeler.predict_topics(new_docs)
        
        self.assertIsInstance(predictions, list)
        self.assertEqual(len(predictions), len(new_docs))
        for pred in predictions:
            self.assertIsInstance(pred, list)
            self.assertEqual(len(pred), 3)  # 3 topics
    
    def test_document_topics(self):
        """Test document topic assignment"""
        self.modeler.fit(self.documents)
        doc_topics = self.modeler.get_document_topics(self.documents)
        
        self.assertIsInstance(doc_topics, list)
        self.assertEqual(len(doc_topics), len(self.documents))
        
        for doc_topic in doc_topics:
            self.assertIn('document_id', doc_topic)
            self.assertIn('topic_distribution', doc_topic)
            self.assertIn('main_topic', doc_topic)
            self.assertIn('main_topic_score', doc_topic)
    
    def test_model_evaluation(self):
        """Test model evaluation"""
        self.modeler.fit(self.documents)
        evaluation = self.modeler.evaluate_model(self.documents)
        
        self.assertIsInstance(evaluation, dict)
        self.assertIn('method', evaluation)
        self.assertIn('n_topics', evaluation)
        self.assertIn('average_coherence', evaluation)
        self.assertIn('n_documents', evaluation)


class AdvancedTopicModelingTests(TestCase):
    """Test advanced topic modeling functionality"""
    
    def setUp(self):
        self.documents = [
            "Machine learning algorithms improve with more data",
            "Deep neural networks require powerful hardware",
            "Natural language processing understands text data",
            "Computer vision analyzes images and videos",
            "Data scientists use Python and R for analysis",
            "AI systems can learn and adapt over time"
        ]
        self.advanced_modeler = AdvancedTopicModeler()
    
    def test_optimal_topic_finding(self):
        """Test finding optimal number of topics"""
        results = self.advanced_modeler.find_optimal_topics(
            self.documents, 
            max_topics=5, 
            method='lda'
        )
        
        self.assertIsInstance(results, dict)
        self.assertTrue(len(results) > 0)
        
        for n_topics, result in results.items():
            self.assertIn('coherence_score', result)
            self.assertIn('topics', result)
            self.assertIsInstance(result['topics'], list)


class SentimentAnalysisTests(TestCase):
    """Test sentiment analysis functionality"""
    
    def setUp(self):
        self.analyzer = SentimentAnalyzer()
        self.positive_text = "I love this product! It's amazing and wonderful."
        self.negative_text = "This is terrible. I hate it and it doesn't work."
        self.neutral_text = "The product arrived today. It is a product."
    
    def test_sentiment_analysis(self):
        """Test sentiment analysis"""
        result = self.analyzer.analyze_text_sentiment(self.positive_text)
        
        self.assertIsInstance(result, dict)
        self.assertIn('overall_sentiment', result)
        self.assertIn('overall_polarity', result)
        self.assertIn('distribution', result)
        self.assertIn('sentence_level', result)
        
        self.assertIn('positive', result['distribution'])
        self.assertIn('neutral', result['distribution'])
        self.assertIn('negative', result['distribution'])
    
    def test_sentiment_categorization(self):
        """Test sentiment categorization"""
        positive_result = self.analyzer.analyze_text_sentiment(self.positive_text)
        negative_result = self.analyzer.analyze_text_sentiment(self.negative_text)
        neutral_result = self.analyzer.analyze_text_sentiment(self.neutral_text)
        
        self.assertEqual(positive_result['overall_sentiment'], 'positive')
        self.assertEqual(negative_result['overall_sentiment'], 'negative')
        self.assertEqual(neutral_result['overall_sentiment'], 'neutral')


class SummarizationTests(TestCase):
    """Test text summarization functionality"""
    
    def setUp(self):
        self.summarizer = TextSummarizer()
        self.long_text = """
        Machine learning is a method of data analysis that automates analytical model building. 
        It is a branch of artificial intelligence based on the idea that systems can learn from data, 
        identify patterns and make decisions with minimal human intervention. Machine learning algorithms 
        are used in a wide variety of applications, such as email filtering and computer vision, 
        where it is difficult or infeasible to develop conventional algorithms to perform the needed tasks.
        Deep learning is part of a broader family of machine learning methods based on artificial neural networks 
        with representation learning. Learning can be supervised, semi-supervised or unsupervised.
        """
    
    def test_extractive_summarization(self):
        """Test extractive summarization"""
        summary = self.summarizer.extractive_summary(self.long_text, sentences_count=2)
        
        self.assertIsInstance(summary, str)
        self.assertTrue(len(summary) > 0)
        self.assertTrue(len(summary) < len(self.long_text))
    
    @patch('transformers.pipeline')
    def test_abstractive_summarization(self, mock_pipeline):
        """Test abstractive summarization with mock"""
        mock_summarizer = MagicMock()
        mock_summarizer.return_value = [{'summary_text': 'This is a summary.'}]
        mock_pipeline.return_value = mock_summarizer
        
        summary = self.summarizer.abstractive_summary(self.long_text)
        
        self.assertIsInstance(summary, str)
        self.assertTrue(len(summary) > 0)


class VisualizationTests(TestCase):
    """Test visualization generation"""
    
    def setUp(self):
        self.visualizer = VisualizationGenerator()
        self.topics = [
            {
                'topic_id': 1,
                'words': ['machine', 'learning', 'data', 'algorithm'],
                'weights': [0.9, 0.8, 0.7, 0.6]
            },
            {
                'topic_id': 2,
                'words': ['neural', 'network', 'deep', 'layer'],
                'weights': [0.85, 0.75, 0.65, 0.55]
            }
        ]
        self.sentiment_distribution = {'positive': 40, 'neutral': 30, 'negative': 30}
        self.sample_text = "machine learning data science artificial intelligence"
    
    def test_topic_barchart_generation(self):
        """Test topic bar chart generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.visualizer.output_dir = temp_dir
            chart_path = self.visualizer.generate_topic_barchart(self.topics, 'test123')
            
            self.assertIsInstance(chart_path, str)
            self.assertTrue(os.path.exists(chart_path))
            self.assertTrue(chart_path.endswith('.png'))
    
    def test_sentiment_chart_generation(self):
        """Test sentiment chart generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.visualizer.output_dir = temp_dir
            chart_path = self.visualizer.generate_sentiment_chart(
                self.sentiment_distribution, 
                'test123'
            )
            
            self.assertIsInstance(chart_path, str)
            self.assertTrue(os.path.exists(chart_path))
            self.assertTrue(chart_path.endswith('.png'))
    
    def test_wordcloud_generation(self):
        """Test word cloud generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.visualizer.output_dir = temp_dir
            cloud_path = self.visualizer.generate_wordcloud(self.sample_text, 'test123')
            
            self.assertIsInstance(cloud_path, str)
            self.assertTrue(os.path.exists(cloud_path))
            self.assertTrue(cloud_path.endswith('.png'))


class ModelTests(TestCase):
    """Test database models"""
    
    def test_text_analysis_creation(self):
        """Test TextAnalysis model creation"""
        analysis = TextAnalysis.objects.create(
            title="Test Analysis",
            input_text="This is a test document for analysis."
        )
        
        self.assertEqual(analysis.title, "Test Analysis")
        self.assertEqual(analysis.input_text, "This is a test document for analysis.")
        self.assertIsNotNone(analysis.id)
        self.assertIsNotNone(analysis.created_at)


class ViewTests(TestCase):
    """Test API views"""
    
    def setUp(self):
        self.viewset = TextAnalysisViewSet()
    
    def test_analysis_insight_generation(self):
        """Test actionable insight generation"""
        topics = [
            {
                'topic_id': 1,
                'words': ['customer', 'service', 'satisfaction', 'experience'],
                'weights': [0.9, 0.8, 0.7, 0.6]
            }
        ]
        sentiment_results = {
            'overall_sentiment': 'positive',
            'overall_polarity': 0.8,
            'distribution': {'positive': 70, 'neutral': 20, 'negative': 10}
        }
        summary = "Customers are generally satisfied with the service experience."
        
        insights = self.viewset._generate_insights(topics, sentiment_results, summary)
        
        self.assertIsInstance(insights, list)
        self.assertTrue(len(insights) > 0)
        
        for insight in insights:
            self.assertIn('type', insight)
            self.assertIn('title', insight)
            self.assertIn('description', insight)
            self.assertIn('recommendation', insight)


class IntegrationTests(TestCase):
    """Integration tests for complete pipeline"""
    
    def test_complete_analysis_pipeline(self):
        """Test complete analysis pipeline"""
        sample_text = """
        Customer feedback about our new product has been overwhelmingly positive. 
        Users love the intuitive interface and fast performance. However, some customers 
        reported issues with the mobile app crashing occasionally. The support team 
        is actively working on fixing these issues. Overall, customer satisfaction 
        remains high with most users recommending the product to others.
        """
        
        # Test preprocessing
        preprocessor = TextPreprocessor()
        processed_text = preprocessor.preprocess_text(sample_text)
        self.assertTrue(len(processed_text) > 0)
        
        # Test topic modeling
        modeler = TopicModeler(n_topics=2, method='lda')
        topics = modeler.fit([sample_text])
        self.assertEqual(len(topics), 2)
        
        # Test sentiment analysis
        analyzer = SentimentAnalyzer()
        sentiment = analyzer.analyze_text_sentiment(sample_text)
        self.assertIn(sentiment['overall_sentiment'], ['positive', 'neutral', 'negative'])
        
        # Test summarization
        summarizer = TextSummarizer()
        extractive = summarizer.extractive_summary(sample_text)
        self.assertTrue(len(extractive) > 0)
        
        print("Integration test completed successfully!")


def run_all_tests():
    """Run all tests and print results"""
    import unittest
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TextPreprocessingTests)
    suite.addTests(loader.loadTestsFromTestCase(TopicModelingTests))
    suite.addTests(loader.loadTestsFromTestCase(AdvancedTopicModelingTests))
    suite.addTests(loader.loadTestsFromTestCase(SentimentAnalysisTests))
    suite.addTests(loader.loadTestsFromTestCase(SummarizationTests))
    suite.addTests(loader.loadTestsFromTestCase(VisualizationTests))
    suite.addTests(loader.loadTestsFromTestCase(ModelTests))
    suite.addTests(loader.loadTestsFromTestCase(ViewTests))
    suite.addTests(loader.loadTestsFromTestCase(IntegrationTests))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Running NarrativeNexus Backend Tests...")
    success = run_all_tests()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")