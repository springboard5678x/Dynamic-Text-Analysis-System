from django.db import models
import os
import uuid

def uploaded_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('uploaded_files', filename)

def report_file_path(instance, filename):
    return os.path.join('generated_reports', filename)

class TextAnalysis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    input_text = models.TextField(blank=True, null=True)
    uploaded_file = models.FileField(upload_to=uploaded_file_path, blank=True, null=True)
    file_type = models.CharField(max_length=10, blank=True, null=True)
    
    # Analysis results
    topics_json = models.JSONField(blank=True, null=True)
    sentiment_distribution = models.JSONField(blank=True, null=True)
    wordcloud_data = models.JSONField(blank=True, null=True)
    extractive_summary = models.TextField(blank=True, null=True)
    abstractive_summary = models.TextField(blank=True, null=True)
    actionable_insights = models.JSONField(blank=True, null=True)
    
    # Visualization paths
    topic_chart_path = models.CharField(max_length=500, blank=True, null=True)
    sentiment_chart_path = models.CharField(max_length=500, blank=True, null=True)
    wordcloud_path = models.CharField(max_length=500, blank=True, null=True)
    
    # Report
    generated_report = models.FileField(upload_to=report_file_path, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Analysis: {self.title} - {self.created_at}"