import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TagCloud } from 'react-tagcloud';
import { AnalysisResult } from '../App';

interface DashboardProps {
  analysisResult: AnalysisResult | null;
}

const Dashboard: React.FC<DashboardProps> = ({ analysisResult }) => {
  if (!analysisResult) {
    return (
      <div className="page-container">
        <h2 className="page-title">Analysis Dashboard</h2>
        <div className="empty-state">
          <h3>No Analysis Data Available</h3>
          <p>Please go to the Text Analysis page and analyze some text first.</p>
        </div>
      </div>
    );
  }

  const { sentiment, topics, keywords, wordCount, sentenceCount, summary } = analysisResult;

  const sentimentData = [
    { name: 'Positive', value: sentiment.positive, color: '#10b981' },
    { name: 'Negative', value: sentiment.negative, color: '#ef4444' },
    { name: 'Neutral', value: sentiment.neutral, color: '#6b7280' }
  ].filter(item => item.value > 0);

  const topicData = topics.map(topic => ({
    name: topic.word,
    weight: topic.weight
  }));

  const wordCloudData = keywords.map(kw => ({
    value: kw.text,
    count: kw.value
  }));

  return (
    <div className="page-container">
      <h2 className="page-title">Analysis Dashboard</h2>

      {/* Summary Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
              <polyline points="10 9 9 9 8 9" />
            </svg>
          </div>
          <div className="stat-value">{wordCount}</div>
          <div className="stat-label">Total Words</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
            </svg>
          </div>
          <div className="stat-value">{sentenceCount}</div>
          <div className="stat-label">Sentences</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <path d="M8 14s1.5 2 4 2 4-2 4-2" />
              <line x1="9" y1="9" x2="9.01" y2="9" />
              <line x1="15" y1="9" x2="15.01" y2="9" />
            </svg>
          </div>
          <div className="stat-value">{sentiment.label}</div>
          <div className="stat-label">Overall Sentiment</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <circle cx="12" cy="12" r="6" />
              <circle cx="12" cy="12" r="2" />
            </svg>
          </div>
          <div className="stat-value">{topics.length}</div>
          <div className="stat-label">Key Topics</div>
        </div>
      </div>

      {/* Text Summary */}
      <div className="analysis-section">
        <h3 className="section-title">
          <span className="section-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 3h18v18H3zM12 8v8m-4-4h8" />
            </svg>
          </span>
          Text Summary
        </h3>
        <div className="summary-text">
          {summary}
        </div>
      </div>

      {/* Charts Grid */}
      <div className="charts-grid">
        {/* Sentiment Distribution */}
        <div className="analysis-section">
          <h3 className="section-title">
            <span className="section-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
              </svg>
            </span>
            Sentiment Distribution
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={sentimentData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {sentimentData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="sentiment-info">
            <div className={`sentiment-badge ${sentiment.label.toLowerCase()}`}>
              {sentiment.label} (Score: {sentiment.score})
            </div>
          </div>
        </div>

        {/* Topic Distribution */}
        <div className="analysis-section">
          <h3 className="section-title">
            <span className="section-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="20" x2="18" y2="10" />
                <line x1="12" y1="20" x2="12" y2="4" />
                <line x1="6" y1="20" x2="6" y2="14" />
              </svg>
            </span>
            Top Topics by Weight
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topicData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="weight" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Word Cloud */}
      <div className="analysis-section">
        <h3 className="section-title">
          <span className="section-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z" />
            </svg>
          </span>
          Keyword Cloud
        </h3>
        <div style={{ 
          minHeight: '350px', 
          padding: '2.5rem',
          background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          {keywords.length > 0 ? (
            <TagCloud
              minSize={24}
              maxSize={70}
              tags={wordCloudData}
              colorOptions={{
                luminosity: 'dark',
                hue: 'blue'
              }}
              shuffle={true}
              onClick={(tag: any) => console.log(`Keyword: ${tag.value}`)}
            />
          ) : (
            <p className="empty-state">No keywords found</p>
          )}
        </div>
      </div>

      {/* Insights & Recommendations */}
      <div className="analysis-section">
        <h3 className="section-title">
          <span className="section-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <path d="M12 16v-4M12 8h.01" />
            </svg>
          </span>
          Actionable Insights
        </h3>
        <ul className="insights-list">
          {sentiment.label === 'Negative' && (
            <li className="insight-item negative">
              <strong>Attention Required:</strong> The text shows negative sentiment. 
              Consider investigating the underlying issues or concerns raised.
            </li>
          )}
          {sentiment.label === 'Positive' && (
            <li className="insight-item positive">
              <strong>Positive Feedback:</strong> The content reflects positive sentiment. 
              This could be leveraged for testimonials or case studies.
            </li>
          )}
          {topics.length > 0 && (
            <li className="insight-item">
              🎯 <strong>Key Topics Identified:</strong> Focus on "{topics[0].word}" which appears 
              to be the dominant theme in your text.
            </li>
          )}
          {wordCount < 100 && (
            <li className="insight-item">
              📝 <strong>Short Text:</strong> Consider providing more content for deeper analysis 
              and more accurate insights.
            </li>
          )}
          {wordCount > 1000 && (
            <li className="insight-item">
              📚 <strong>Comprehensive Content:</strong> Your text is substantial, providing 
              rich data for detailed analysis.
            </li>
          )}
        </ul>
      </div>

      <style>{`
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1.5rem;
          margin-bottom: 2rem;
        }

        .stat-card {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          padding: 1.5rem;
          border-radius: 10px;
          text-align: center;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .stat-icon {
          font-size: 2.5rem;
          margin-bottom: 0.5rem;
        }

        .stat-value {
          font-size: 2rem;
          font-weight: bold;
          margin: 0.5rem 0;
        }

        .stat-label {
          font-size: 0.9rem;
          opacity: 0.9;
        }

        .summary-box {
          padding: 1.5rem;
          background-color: #f7fafc;
          border-left: 4px solid #667eea;
          border-radius: 5px;
          line-height: 1.6;
          color: #2d3748;
        }

        .charts-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
          gap: 1.5rem;
          margin: 1.5rem 0;
        }

        .sentiment-info {
          text-align: center;
          margin-top: 1rem;
        }

        .sentiment-badge {
          display: inline-block;
          padding: 0.5rem 1rem;
          border-radius: 20px;
          font-weight: 600;
          font-size: 1.1rem;
        }

        .sentiment-badge.positive {
          background-color: #c6f6d5;
          color: #22543d;
        }

        .sentiment-badge.negative {
          background-color: #fed7d7;
          color: #742a2a;
        }

        .sentiment-badge.neutral {
          background-color: #e2e8f0;
          color: #2d3748;
        }

        .insights-card {
          background: linear-gradient(to right, #f7fafc, #edf2f7);
        }

        .insights-list {
          list-style: none;
          padding: 0;
        }

        .insight-item {
          padding: 1rem;
          margin-bottom: 1rem;
          background: white;
          border-radius: 8px;
          border-left: 4px solid #667eea;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .insight-item.negative {
          border-left-color: #f56565;
        }

        .insight-item.positive {
          border-left-color: #48bb78;
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

export default Dashboard;
