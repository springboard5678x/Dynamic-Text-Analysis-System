from rest_framework import serializers
from .models import TextAnalysis

class TextAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextAnalysis
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class TextAnalysisCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextAnalysis
        fields = ('title', 'input_text', 'uploaded_file')