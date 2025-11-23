import { Tag } from 'lucide-react';
import { KeywordScore } from '../types';

interface KeywordsCardProps {
  keywords: KeywordScore[];
}

export default function KeywordsCard({ keywords }: KeywordsCardProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-base font-semibold text-gray-900 mb-4 flex items-center">
        <Tag className="w-5 h-5 mr-2 text-blue-600" />
        Key Terms
      </h3>

      <div className="space-y-3">
        {keywords.map((keyword, index) => (
          <div
            key={index}
            className="flex items-center justify-between bg-gray-50 rounded-lg p-3 border border-gray-200 hover:border-blue-300 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <div className="bg-blue-100 text-blue-600 rounded-full w-7 h-7 flex items-center justify-center text-xs font-bold">
                {index + 1}
              </div>
              <span className="font-medium text-gray-800 capitalize">
                {keyword.word}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-24 bg-gray-200 rounded-full h-1.5">
                <div
                  className="bg-gradient-to-r from-blue-500 to-purple-600 h-1.5 rounded-full transition-all"
                  style={{ width: `${(keyword.score / keywords[0].score) * 100}%` }}
                />
              </div>
              <span className="text-xs text-gray-500 font-semibold w-12 text-right">
                {keyword.score.toFixed(2)}
              </span>
            </div>
          </div>
        ))}
      </div>

      {keywords.length === 0 && (
        <p className="text-sm text-gray-400 italic text-center py-4">
          No keywords extracted yet
        </p>
      )}
    </div>
  );
}
