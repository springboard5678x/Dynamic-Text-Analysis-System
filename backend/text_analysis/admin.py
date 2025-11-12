from django.contrib import admin
from .models import TextAnalysis

@admin.register(TextAnalysis)
class TextAnalysisAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'file_type')
    list_filter = ('created_at', 'file_type')
    search_fields = ('title', 'input_text')
    readonly_fields = ('created_at', 'updated_at')