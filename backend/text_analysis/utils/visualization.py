import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import base64
from io import BytesIO
import os
import logging

logger = logging.getLogger(__name__)

class VisualizationGenerator:
    def __init__(self, output_dir='media/visualizations'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        plt.style.use('default')
    
    def generate_topic_barchart(self, topics, analysis_id):
        try:
            if not topics or len(topics) == 0:
                logger.warning("No topics provided for barchart generation")
                return None
                
            # Create figure and axes
            n_topics = len(topics)
            fig, axes = plt.subplots(n_topics, 1, figsize=(10, 3 * n_topics))
            
            if n_topics == 1:
                axes = [axes]
            
            for idx, topic in enumerate(topics):
                words = topic['words'][:6]  # Top 6 words
                weights = topic['weights'][:6]
                
                # Create horizontal bar chart
                bars = axes[idx].barh(words, weights, color=sns.color_palette("husl", len(words)))
                axes[idx].set_title(f'Topic {topic["topic_id"]}', fontsize=12, fontweight='bold')
                axes[idx].set_xlabel('Importance Score', fontsize=10)
                axes[idx].tick_params(axis='both', which='major', labelsize=9)
                
                # Add value labels on bars
                for bar, weight in zip(bars, weights):
                    width = bar.get_width()
                    axes[idx].text(width + 0.01, bar.get_y() + bar.get_height()/2, 
                                 f'{width:.2f}', ha='left', va='center', fontsize=8)
            
            plt.tight_layout()
            
            # Save and return path
            filename = f'topic_chart_{analysis_id}.png'
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close(fig)  # Explicitly close the figure
            logger.info(f"Topic chart saved: {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating topic barchart: {e}")
            plt.close('all')  # Close all figures on error
            return None
    
    def generate_sentiment_chart(self, sentiment_distribution, analysis_id):
        try:
            if not sentiment_distribution:
                logger.warning("No sentiment distribution provided")
                return None
                
            labels = list(sentiment_distribution.keys())
            values = list(sentiment_distribution.values())
            
            # Create figure
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Pie chart
            colors = ['#4CAF50', '#FFC107', '#F44336']  # green, yellow, red
            wedges, texts, autotexts = ax1.pie(values, labels=labels, autopct='%1.1f%%', 
                                             colors=colors, startangle=90)
            ax1.set_title('Sentiment Distribution', fontweight='bold')
            
            # Bar chart
            bars = ax2.bar(labels, values, color=colors)
            ax2.set_title('Sentiment Count', fontweight='bold')
            ax2.set_ylabel('Number of Sentences')
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{value}', ha='center', va='bottom')
            
            plt.tight_layout()
            
            filename = f'sentiment_chart_{analysis_id}.png'
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close(fig)
            logger.info(f"Sentiment chart saved: {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating sentiment chart: {e}")
            plt.close('all')
            return None
    
    def generate_wordcloud(self, text, analysis_id):
        try:
            if not text or len(text.strip()) < 10:
                logger.warning("Insufficient text for wordcloud")
                return None
                
            # Generate word cloud
            wordcloud = WordCloud(
                width=800, 
                height=400, 
                background_color='white',
                max_words=100,
                colormap='viridis',
                relative_scaling=0.5
            ).generate(text)
            
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('Key Themes Word Cloud', fontweight='bold')
            
            filename = f'wordcloud_{analysis_id}.png'
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            logger.info(f"Wordcloud saved: {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating wordcloud: {e}")
            plt.close('all')
            return None
    
    def image_to_base64(self, image_path):
        """Convert image to base64 for embedding"""
        try:
            if image_path and os.path.exists(image_path):
                with open(image_path, "rb") as img_file:
                    return base64.b64encode(img_file.read()).decode('utf-8')
            return None
        except Exception as e:
            logger.error(f"Error converting image to base64: {e}")
            return None