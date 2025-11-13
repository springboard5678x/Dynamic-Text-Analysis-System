import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { analyzeText, AnalysisResult } from '../services/analysisService';
import mammoth from 'mammoth';
import Papa from 'papaparse';

interface TextInputProps {
  onAnalysisComplete: (result: AnalysisResult) => void;
}

const TextInput: React.FC<TextInputProps> = ({ onAnalysisComplete }) => {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [fileName, setFileName] = useState('');
  const navigate = useNavigate();

  const handleFileUpload = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    setLoading(true);

    try {
      if (file.name.endsWith('.txt')) {
        const fileText = await file.text();
        setText(fileText);
      } else if (file.name.endsWith('.csv')) {
        Papa.parse(file, {
          complete: (results) => {
            const csvText = results.data.map((row: any) => 
              Array.isArray(row) ? row.join(' ') : Object.values(row).join(' ')
            ).join('\n');
            setText(csvText);
          },
          error: (error) => {
            console.error('CSV parsing error:', error);
            alert('Error parsing CSV file');
          }
        });
      } else if (file.name.endsWith('.docx')) {
        const arrayBuffer = await file.arrayBuffer();
        const result = await mammoth.extractRawText({ arrayBuffer });
        setText(result.value);
      } else {
        alert('Please upload a .txt, .csv, or .docx file');
      }
    } catch (error) {
      console.error('File reading error:', error);
      alert('Error reading file');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleAnalyze = async () => {
    if (!text.trim()) {
      alert('Please enter or upload some text to analyze');
      return;
    }

    setLoading(true);
    
    try {
      // Call analysis service (will use Python backend if available)
      const result = await analyzeText(text);
      onAnalysisComplete(result);
      navigate('/dashboard');
    } catch (error) {
      console.error('Analysis error:', error);
      alert('Error analyzing text. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setText('');
    setFileName('');
  };

  return (
    <div className="page-container">
      <h2 className="page-title">Text Analysis Input</h2>
      
      <div className="input-section">
        <div className="file-upload-section">
          <div className="upload-area">
            <label htmlFor="file-input" className="upload-label">
              <div className="upload-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
              </div>
              <div>
                <strong>Click to upload</strong> or drag and drop
              </div>
              <div className="upload-formats">
                Supported formats: .txt, .csv, .docx
              </div>
              {fileName && <div className="file-name">Selected: {fileName}</div>}
            </label>
            <input
              id="file-input"
              type="file"
              accept=".txt,.csv,.docx"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
          </div>
        </div>

        <div className="divider">OR</div>

        <div className="text-input-section">
          <label htmlFor="text-area" className="input-label">
            Enter your text directly:
          </label>
          <textarea
            id="text-area"
            className="text-area"
            placeholder="Paste or type your text here for analysis... (e.g., articles, reports, social media content, customer feedback, etc.)"
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={15}
          />
          
          <div className="text-stats">
            <span>Characters: {text.length}</span>
            <span>Words: {text.trim() ? text.trim().split(/\s+/).length : 0}</span>
          </div>
        </div>

        <div className="button-group">
          <button 
            className="btn btn-primary" 
            onClick={handleAnalyze}
            disabled={loading || !text.trim()}
          >
            {loading ? 'Analyzing...' : '🔍 Analyze Text'}
          </button>
          <button 
            className="btn btn-secondary" 
            onClick={handleClear}
            disabled={loading}
          >
            Clear
          </button>
        </div>
      </div>

      <style>{`
        .input-section {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .file-upload-section {
          width: 100%;
        }

        .upload-area {
          border: 2px dashed #667eea;
          border-radius: 8px;
          padding: 2rem;
          text-align: center;
          background-color: #f7fafc;
          transition: all 0.3s ease;
        }

        .upload-area:hover {
          border-color: #764ba2;
          background-color: #edf2f7;
        }

        .upload-label {
          cursor: pointer;
          display: block;
          color: #2d3748;
        }

        .upload-icon {
          font-size: 3rem;
          margin-bottom: 1rem;
        }

        .upload-formats {
          font-size: 0.9rem;
          color: #718096;
          margin-top: 0.5rem;
        }

        .file-name {
          margin-top: 1rem;
          padding: 0.5rem 1rem;
          background-color: #667eea;
          color: white;
          border-radius: 5px;
          display: inline-block;
        }

        .divider {
          text-align: center;
          color: #718096;
          font-weight: 600;
          position: relative;
          padding: 1rem 0;
        }

        .divider::before,
        .divider::after {
          content: '';
          position: absolute;
          top: 50%;
          width: 45%;
          height: 1px;
          background-color: #e2e8f0;
        }

        .divider::before {
          left: 0;
        }

        .divider::after {
          right: 0;
        }

        .text-input-section {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .input-label {
          font-weight: 600;
          color: #2d3748;
          font-size: 1.1rem;
        }

        .text-area {
          width: 100%;
          padding: 1rem;
          border: 2px solid #e2e8f0;
          border-radius: 8px;
          font-size: 1rem;
          font-family: inherit;
          resize: vertical;
          transition: border-color 0.3s ease;
        }

        .text-area:focus {
          outline: none;
          border-color: #667eea;
        }

        .text-stats {
          display: flex;
          justify-content: space-between;
          color: #718096;
          font-size: 0.9rem;
        }

        .button-group {
          display: flex;
          gap: 1rem;
          justify-content: center;
        }

        .btn-secondary {
          background-color: #e2e8f0;
          color: #2d3748;
        }

        .btn-secondary:hover {
          background-color: #cbd5e0;
        }
      `}</style>
    </div>
  );
};

export default TextInput;
