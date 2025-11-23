import { Upload, X } from 'lucide-react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
  onClear: () => void;
}

export default function FileUpload({ onFileSelect, selectedFile, onClear }: FileUploadProps) {
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const validTypes = ['text/plain', 'text/csv', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (validTypes.includes(file.type) || file.name.endsWith('.txt') || file.name.endsWith('.csv')) {
        onFileSelect(file);
      } else {
        alert('Please upload a .txt, .csv, or .docx file');
      }
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <Upload className="w-5 h-5 mr-2 text-blue-600" />
        Upload Document
      </h2>

      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
        <input
          type="file"
          id="file-upload"
          className="hidden"
          accept=".txt,.csv,.docx"
          onChange={handleFileChange}
        />
        <label
          htmlFor="file-upload"
          className="cursor-pointer flex flex-col items-center"
        >
          <Upload className="w-12 h-12 text-gray-400 mb-3" />
          <span className="text-sm font-medium text-gray-700 mb-1">
            Click to upload or drag and drop
          </span>
          <span className="text-xs text-gray-500">
            TXT, CSV, or DOCX files
          </span>
        </label>
      </div>

      {selectedFile && (
        <div className="mt-4 flex items-center justify-between bg-gray-50 rounded-lg p-3">
          <div className="flex items-center space-x-2">
            <Upload className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-medium text-gray-700">
              {selectedFile.name}
            </span>
            <span className="text-xs text-gray-500">
              ({(selectedFile.size / 1024).toFixed(2)} KB)
            </span>
          </div>
          <button
            onClick={onClear}
            className="text-gray-400 hover:text-red-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      )}
    </div>
  );
}
