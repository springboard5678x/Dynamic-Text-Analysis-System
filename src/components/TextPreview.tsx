import { FileText } from 'lucide-react';

interface TextPreviewProps {
  text: string;
}

export default function TextPreview({ text }: TextPreviewProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 h-full">
      <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <FileText className="w-5 h-5 mr-2 text-blue-600" />
        Text Preview
      </h2>

      <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto border border-gray-200">
        {text ? (
          <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
            {text}
          </p>
        ) : (
          <p className="text-sm text-gray-400 italic">
            No text loaded. Upload a file to see preview.
          </p>
        )}
      </div>

      {text && (
        <div className="mt-3 text-xs text-gray-500">
          {text.split(/\s+/).length} words • {text.length} characters
        </div>
      )}
    </div>
  );
}
