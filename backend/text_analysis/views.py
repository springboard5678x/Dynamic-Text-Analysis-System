from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.http import FileResponse
from django.db import models
import os
import uuid
import logging
import threading

from .models import TextAnalysis
from .serializers import TextAnalysisSerializer, TextAnalysisCreateSerializer
from .utils.preprocessing import TextPreprocessor, read_file_content
from .utils.topic_modeling import TopicModeler, find_optimal_topics, create_topic_modeler
from .utils.sentiment_analysis import SentimentAnalyzer
from .utils.summarization import TextSummarizer
from .utils.visualization import VisualizationGenerator
from .utils.report_generator import PDFReportGenerator

logger = logging.getLogger(__name__)

class TextAnalysisViewSet(viewsets.ModelViewSet):
    queryset = TextAnalysis.objects.all().order_by('-created_at')
    serializer_class = TextAnalysisSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TextAnalysisCreateSerializer
        return TextAnalysisSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Get text content
            input_text = serializer.validated_data.get('input_text', '')
            uploaded_file = serializer.validated_data.get('uploaded_file')
            title = serializer.validated_data.get('title', 'Untitled Analysis')
            
            analysis = None
            
            if uploaded_file:
                # Validate file type
                file_extension = uploaded_file.name.split('.')[-1].lower()
                allowed_extensions = ['txt', 'csv', 'docx']
                
                if file_extension not in allowed_extensions:
                    return Response(
                        {'error': f'Unsupported file type. Allowed types: {", ".join(allowed_extensions)}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Validate file size (10MB limit)
                if uploaded_file.size > 10 * 1024 * 1024:
                    return Response(
                        {'error': 'File size exceeds 10MB limit'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                file_type = file_extension
                
                # Create analysis instance
                analysis = TextAnalysis(
                    title=title,
                    uploaded_file=uploaded_file,
                    file_type=file_type
                )
                analysis.save()
                
                # Read file content
                file_path = analysis.uploaded_file.path
                input_text = read_file_content(file_path, file_type)
                
            else:
                # Validate text input
                if not input_text.strip():
                    return Response(
                        {'error': 'Please provide either text input or upload a file'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if len(input_text.strip()) < 50:
                    return Response(
                        {'error': 'Text input should be at least 50 characters long'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                analysis = TextAnalysis(
                    title=title,
                    input_text=input_text
                )
                analysis.save()
            
            # ✅ QUICK FIX: Start processing in background thread and return immediately
            thread = threading.Thread(
                target=self._perform_complete_analysis_thread,
                args=(analysis.id, input_text)
            )
            thread.daemon = True
            thread.start()
            
            # Return immediate response with analysis ID
            response_data = {
                'id': analysis.id,
                'title': analysis.title,
                'status': 'processing',
                'message': 'Analysis started successfully. Please check back in a moment for results.',
                'created_at': analysis.created_at.isoformat(),
                'report_available': False,
                'report_download_url': None
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error in analysis creation: {str(e)}")
            # Clean up if analysis was created but failed
            if 'analysis' in locals() and analysis and analysis.pk:
                analysis.delete()
            return Response(
                {'error': f'Analysis failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _perform_complete_analysis_thread(self, analysis_id, text):
        """Wrapper for threaded execution"""
        try:
            analysis = TextAnalysis.objects.get(id=analysis_id)
            self._perform_complete_analysis(analysis, text)
            logger.info(f"Background analysis completed for {analysis_id}")
        except Exception as e:
            logger.error(f"Background analysis failed for {analysis_id}: {e}")
    
    def _perform_complete_analysis(self, analysis, text):
        try:
            # Validate text quality
            if len(text.strip()) < 50:
                logger.warning("Text is too short, performing basic analysis")
                return self._perform_basic_analysis(analysis, text)
            
            # Check text encoding and clean if necessary
            text = self._clean_input_text(text)
            
            logger.info(f"Starting comprehensive analysis for: {analysis.title}")
            logger.info(f"Text length: {len(text)} chars, {len(text.split())} words")
            
            # Initialize components with error handling
            try:
                preprocessor = TextPreprocessor()
                sentiment_analyzer = SentimentAnalyzer()
                summarizer = TextSummarizer()  # Updated class
                
                # Use simpler topic modeling for problematic texts
                if len(text.split()) < 100:
                    logger.info("Short text, using basic topic modeling")
                    topic_modeler = TopicModeler(n_topics=2, method='lda')
                else:
                    topic_modeler = create_topic_modeler(text, method='lda', auto_select_topics=True)
                    
                visualizer = VisualizationGenerator()
            except Exception as e:
                logger.error(f"Component initialization failed: {e}")
                raise Exception(f"Analysis components failed to initialize: {str(e)}")
            
            # Preprocess text with validation
            processed_text = preprocessor.preprocess_text(text)
            if len(processed_text.split()) < 10:
                logger.warning("Insufficient text after preprocessing")
                return self._perform_basic_analysis(analysis, text)
            
            # Prepare documents for topic modeling
            words = text.split()
            if len(words) > 1500:
                # For large documents, split into chunks
                chunk_size = 800
                chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
                chunks = chunks[:8]  # Limit to 8 chunks maximum
                analysis_chunks = chunks
                logger.info(f"Split document into {len(analysis_chunks)} chunks for topic modeling")
            else:
                # For smaller documents, use the whole text
                analysis_chunks = [processed_text]
                logger.info("Using single document for topic modeling")
            
            # Topic Modeling
            logger.info("Performing topic modeling...")
            try:
                topics = topic_modeler.fit(analysis_chunks)
                analysis.topics_json = topics
                logger.info(f"Successfully generated {len(topics)} topics")
            except Exception as e:
                logger.error(f"Topic modeling failed: {e}")
                # Use fallback topics
                topics = topic_modeler.get_fallback_topics(analysis_chunks)
                analysis.topics_json = topics
                logger.info(f"Using fallback topics: {len(topics)} topics")
            
            # Sentiment Analysis
            logger.info("Performing sentiment analysis...")
            try:
                sentiment_results = sentiment_analyzer.analyze_text_sentiment(text)
                analysis.sentiment_distribution = sentiment_results
                logger.info(f"Overall sentiment: {sentiment_results['overall_sentiment']}")
            except Exception as e:
                logger.error(f"Sentiment analysis failed: {e}")
                # Fallback sentiment
                analysis.sentiment_distribution = {
                    'overall_sentiment': 'neutral',
                    'overall_polarity': 0.0,
                    'distribution': {'positive': 1, 'neutral': 1, 'negative': 1},
                    'sentence_level': [0.0]
                }
            
            # Summarization with better error handling
            logger.info("Generating summaries...")
            try:
                analysis.extractive_summary = summarizer.extractive_summary(text, sentences_count=4)
                logger.info("Extractive summary generated")
            except Exception as e:
                logger.error(f"Extractive summarization failed: {e}")
                analysis.extractive_summary = "Unable to generate extractive summary."
            
            try:
                abstractive_result = summarizer.abstractive_summary(
                    text, 
                    max_length=150, 
                    min_length=50
                )
                
                # Check if we got a valid result
                if abstractive_result and len(abstractive_result.strip()) > 20:
                    analysis.abstractive_summary = abstractive_result
                    logger.info("Abstractive summary generated successfully")
                else:
                    analysis.abstractive_summary = "Generated summary was too short or empty. Using extractive summary as fallback."
                    logger.warning("Abstractive summary result was insufficient")
                    
            except Exception as e:
                logger.error(f"Abstractive summarization failed: {e}")
                analysis.abstractive_summary = "Unable to generate abstractive summary. Using extractive summary instead."
            
            # Generate Visualizations
            logger.info("Creating visualizations...")
            try:
                analysis.topic_chart_path = visualizer.generate_topic_barchart(
                    topics, str(analysis.id)
                )
                logger.info("Topic chart generated")
            except Exception as e:
                logger.error(f"Topic chart generation failed: {e}")
                analysis.topic_chart_path = None
            
            try:
                analysis.sentiment_chart_path = visualizer.generate_sentiment_chart(
                    sentiment_results['distribution'], str(analysis.id)
                )
                logger.info("Sentiment chart generated")
            except Exception as e:
                logger.error(f"Sentiment chart generation failed: {e}")
                analysis.sentiment_chart_path = None
            
            try:
                analysis.wordcloud_path = visualizer.generate_wordcloud(
                    processed_text, str(analysis.id)
                )
                logger.info("Word cloud generated")
            except Exception as e:
                logger.error(f"Word cloud generation failed: {e}")
                analysis.wordcloud_path = None
            
            # Generate actionable insights
            logger.info("Generating actionable insights...")
            try:
                analysis.actionable_insights = self._generate_insights(
                    topics, sentiment_results, analysis.extractive_summary, text
                )
                logger.info(f"Generated {len(analysis.actionable_insights)} insights")
            except Exception as e:
                logger.error(f"Insight generation failed: {e}")
                analysis.actionable_insights = [{
                    'type': 'error_fallback',
                    'title': 'Analysis Completed',
                    'description': 'Basic analysis performed with some limitations',
                    'recommendation': 'Review the generated topics and summaries for insights',
                    'priority': 'medium'
                }]
            
            # Generate PDF Report
            logger.info("Generating PDF report...")
            try:
                report_generator = PDFReportGenerator()
                report_path = report_generator.generate_report(analysis, text)
                # Store relative path from MEDIA_ROOT
                analysis.generated_report.name = report_path
                logger.info(f"PDF report saved with path: {report_path}")
            except Exception as e:
                logger.error(f"PDF report generation failed: {e}")
                analysis.generated_report = None

            analysis.save()
            logger.info("Analysis completed and saved successfully")
            
        except Exception as e:
            logger.error(f"Error in complete analysis: {str(e)}")
            # Try to save whatever we have
            try:
                analysis.save()
                logger.info("Partial analysis saved despite errors")
            except:
                if analysis.pk:
                    analysis.delete()
                    logger.info("Analysis deleted due to critical errors")
            raise e

    def _clean_input_text(self, text):
        """Clean and validate input text"""
        # Remove null bytes and problematic characters
        text = text.replace('\x00', '').replace('\ufffd', '')
        
        # Ensure proper encoding
        try:
            text = text.encode('utf-8', 'ignore').decode('utf-8')
        except:
            text = text.encode('ascii', 'ignore').decode('ascii')
        
        # Remove excessive whitespace but preserve paragraph structure
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = ' '.join(line.split())  # Collapse multiple spaces
            if len(line.strip()) > 1:  # Keep non-empty lines
                cleaned_lines.append(line.strip())
        
        return '\n'.join(cleaned_lines)
    
    def _perform_basic_analysis(self, analysis, text):
        """Perform basic analysis for short or problematic texts"""
        logger.info("Performing basic analysis")
        
        preprocessor = TextPreprocessor()
        sentiment_analyzer = SentimentAnalyzer()
        summarizer = TextSummarizer()
        
        try:
            # Basic sentiment analysis
            sentiment_results = sentiment_analyzer.analyze_text_sentiment(text)
            analysis.sentiment_distribution = sentiment_results
            
            # Basic summarization
            analysis.extractive_summary = summarizer.extractive_summary(text, sentences_count=2)
            analysis.abstractive_summary = "Text is too short for detailed abstractive summarization. Consider providing more content for comprehensive analysis."
            
            # Generate basic topics from word frequency
            processed_text = preprocessor.preprocess_text(text)
            from .utils.topic_modeling import TopicModeler
            modeler = TopicModeler(n_topics=1)
            topics = modeler.get_fallback_topics([text])
            analysis.topics_json = topics
            
            # Basic insights
            analysis.actionable_insights = [{
                'type': 'basic_analysis',
                'title': 'Basic Text Analysis Completed',
                'description': 'Analysis performed on limited text content',
                'recommendation': 'For more detailed insights, provide longer text with more contextual information',
                'priority': 'low'
            }]
            
            # Try to generate basic visualizations
            try:
                visualizer = VisualizationGenerator()
                if len(topics) > 0:
                    analysis.topic_chart_path = visualizer.generate_topic_barchart(topics, str(analysis.id))
                analysis.sentiment_chart_path = visualizer.generate_sentiment_chart(
                    sentiment_results['distribution'], str(analysis.id)
                )
                if processed_text:
                    analysis.wordcloud_path = visualizer.generate_wordcloud(processed_text, str(analysis.id))
            except Exception as e:
                logger.warning(f"Basic visualization generation failed: {e}")
            
            analysis.save()
            logger.info("Basic analysis completed successfully")
            
        except Exception as e:
            logger.error(f"Basic analysis also failed: {e}")
            raise e
    
    def _generate_insights(self, topics, sentiment_results, summary, original_text):
        insights = []
        
        # Topic-based insights
        if topics and len(topics) > 0:
            main_topics = [topic['words'][:3] for topic in topics[:3]]
            topic_words = []
            for topic in main_topics:
                topic_words.extend(topic)
            
            topic_insight = {
                'type': 'key_themes',
                'title': 'Primary Topics Identified',
                'description': f"Main themes include: {', '.join(topic_words[:6])}",
                'recommendation': 'Focus on these key areas for content strategy and analysis',
                'priority': 'high'
            }
            insights.append(topic_insight)
            
            # Topic diversity insight
            unique_words = set()
            for topic in topics[:3]:
                unique_words.update(topic['words'][:4])
            
            if len(unique_words) > 8:
                insights.append({
                    'type': 'topic_diversity',
                    'title': 'Good Topic Diversity',
                    'description': f'Found {len(unique_words)} unique key terms across topics',
                    'recommendation': 'Content covers multiple themes - consider segmenting analysis by topics',
                    'priority': 'medium'
                })
            elif len(unique_words) <= 4:
                insights.append({
                    'type': 'topic_focus',
                    'title': 'Focused Content',
                    'description': 'Content focuses on a few key themes',
                    'recommendation': 'Consider expanding content scope for broader coverage',
                    'priority': 'low'
                })
        
        # Sentiment-based insights
        sentiment = sentiment_results.get('overall_sentiment', 'neutral')
        distribution = sentiment_results.get('distribution', {'positive': 0, 'neutral': 0, 'negative': 0})
        total_sentences = sum(distribution.values())
        
        if total_sentences > 0:
            if sentiment == 'positive' and distribution['positive'] / total_sentences > 0.6:
                insights.append({
                    'type': 'sentiment_positive',
                    'title': 'Strong Positive Sentiment',
                    'description': f"Positive sentiment dominates ({distribution['positive']/total_sentences*100:.1f}% of content)",
                    'recommendation': 'Leverage positive aspects in marketing and communication materials',
                    'priority': 'high'
                })
            elif sentiment == 'negative' and distribution['negative'] / total_sentences > 0.4:
                insights.append({
                    'type': 'sentiment_negative',
                    'title': 'Significant Negative Sentiment',
                    'description': f"Negative sentiment present ({distribution['negative']/total_sentences*100:.1f}% of content)",
                    'recommendation': 'Address concerns and improve communication. Consider sentiment root cause analysis.',
                    'priority': 'high'
                })
            elif sentiment == 'neutral' and distribution['neutral'] / total_sentences > 0.7:
                insights.append({
                    'type': 'sentiment_neutral',
                    'title': 'Primarily Neutral Tone',
                    'description': 'Content maintains a balanced, factual tone',
                    'recommendation': 'Suitable for technical documentation and reports',
                    'priority': 'low'
                })
            elif distribution['positive'] > 0 and distribution['negative'] > 0:
                insights.append({
                    'type': 'sentiment_mixed',
                    'title': 'Mixed Sentiment Detected',
                    'description': 'Content contains both positive and negative elements',
                    'recommendation': 'Analyze specific sections to understand contrasting opinions',
                    'priority': 'medium'
                })
        
        # Content complexity insights
        word_count = len(original_text.split())
        sentence_count = len([s for s in original_text.split('.') if len(s.strip()) > 10])
        
        if word_count > 2000:
            insights.append({
                'type': 'content_length',
                'title': 'Comprehensive Content',
                'description': f'Document contains {word_count} words across {sentence_count} sentences',
                'recommendation': 'Consider breaking down into smaller, focused sections for better readability',
                'priority': 'medium'
            })
        elif word_count > 800:
            insights.append({
                'type': 'content_optimal',
                'title': 'Well-Sized Content',
                'description': f'Document has {word_count} words, suitable for detailed analysis',
                'recommendation': 'Ideal length for comprehensive topic modeling and sentiment analysis',
                'priority': 'low'
            })
        elif word_count < 300:
            insights.append({
                'type': 'content_brief',
                'title': 'Concise Content',
                'description': f'Document is brief with {word_count} words',
                'recommendation': 'Content may benefit from additional details and examples for deeper insights',
                'priority': 'low'
            })
        
        # Summary effectiveness insight
        if summary and word_count > 0:
            summary_word_count = len(summary.split())
            compression_ratio = summary_word_count / word_count
            
            if compression_ratio < 0.3:
                insights.append({
                    'type': 'summary_efficiency',
                    'title': 'Effective Summarization',
                    'description': f'Summary captures key points in {summary_word_count} words ({compression_ratio*100:.1f}% of original)',
                    'recommendation': 'Use summary for quick decision-making and executive briefings',
                    'priority': 'medium'
                })
        
        # Domain-specific insights based on common keywords
        text_lower = original_text.lower()
        
        if any(keyword in text_lower for keyword in ['customer', 'client', 'user']):
            insights.append({
                'type': 'customer_focus',
                'title': 'Customer-Centric Content',
                'description': 'Content discusses customer-related topics',
                'recommendation': 'Monitor customer sentiment and feedback regularly for continuous improvement',
                'priority': 'high'
            })
        
        if any(keyword in text_lower for keyword in ['issue', 'problem', 'challenge', 'difficulty']):
            insights.append({
                'type': 'problem_areas',
                'title': 'Problem Areas Identified',
                'description': 'Content mentions issues or challenges',
                'recommendation': 'Investigate root causes and develop targeted action plans',
                'priority': 'high'
            })
        
        if any(keyword in text_lower for keyword in ['growth', 'improve', 'enhance', 'develop']):
            insights.append({
                'type': 'growth_opportunity',
                'title': 'Growth Opportunities',
                'description': 'Content discusses improvement and development',
                'recommendation': 'Focus on implementing suggested improvements and tracking progress',
                'priority': 'medium'
            })
        
        # Ensure we have at least 3 insights
        while len(insights) < 3:
            insights.append({
                'type': 'general_insight',
                'title': 'Content Analysis Complete',
                'description': 'Comprehensive text analysis performed successfully',
                'recommendation': 'Use the generated insights to inform your strategy and decision-making',
                'priority': 'low'
            })
        
        # Limit to 5 insights maximum
        insights = insights[:5]
        
        return insights
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Check analysis status - more lenient version"""
        try:
            analysis = self.get_object()
            
            # ✅ FIX: More lenient completion check - if we have most major components
            has_essential_data = any([
                analysis.topics_json is not None,
                analysis.sentiment_distribution is not None,
                analysis.extractive_summary is not None
            ])
            
            # Consider complete if we have at least 2 out of 3 essential components
            essential_count = sum([
                analysis.topics_json is not None,
                analysis.sentiment_distribution is not None, 
                analysis.extractive_summary is not None
            ])
            
            is_complete = essential_count >= 2
            
            status_data = {
                'id': analysis.id,
                'title': analysis.title,
                'status': 'complete' if is_complete else 'processing',
                'created_at': analysis.created_at.isoformat(),
                'updated_at': analysis.updated_at.isoformat(),
                'has_topics': bool(analysis.topics_json),
                'has_sentiment': bool(analysis.sentiment_distribution),
                'has_summary': bool(analysis.extractive_summary),
                'has_abstractive_summary': bool(analysis.abstractive_summary),
                'has_insights': bool(analysis.actionable_insights),
                'report_available': bool(analysis.generated_report),
                'essential_count': essential_count,  # Debug info
            }
            
            if analysis.generated_report:
                status_data['report_download_url'] = f"/api/analysis/{analysis.id}/download_report/"
            
            logger.info(f"Status check for {analysis.id}: complete={is_complete}, "
                       f"essential_count={essential_count}/3")
            
            return Response(status_data)
            
        except Exception as e:
            logger.error(f"Error checking status: {e}")
            return Response(
                {'error': 'Error checking analysis status'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def download_report(self, request, pk=None):
        """Download the generated PDF report"""
        try:
            analysis = self.get_object()
            if analysis.generated_report:
                # Use the stored file path - FIXED: Check if file exists
                file_path = analysis.generated_report.path
                logger.info(f"Looking for report at: {file_path}")
                
                if os.path.exists(file_path):
                    response = FileResponse(
                        open(file_path, 'rb'),
                        content_type='application/pdf'
                    )
                    response['Content-Disposition'] = f'attachment; filename="NarrativeNexus_Report_{analysis.id}.pdf"'
                    logger.info(f"Report downloaded successfully for analysis {analysis.id}")
                    return response
                else:
                    logger.warning(f"Report file not found at: {file_path}")
                    # Try alternative path
                    alt_path = os.path.join('media', str(analysis.generated_report))
                    if os.path.exists(alt_path):
                        response = FileResponse(
                            open(alt_path, 'rb'),
                            content_type='application/pdf'
                        )
                        response['Content-Disposition'] = f'attachment; filename="NarrativeNexus_Report_{analysis.id}.pdf"'
                        logger.info(f"Report downloaded from alternative path for analysis {analysis.id}")
                        return response
            
            logger.warning(f"Report not found for analysis {pk}")
            return Response(
                {'error': 'Report not generated or file not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error downloading report: {e}")
            return Response(
                {'error': 'Error downloading report'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def analysis_stats(self, request):
        """Get overall analysis statistics"""
        try:
            total_analyses = TextAnalysis.objects.count()
            recent_analyses = TextAnalysis.objects.order_by('-created_at')[:5]
            
            file_type_stats = TextAnalysis.objects.exclude(file_type__isnull=True).exclude(file_type='').values('file_type').annotate(
                count=models.Count('id')
            )
            
            # Calculate average topics (simplified)
            analyses_with_topics = TextAnalysis.objects.exclude(topics_json__isnull=True)
            avg_topics = 0
            if analyses_with_topics.exists():
                total_topics = sum(len(analysis.topics_json) for analysis in analyses_with_topics if analysis.topics_json)
                avg_topics = total_topics / analyses_with_topics.count()
            
            stats = {
                'total_analyses': total_analyses,
                'recent_analyses': TextAnalysisSerializer(recent_analyses, many=True).data,
                'file_type_distribution': list(file_type_stats),
                'average_topics': round(avg_topics, 1),
            }
            
            return Response(stats)
        except Exception as e:
            logger.error(f"Error getting analysis stats: {e}")
            return Response(
                {'error': 'Error retrieving statistics'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def list(self, request, *args, **kwargs):
        """Override list to include pagination and filtering"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            # Add basic search functionality
            search_query = request.query_params.get('search', None)
            if search_query:
                queryset = queryset.filter(
                    models.Q(title__icontains=search_query) |
                    models.Q(input_text__icontains=search_query)
                )
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error listing analyses: {e}")
            return Response(
                {'error': 'Error retrieving analyses'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to include additional data"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            # Add visualization URLs if available
            data = serializer.data
            
            # Build media URLs for visualizations
            media_base = request.build_absolute_uri('/media/')
            
            if instance.topic_chart_path and os.path.exists(instance.topic_chart_path):
                filename = os.path.basename(instance.topic_chart_path)
                data['topic_chart_url'] = f"{media_base}visualizations/{filename}"
            
            if instance.sentiment_chart_path and os.path.exists(instance.sentiment_chart_path):
                filename = os.path.basename(instance.sentiment_chart_path)
                data['sentiment_chart_url'] = f"{media_base}visualizations/{filename}"
            
            if instance.wordcloud_path and os.path.exists(instance.wordcloud_path):
                filename = os.path.basename(instance.wordcloud_path)
                data['wordcloud_url'] = f"{media_base}visualizations/{filename}"
            
            return Response(data)
        except Exception as e:
            logger.error(f"Error retrieving analysis: {e}")
            return Response(
                {'error': 'Error retrieving analysis details'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )