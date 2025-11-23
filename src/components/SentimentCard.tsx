import { Smile, Frown, Minus } from 'lucide-react';

interface SentimentCardProps {
  sentiment: 'Positive' | 'Negative' | 'Neutral';
  score: number;
}

export default function SentimentCard({ sentiment, score }: SentimentCardProps) {
  const getSentimentConfig = () => {
    switch (sentiment) {
      case 'Positive':
        return {
          icon: Smile,
          color: 'text-green-600',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          label: 'Positive Sentiment',
        };
      case 'Negative':
        return {
          icon: Frown,
          color: 'text-red-600',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          label: 'Negative Sentiment',
        };
      case 'Neutral':
        return {
          icon: Minus,
          color: 'text-yellow-600',
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          label: 'Neutral Sentiment',
        };
    }
  };

  const config = getSentimentConfig();
  const Icon = config.icon;

  return (
    <div className={`bg-white rounded-xl shadow-sm border ${config.borderColor} p-6`}>
      <h3 className="text-base font-semibold text-gray-900 mb-4">
        Sentiment Analysis
      </h3>

      <div className={`${config.bgColor} rounded-lg p-5 border ${config.borderColor}`}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-3">
            <Icon className={`w-8 h-8 ${config.color}`} />
            <div>
              <div className={`text-2xl font-bold ${config.color}`}>
                {sentiment}
              </div>
              <div className="text-xs text-gray-600 mt-0.5">
                Overall Sentiment
              </div>
            </div>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs font-medium text-gray-600">
              Confidence Score
            </span>
            <span className={`text-xs font-semibold ${config.color}`}>
              {Math.abs(score * 100).toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${
                sentiment === 'Positive'
                  ? 'bg-green-500'
                  : sentiment === 'Negative'
                  ? 'bg-red-500'
                  : 'bg-yellow-500'
              }`}
              style={{ width: `${Math.abs(score * 100)}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
