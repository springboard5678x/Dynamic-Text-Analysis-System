import { Lightbulb } from 'lucide-react';
import { Topic } from '../types';

interface TopicsCardProps {
  topics: Topic[];
}

export default function TopicsCard({ topics }: TopicsCardProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-base font-semibold text-gray-900 mb-4 flex items-center">
        <Lightbulb className="w-5 h-5 mr-2 text-blue-600" />
        Detected Topics
      </h3>

      <div className="space-y-4">
        {topics.map((topic, index) => (
          <div
            key={index}
            className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-4 border border-blue-200"
          >
            <div className="flex items-start space-x-3">
              <div className="bg-gradient-to-br from-blue-500 to-purple-600 text-white rounded-lg w-8 h-8 flex items-center justify-center text-sm font-bold flex-shrink-0 mt-0.5">
                {index + 1}
              </div>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900 mb-1">
                  {topic.topic}
                </h4>
                <p className="text-sm text-gray-600 mb-3">
                  {topic.description}
                </p>
                {topic.keywords.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {topic.keywords.map((keyword, kIndex) => (
                      <span
                        key={kIndex}
                        className="inline-block bg-white text-blue-700 text-xs font-medium px-2.5 py-1 rounded-full border border-blue-300"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {topics.length === 0 && (
        <p className="text-sm text-gray-400 italic text-center py-4">
          No topics detected yet
        </p>
      )}
    </div>
  );
}
