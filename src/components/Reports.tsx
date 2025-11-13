import React from 'react';
import { AnalysisResult } from '../App';

interface ReportsProps {
  analysisResult: AnalysisResult | null;
}

const Reports: React.FC<ReportsProps> = ({ analysisResult }) => {
  if (!analysisResult) {
    return (
      <div className="page-container">
        <h2 className="page-title">Analysis Reports</h2>
        <div className="empty-state">
          <h3>No Analysis Data Available</h3>
          <p>Please go to the Text Analysis page and analyze some text first.</p>
        </div>
      </div>
    );
  }

  const { sentiment, topics, summary, wordCount, sentenceCount, keywords } = analysisResult;

  const generateReport = () => {
    const reportContent = `
===========================================
NARRATIVENEXUS - TEXT ANALYSIS REPORT
===========================================
Generated on: ${new Date().toLocaleString()}

-------------------------------------------
1. DOCUMENT STATISTICS
-------------------------------------------
Total Words: ${wordCount}
Total Sentences: ${sentenceCount}
Keywords Identified: ${keywords.length}

-------------------------------------------
2. SENTIMENT ANALYSIS
-------------------------------------------
Overall Sentiment: ${sentiment.label}
Sentiment Score: ${sentiment.score}
Distribution:
  - Positive: ${sentiment.positive}%
  - Negative: ${sentiment.negative}%
  - Neutral: ${sentiment.neutral}%

-------------------------------------------
3. KEY TOPICS
-------------------------------------------
${topics.map((topic, idx) => `${idx + 1}. ${topic.word} (Weight: ${topic.weight})`).join('\n')}

-------------------------------------------
4. TEXT SUMMARY
-------------------------------------------
${summary}

-------------------------------------------
5. TOP KEYWORDS
-------------------------------------------
${keywords.slice(0, 10).map((kw, idx) => `${idx + 1}. ${kw.text} (${kw.value} occurrences)`).join('\n')}

-------------------------------------------
6. RECOMMENDATIONS
-------------------------------------------
${generateRecommendations(sentiment, wordCount, topics)}

===========================================
END OF REPORT
===========================================
    `.trim();

    const blob = new Blob([reportContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `NarrativeNexus_Report_${Date.now()}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const exportJSON = () => {
    const jsonData = JSON.stringify(analysisResult, null, 2);
    const blob = new Blob([jsonData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `NarrativeNexus_Data_${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const exportCSV = () => {
    const csvContent = [
      ['Metric', 'Value'],
      ['Word Count', wordCount],
      ['Sentence Count', sentenceCount],
      ['Sentiment', sentiment.label],
      ['Sentiment Score', sentiment.score],
      ['Positive %', sentiment.positive],
      ['Negative %', sentiment.negative],
      ['Neutral %', sentiment.neutral],
      [''],
      ['Top Keywords', 'Frequency'],
      ...keywords.slice(0, 15).map(kw => [kw.text, kw.value]),
      [''],
      ['Topics', 'Weight'],
      ...topics.map(t => [t.word, t.weight])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `NarrativeNexus_Data_${Date.now()}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="page-container">
      <h2 className="page-title">Analysis Reports</h2>

      {/* Export Options */}
      <div className="export-section">
        <h3>Export Options</h3>
        <p style={{ marginBottom: '1.5rem', color: '#6b7280' }}>
          Download your analysis results in various formats
        </p>
        <div className="export-buttons">
          <button className="btn btn-export" onClick={generateReport}>
            Download Full Report (.txt)
          </button>
          <button className="btn btn-export" onClick={exportJSON}>
            Export as JSON
          </button>
          <button className="btn btn-export" onClick={exportCSV}>
            Export as CSV
          </button>
        </div>
      </div>

      {/* Report Preview */}
      <div className="report-preview">
        <h3 style={{ fontSize: '1.5rem', marginBottom: '2rem', color: '#111827', fontWeight: 700 }}>Report Preview</h3>
        
        <div className="report-section">
          <h4>Document Statistics</h4>
          <div className="metrics-grid">
            <div className="metric-item">
              <div className="metric-label">Total Words</div>
              <div className="metric-value">{wordCount}</div>
            </div>
            <div className="metric-item">
              <div className="metric-label">Total Sentences</div>
              <div className="metric-value">{sentenceCount}</div>
            </div>
            <div className="metric-item">
              <div className="metric-label">Keywords Identified</div>
              <div className="metric-value">{keywords.length}</div>
            </div>
          </div>
        </div>

        <div className="report-section">
          <h4>Sentiment Analysis</h4>
          <div className="metrics-grid">
            <div className="metric-item">
              <div className="metric-label">Overall Sentiment</div>
              <div className={`metric-value sentiment-${sentiment.label.toLowerCase()}`}>{sentiment.label}</div>
            </div>
            <div className="metric-item">
              <div className="metric-label">Sentiment Score</div>
              <div className="metric-value">{sentiment.score}</div>
            </div>
            <div className="metric-item">
              <div className="metric-label">Positive</div>
              <div className="metric-value">{sentiment.positive}%</div>
            </div>
            <div className="metric-item">
              <div className="metric-label">Negative</div>
              <div className="metric-value">{sentiment.negative}%</div>
            </div>
            <div className="metric-item">
              <div className="metric-label">Neutral</div>
              <div className="metric-value">{sentiment.neutral}%</div>
            </div>
          </div>
        </div>

        <div className="report-section">
          <h4>Key Topics</h4>
          <ol style={{ paddingLeft: '1.5rem' }}>
            {topics.map((topic, idx) => (
              <li key={idx} style={{ marginBottom: '0.5rem' }}>
                <strong>{topic.word}</strong> (Weight: {topic.weight})
              </li>
            ))}
          </ol>
        </div>

        <div className="report-section">
          <h4>Summary</h4>
          <div className="summary-text">
            {summary}
          </div>
        </div>

        <div className="report-section">
          <h4>Top Keywords</h4>
          <div className="keywords-list">
            {keywords.slice(0, 15).map((kw, idx) => (
              <span key={idx} className="keyword-tag">
                {kw.text} ({kw.value})
              </span>
            ))}
          </div>
        </div>

        <div className="report-section recommendations">
          <h4>💡 Recommendations</h4>
          <div className="recommendations-box">
            {generateRecommendations(sentiment, wordCount, topics)}
          </div>
        </div>
      </div>

      <style>{`
        .export-buttons {
          display: flex;
          gap: 1rem;
          flex-wrap: wrap;
        }

        .report-section {
          margin: 2rem 0;
          padding: 1.5rem;
          background-color: #f7fafc;
          border-radius: 8px;
          border-left: 4px solid #667eea;
        }

        .report-section h4 {
          color: #2d3748;
          margin-bottom: 1rem;
          font-size: 1.2rem;
        }

        .report-section ul,
        .report-section ol {
          line-height: 1.8;
          color: #4a5568;
        }

        .report-section li {
          margin: 0.5rem 0;
        }

        .sentiment-positive {
          color: #22543d;
          background-color: #c6f6d5;
          padding: 0.2rem 0.5rem;
          border-radius: 4px;
        }

        .sentiment-negative {
          color: #742a2a;
          background-color: #fed7d7;
          padding: 0.2rem 0.5rem;
          border-radius: 4px;
        }

        .sentiment-neutral {
          color: #2d3748;
          background-color: #e2e8f0;
          padding: 0.2rem 0.5rem;
          border-radius: 4px;
        }

        .summary-preview {
          padding: 1rem;
          background-color: white;
          border-radius: 5px;
          line-height: 1.6;
          color: #2d3748;
        }

        .keywords-grid {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }

        .keyword-tag {
          display: inline-block;
          padding: 0.5rem 1rem;
          background-color: #667eea;
          color: white;
          border-radius: 20px;
          font-size: 0.9rem;
        }

        .recommendations {
          background: linear-gradient(to right, #fef5e7, #fdebd0);
          border-left-color: #f59e0b;
        }

        .recommendations-box {
          padding: 1rem;
          background-color: white;
          border-radius: 5px;
          line-height: 1.8;
          white-space: pre-line;
        }

        .no-data {
          text-align: center;
          padding: 3rem;
          color: #718096;
          font-size: 1.1rem;
        }

        .no-data p {
          margin: 0.5rem 0;
        }
      `}</style>
    </div>
  );
};

function generateRecommendations(
  sentiment: { label: string; score: number },
  wordCount: number,
  topics: Array<{ word: string; weight: number }>
): string {
  const recommendations: string[] = [];

  if (sentiment.label === 'Negative') {
    recommendations.push(
      '⚠️ NEGATIVE SENTIMENT DETECTED:\n' +
      '   - Investigate underlying issues or concerns\n' +
      '   - Consider follow-up analysis on specific pain points\n' +
      '   - Develop action plan to address negative feedback'
    );
  } else if (sentiment.label === 'Positive') {
    recommendations.push(
      '✅ POSITIVE SENTIMENT IDENTIFIED:\n' +
      '   - Leverage this content for marketing materials\n' +
      '   - Consider featuring as testimonial or case study\n' +
      '   - Amplify positive aspects in future communications'
    );
  }

  if (topics.length > 0) {
    recommendations.push(
      `🎯 KEY THEME FOCUS:\n` +
      `   - Primary topic "${topics[0].word}" should be central to strategy\n` +
      `   - Create content that expands on this theme\n` +
      `   - Monitor related topics for trends`
    );
  }

  if (wordCount < 100) {
    recommendations.push(
      '📝 CONTENT LENGTH:\n' +
      '   - Current text is brief - consider expanding for deeper insights\n' +
      '   - Gather more data for comprehensive analysis\n' +
      '   - Short content may limit analysis accuracy'
    );
  } else if (wordCount > 1000) {
    recommendations.push(
      '📚 COMPREHENSIVE CONTENT:\n' +
      '   - Rich data available for detailed analysis\n' +
      '   - Consider breaking into segments for targeted insights\n' +
      '   - Good foundation for trend analysis'
    );
  }

  recommendations.push(
    '🔄 NEXT STEPS:\n' +
    '   - Share findings with relevant stakeholders\n' +
    '   - Schedule follow-up analysis to track changes\n' +
    '   - Implement actionable insights from this report'
  );

  return recommendations.join('\n\n');
}

export default Reports;
