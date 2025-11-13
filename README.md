# NarrativeNexus - Dynamic Text Analysis Platform

A professional full-stack application for advanced text analysis using React and Python Machine Learning.

## Features

- 📝 **Multiple Input Methods**: Upload files (.txt, .csv, .docx) or paste text directly
- 🔍 **Text Preprocessing**: Automatic cleaning, tokenization, and normalization
- 💭 **Sentiment Analysis**: Categorizes content as positive, negative, or neutral
- 🎯 **Topic Modeling**: Identifies key themes using TF-IDF algorithms
- 📊 **Interactive Visualizations**: Word clouds, sentiment charts, topic distributions
- 📄 **Comprehensive Reports**: Generate and export analysis reports in multiple formats
- 💡 **Actionable Insights**: AI-powered recommendations based on analysis

## Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm start
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

## Usage

1. **Input Text**: 
   - Upload a file (.txt, .csv, or .docx)
   - Or paste/type text directly into the text area

2. **Analyze**:
   - Click the "Analyze Text" button
   - Wait for processing to complete

3. **View Dashboard**:
   - See sentiment distribution
   - Explore key topics and themes
   - View word cloud visualization
   - Read actionable insights

4. **Generate Reports**:
   - Export analysis as TXT, JSON, or CSV
   - Share findings with stakeholders

## Technology Stack

- **Frontend**: React 18 + TypeScript
- **Routing**: React Router DOM
- **Charts**: Recharts
- **Word Cloud**: react-wordcloud
- **NLP**: Natural.js, Sentiment.js
- **File Processing**: Mammoth (DOCX), PapaParse (CSV)

## Project Structure

```
dynamic_live_text_platform/
├── public/
│   └── index.html
├── src/
│   ├── App.tsx                    # Main application component
│   ├── App.css                    # Global styles
│   ├── index.tsx                  # Entry point
│   ├── components/
│   │   ├── TextInput.tsx         # File upload & text input
│   │   ├── Dashboard.tsx         # Analysis visualization
│   │   └── Reports.tsx           # Report generation
│   └── services/
│       └── analysisService.ts    # Core analysis logic
├── package.json
├── tsconfig.json
└── README.md
```

## Key Features Explained

### Text Preprocessing
- Removes special characters
- Normalizes whitespace
- Converts to lowercase for analysis
- Tokenizes text into words and sentences

### Sentiment Analysis
- Uses sentiment.js library
- Provides overall sentiment score
- Calculates positive/negative/neutral distribution
- Categorizes content automatically

### Topic Modeling
- Implements TF-IDF algorithm
- Extracts top 10 most relevant topics
- Filters out short and common words
- Assigns weights to each topic

### Text Summarization
- Extractive summarization approach
- Scores sentences by keyword frequency
- Selects most representative sentences
- Generates concise summary (top 30% of content)

### Insights & Recommendations
- Automated insight generation
- Context-aware recommendations
- Actionable next steps
- Strategic guidance based on analysis

## Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build` folder.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Support

For issues or questions, please open an issue on the GitHub repository.

---

**NarrativeNexus** - Transforming text into actionable insights 
