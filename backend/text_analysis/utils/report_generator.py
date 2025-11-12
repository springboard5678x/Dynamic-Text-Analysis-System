from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        # Create custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # Center aligned
            textColor=colors.HexColor('#2E86AB')
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.HexColor('#2E86AB')
        )
        
        self.subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=8,
            textColor=colors.HexColor('#4A4A4A')
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceBefore=6,
            spaceAfter=6,
            leading=12
        )
        
        self.highlight_style = ParagraphStyle(
            'CustomHighlight',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceBefore=6,
            spaceAfter=6,
            leading=12,
            backColor=colors.HexColor('#F8F9FA'),
            borderPadding=5,
            borderColor=colors.HexColor('#DEE2E6'),
            borderWidth=1
        )
        
        self.bullet_style = ParagraphStyle(
            'CustomBullet',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceBefore=4,
            spaceAfter=4,
            leftIndent=10,
            bulletIndent=5
        )
    
    def generate_report(self, analysis, original_text):
        try:
            filename = f'report_{analysis.id}.pdf'
            # Store in media/generated_reports directory
            reports_dir = os.path.join('media', 'generated_reports')
            os.makedirs(reports_dir, exist_ok=True)
            filepath = os.path.join(reports_dir, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=0.5*inch)
            story = []
            
            # Title Page
            story.append(Paragraph("NarrativeNexus", self.title_style))
            story.append(Spacer(1, 10))
            story.append(Paragraph("Text Analysis Report", self.title_style))
            story.append(Spacer(1, 40))
            
            # Analysis Overview
            story.append(Paragraph("Analysis Overview", self.heading_style))
            
            overview_data = [
                ["<b>Title:</b>", analysis.title],
                ["<b>Analysis ID:</b>", str(analysis.id)],
                ["<b>Created:</b>", analysis.created_at.strftime('%Y-%m-%d %H:%M')],
                ["<b>Text Length:</b>", f"{len(original_text.split())} words"],
                ["<b>Characters:</b>", f"{len(original_text)} characters"],
            ]
            
            if analysis.file_type:
                overview_data.append(["<b>File Type:</b>", analysis.file_type.upper()])
            
            for label, value in overview_data:
                story.append(Paragraph(f"{label} {value}", self.normal_style))
            
            story.append(PageBreak())
            
            # Executive Summary
            story.append(Paragraph("Executive Summary", self.heading_style))
            
            # Overall sentiment summary
            if analysis.sentiment_distribution:
                sentiment = analysis.sentiment_distribution.get('overall_sentiment', 'neutral')
                polarity = analysis.sentiment_distribution.get('overall_polarity', 0)
                
                sentiment_summary = f"""
                The analysis reveals a <b>{sentiment}</b> overall sentiment with a polarity score of <b>{polarity:.2f}</b>. 
                """
                story.append(Paragraph(sentiment_summary, self.normal_style))
                story.append(Spacer(1, 10))
            
            # Topic summary
            if analysis.topics_json:
                topic_count = len(analysis.topics_json)
                main_topics = []
                for topic in analysis.topics_json[:3]:
                    main_topics.extend(topic['words'][:2])
                
                topic_summary = f"""
                <b>{topic_count} key topics</b> were identified in the text, including: {', '.join(main_topics[:6])}.
                """
                story.append(Paragraph(topic_summary, self.normal_style))
                story.append(Spacer(1, 10))
            
            story.append(PageBreak())
            
            # Key Insights & Recommendations
            story.append(Paragraph("Key Insights & Recommendations", self.heading_style))
            
            if analysis.actionable_insights:
                for insight in analysis.actionable_insights:
                    priority = insight.get('priority', 'medium')
                    priority_color = {
                        'high': '#DC3545',    # Red
                        'medium': '#FFC107',  # Yellow
                        'low': '#28A745'      # Green
                    }.get(priority, '#6C757D')  # Gray default
                    
                    priority_text = {
                        'high': 'HIGH PRIORITY',
                        'medium': 'MEDIUM PRIORITY', 
                        'low': 'LOW PRIORITY'
                    }.get(priority, 'PRIORITY')
                    
                    insight_text = f"""
                    <b><font color="{priority_color}">● {priority_text}</font><br/>
                    {insight['title']}</b><br/>
                    <i>{insight['description']}</i><br/>
                    <b>Recommendation:</b> {insight['recommendation']}
                    """
                    story.append(Paragraph(insight_text, self.highlight_style))
                    story.append(Spacer(1, 12))
            else:
                story.append(Paragraph("No specific insights generated for this analysis.", self.normal_style))
            
            story.append(PageBreak())
            
            # Topic Modeling Analysis
            story.append(Paragraph("Topic Modeling Analysis", self.heading_style))
            
            if analysis.topics_json:
                story.append(Paragraph("Identified Topics:", self.subheading_style))
                
                for topic in analysis.topics_json:
                    words = topic['words'][:8]  # Show top 8 words per topic
                    strength = topic.get('strength', 0)
                    
                    topic_text = f"""
                    <b>Topic {topic['topic_id']}</b> (Strength: {strength:.2f}):<br/>
                    {', '.join(words)}
                    """
                    story.append(Paragraph(topic_text, self.normal_style))
                    story.append(Spacer(1, 8))
                
                # Add topic chart if available
                if analysis.topic_chart_path and os.path.exists(analysis.topic_chart_path):
                    try:
                        story.append(Spacer(1, 15))
                        story.append(Paragraph("Topic Distribution Visualization", self.subheading_style))
                        img = Image(analysis.topic_chart_path, width=6*inch, height=3*inch)
                        story.append(img)
                        story.append(Spacer(1, 10))
                    except Exception as e:
                        logger.warning(f"Could not add topic chart to PDF: {e}")
                        story.append(Paragraph("<i>Topic visualization not available</i>", self.normal_style))
            else:
                story.append(Paragraph("No topics were generated for this analysis.", self.normal_style))
            
            story.append(PageBreak())
            
            # Sentiment Analysis
            story.append(Paragraph("Sentiment Analysis", self.heading_style))
            
            if analysis.sentiment_distribution:
                sentiment = analysis.sentiment_distribution
                
                # Sentiment metrics
                story.append(Paragraph("Sentiment Metrics:", self.subheading_style))
                
                sentiment_data = [
                    ["<b>Overall Sentiment:</b>", sentiment.get('overall_sentiment', 'N/A').title()],
                    ["<b>Polarity Score:</b>", f"{sentiment.get('overall_polarity', 0):.3f}"],
                ]
                
                if 'distribution' in sentiment:
                    dist = sentiment['distribution']
                    total = sum(dist.values())
                    if total > 0:
                        sentiment_data.extend([
                            ["<b>Positive Sentences:</b>", f"{dist.get('positive', 0)} ({dist.get('positive', 0)/total*100:.1f}%)"],
                            ["<b>Neutral Sentences:</b>", f"{dist.get('neutral', 0)} ({dist.get('neutral', 0)/total*100:.1f}%)"],
                            ["<b>Negative Sentences:</b>", f"{dist.get('negative', 0)} ({dist.get('negative', 0)/total*100:.1f}%)"],
                        ])
                
                for label, value in sentiment_data:
                    story.append(Paragraph(f"{label} {value}", self.normal_style))
                
                story.append(Spacer(1, 15))
                
                # Add sentiment chart if available
                if analysis.sentiment_chart_path and os.path.exists(analysis.sentiment_chart_path):
                    try:
                        story.append(Paragraph("Sentiment Distribution", self.subheading_style))
                        img = Image(analysis.sentiment_chart_path, width=6*inch, height=3*inch)
                        story.append(img)
                    except Exception as e:
                        logger.warning(f"Could not add sentiment chart to PDF: {e}")
                        story.append(Paragraph("<i>Sentiment visualization not available</i>", self.normal_style))
            else:
                story.append(Paragraph("Sentiment analysis not available.", self.normal_style))
            
            story.append(PageBreak())
            
            # Word Cloud Visualization
            if analysis.wordcloud_path and os.path.exists(analysis.wordcloud_path):
                try:
                    story.append(Paragraph("Key Themes Word Cloud", self.heading_style))
                    story.append(Paragraph("Visual representation of the most frequent words in the text:", self.normal_style))
                    img = Image(analysis.wordcloud_path, width=6*inch, height=3*inch)
                    story.append(img)
                    story.append(Spacer(1, 15))
                except Exception as e:
                    logger.warning(f"Could not add wordcloud to PDF: {e}")
            
            # Text Summarization
            story.append(Paragraph("Text Summarization", self.heading_style))
            
            # Extractive Summary
            story.append(Paragraph("Extractive Summary", self.subheading_style))
            story.append(Paragraph("Key sentences extracted directly from the original text:", self.normal_style))
            
            if analysis.extractive_summary:
                extractive_text = analysis.extractive_summary
                if len(extractive_text) > 1500:
                    extractive_text = extractive_text[:1500] + "... [truncated]"
                story.append(Paragraph(extractive_text, self.highlight_style))
            else:
                story.append(Paragraph("<i>Extractive summary not available</i>", self.normal_style))
            
            story.append(Spacer(1, 20))
            
            # Abstractive Summary
            story.append(Paragraph("Abstractive Summary", self.subheading_style))
            story.append(Paragraph("AI-generated summary capturing the essence of the text:", self.normal_style))
            
            if analysis.abstractive_summary:
                abstractive_text = analysis.abstractive_summary
                if len(abstractive_text) > 1200:
                    abstractive_text = abstractive_text[:1200] + "... [truncated]"
                story.append(Paragraph(abstractive_text, self.highlight_style))
            else:
                story.append(Paragraph("<i>Abstractive summary not available</i>", self.normal_style))
            
            story.append(PageBreak())
            
            # Technical Details
            story.append(Paragraph("Technical Details", self.heading_style))
            
            # Analysis metadata
            story.append(Paragraph("Analysis Configuration:", self.subheading_style))
            
            tech_details = [
                ["<b>Analysis Method:</b>", "Latent Dirichlet Allocation (LDA) for Topic Modeling"],
                ["<b>Sentiment Analysis:</b>", "TextBlob with pattern analysis"],
                ["<b>Summarization:</b>", "Extractive (LSA) + Abstractive (BART transformer)"],
                ["<b>Text Preprocessing:</b>", "Tokenization, stopword removal, lemmatization"],
            ]
            
            if analysis.topics_json:
                tech_details.append(["<b>Topics Generated:</b>", str(len(analysis.topics_json))])
            
            for label, value in tech_details:
                story.append(Paragraph(f"{label} {value}", self.normal_style))
            
            story.append(Spacer(1, 20))
            
            # Original Text Preview
            story.append(Paragraph("Original Text Preview", self.subheading_style))
            story.append(Paragraph("First 500 characters of the original text:", self.normal_style))
            
            preview_text = original_text[:500] + "..." if len(original_text) > 500 else original_text
            story.append(Paragraph(preview_text, self.highlight_style))
            
            # Footer
            story.append(Spacer(1, 30))
            footer_text = f"""
            Report generated by NarrativeNexus Text Analysis Platform<br/>
            Analysis completed: {datetime.now().strftime('%Y-%m-%d at %H:%M')}<br/>
            Document ID: {analysis.id}
            """
            story.append(Paragraph(footer_text, 
                                 ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=8, alignment=1)))
            
            # Build the document
            doc.build(story)
            logger.info(f"PDF report generated successfully: {filepath}")
            
            # Return the relative path from MEDIA_ROOT for database storage
            return f'generated_reports/{filename}'
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            raise e

    def _create_insight_table(self, insights):
        """Create a formatted table for insights"""
        if not insights:
            return None
            
        data = [['Priority', 'Insight', 'Recommendation']]
        
        for insight in insights:
            priority = insight.get('priority', 'medium').upper()
            title = insight.get('title', '')
            recommendation = insight.get('recommendation', '')
            
            # Color coding for priorities
            if priority == 'HIGH':
                priority = f'<font color="#DC3545">{priority}</font>'
            elif priority == 'MEDIUM':
                priority = f'<font color="#FFC107">{priority}</font>'
            else:
                priority = f'<font color="#28A745">{priority}</font>'
            
            data.append([Paragraph(priority, self.normal_style),
                        Paragraph(title, self.normal_style),
                        Paragraph(recommendation, self.normal_style)])
        
        table = Table(data, colWidths=[1*inch, 2.5*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DEE2E6')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        return table