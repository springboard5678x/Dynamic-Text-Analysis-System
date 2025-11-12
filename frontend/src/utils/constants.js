 
export const SUPPORTED_FILE_TYPES = [
  { extension: 'txt', name: 'Text File', accept: '.txt' },
  { extension: 'csv', name: 'CSV File', accept: '.csv' },
  { extension: 'docx', name: 'Word Document', accept: '.docx' },
];

export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export const ANALYSIS_STATUS = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  ERROR: 'error',
};

export const SENTIMENT_COLORS = {
  positive: '#48BB78',
  neutral: '#ED8936',
  negative: '#F56565',
};

export const CHART_COLORS = [
  '#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A8EAE',
  '#3E92CC', '#2A9D8F', '#E9C46A', '#F4A261', '#E76F51'
];