import re
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import docx

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

class TextPreprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
    
    def clean_text(self, text):
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def tokenize_and_lemmatize(self, text):
        tokens = word_tokenize(text)
        # Remove stopwords and lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                 if token not in self.stop_words and len(token) > 2]
        return tokens
    
    def preprocess_text(self, text):
        cleaned_text = self.clean_text(text)
        tokens = self.tokenize_and_lemmatize(cleaned_text)
        return ' '.join(tokens)

def read_file_content(file_path, file_type):
    """Read content from different file types"""
    try:
        if file_type == 'txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        elif file_type == 'csv':
            df = pd.read_csv(file_path)
            # Combine all text columns
            text_columns = df.select_dtypes(include=['object']).columns
            return ' '.join(df[col].astype(str).str.cat(sep=' ') for col in text_columns)
        elif file_type == 'docx':
            doc = docx.Document(file_path)
            return ' '.join([paragraph.text for paragraph in doc.paragraphs])
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    except Exception as e:
        raise Exception(f"Error reading file: {str(e)}")