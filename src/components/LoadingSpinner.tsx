import { Loader2 } from 'lucide-react';

export default function LoadingSpinner() {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl p-8 flex flex-col items-center space-y-4">
        <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            Analyzing Text
          </h3>
          <p className="text-sm text-gray-600">
            Processing your document with NLP algorithms...
          </p>
        </div>
      </div>
    </div>
  );
}
