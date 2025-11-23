import { FileText } from 'lucide-react';

export default function Header() {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center space-x-3">
          <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2.5 rounded-lg shadow-md">
            <FileText className="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">
              NarrativeNexus
            </h1>
            <p className="text-sm text-gray-600 mt-0.5">
              Dynamic Text Analysis Platform
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}
