import { useState } from 'react';
import { Sparkles, Trash2 } from 'lucide-react';
import Header from './components/Header';
import FileUpload from './components/FileUpload';
import TextPreview from './components/TextPreview';
import SentimentCard from './components/SentimentCard';
import KeywordsCard from './components/KeywordsCard';
import TopicsCard from './components/TopicsCard';
import LoadingSpinner from './components/LoadingSpinner';
import { AnalysisResult } from './types';

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [textContent, setTextContent] = useState<string>('');
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = async (file: File) => {
    setSelectedFile(file);
    setError(null);

    try {
      const text = await file.text();
      setTextContent(text);
    } catch (err) {
      setError('Failed to read file. Please try again.');
      console.error('Error reading file:', err);
    }
  };

  const handleAnalyze = async () => {
    if (!textContent) {
      setError('Please upload a file first');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
      const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

      const apiUrl = `${supabaseUrl}/functions/v1/analyze-text`;

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${supabaseAnonKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: textContent,
          filename: selectedFile?.name || 'untitled.txt',
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze text');
      }

      const result = await response.json();
      setAnalysisResult(result);
    } catch (err) {
      setError('Failed to analyze text. Please try again.');
      console.error('Error analyzing text:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    setTextContent('');
    setAnalysisResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {isLoading && <LoadingSpinner />}

      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="space-y-6">
            <FileUpload
              onFileSelect={handleFileSelect}
              selectedFile={selectedFile}
              onClear={handleClear}
            />
            <TextPreview text={textContent} />
          </div>

          <div className="space-y-6">
            {analysisResult ? (
              <>
                <SentimentCard
                  sentiment={analysisResult.sentiment}
                  score={analysisResult.sentimentScore}
                />
                <KeywordsCard keywords={analysisResult.keywords} />
                <TopicsCard topics={analysisResult.topics} />
              </>
            ) : (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
                <Sparkles className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Ready to Analyze
                </h3>
                <p className="text-sm text-gray-600">
                  Upload a document and click "Analyze Text" to see insights
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="flex justify-center space-x-4">
          <button
            onClick={handleAnalyze}
            disabled={!textContent || isLoading}
            className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-3 rounded-lg font-semibold shadow-md hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <Sparkles className="w-5 h-5" />
            <span>Analyze Text</span>
          </button>

          {(textContent || analysisResult) && (
            <button
              onClick={handleClear}
              className="bg-white text-gray-700 px-8 py-3 rounded-lg font-semibold border border-gray-300 shadow-sm hover:shadow-md transition-all flex items-center space-x-2"
            >
              <Trash2 className="w-5 h-5" />
              <span>Clear</span>
            </button>
          )}
        </div>
      </main>

      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-600">
            NarrativeNexus &copy; 2025 - Powered by Advanced NLP
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
