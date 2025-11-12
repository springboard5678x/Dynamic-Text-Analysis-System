import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  Alert,
} from '@mui/material';
import {
  Clear as ClearIcon,
  Analytics as AnalyticsIcon,
  ContentCopy as CopyIcon,
} from '@mui/icons-material';
import './TextInput.css';

const TextInput = ({ onSubmit, loading }) => {
  const [text, setText] = useState('');
  const [title, setTitle] = useState('');
  const [charCount, setCharCount] = useState(0);
  const [error, setError] = useState('');

  const sampleTexts = [
    {
      title: "Customer Feedback",
      content: "The product quality is excellent and delivery was faster than expected. However, the customer support could be more responsive. Overall, I'm satisfied with my purchase and would recommend it to others."
    },
    {
      title: "Business Report", 
      content: "Quarterly performance shows significant growth in key metrics. Revenue increased by 15% compared to last quarter, while customer satisfaction scores improved by 8%. Market expansion initiatives are showing promising early results."
    },
    {
      title: "Product Review",
      content: "This application has revolutionized how we manage our workflow. The user interface is intuitive and the features are comprehensive. The only drawback is the occasional slow performance during peak hours."
    }
  ];

  const handleTextChange = (event) => {
    const newText = event.target.value;
    setText(newText);
    setCharCount(newText.length);
    
    if (newText.length < 50 && newText.length > 0) {
      setError('Text should be at least 50 characters for meaningful analysis');
    } else {
      setError('');
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!title.trim()) {
      setError('Please enter a title for your analysis');
      return;
    }
    
    if (text.length < 50) {
      setError('Text should be at least 50 characters long');
      return;
    }

    onSubmit({
      title: title.trim(),
      input_text: text.trim(),
    });
  };

  const handleClear = () => {
    setText('');
    setTitle('');
    setCharCount(0);
    setError('');
  };

  const handleUseSample = (sample) => {
    setTitle(sample.title);
    setText(sample.content);
    setCharCount(sample.content.length);
    setError('');
  };

  const handleCopyText = () => {
    navigator.clipboard.writeText(text);
  };

  const handlePaste = async () => {
    try {
      const clipboardText = await navigator.clipboard.readText();
      setText(clipboardText);
      setCharCount(clipboardText.length);
    } catch (error) {
      console.error('Failed to read clipboard:', error);
    }
  };

  return (
    <Box className="text-input-component">
      <form onSubmit={handleSubmit}>
        {/* Title Input */}
        <TextField
          fullWidth
          label="Analysis Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g., Customer Feedback Analysis Q4 2024"
          sx={{ mb: 3 }}
          required
          disabled={loading}
        />

        {/* Text Input Area */}
        <Box sx={{ position: 'relative', mb: 2 }}>
          <TextField
            fullWidth
            multiline
            rows={12}
            label="Enter your text here"
            value={text}
            onChange={handleTextChange}
            placeholder="Paste or type your text content here (minimum 50 characters)..."
            disabled={loading}
            sx={{
              '& .MuiOutlinedInput-root': {
                fontFamily: 'monospace',
                fontSize: '0.9rem',
                lineHeight: 1.5,
              },
            }}
          />
          
          {/* Text Actions */}
          {text && (
            <Box sx={{ position: 'absolute', top: 8, right: 8, display: 'flex', gap: 1 }}>
              <Tooltip title="Copy text">
                <IconButton size="small" onClick={handleCopyText} disabled={loading}>
                  <CopyIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Clear text">
                <IconButton size="small" onClick={handleClear} disabled={loading}>
                  <ClearIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          )}
        </Box>

        {/* Character Count & Error */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography 
            variant="body2" 
            color={charCount < 50 ? 'error' : 'text.secondary'}
          >
            {charCount} characters {charCount < 50 && '(minimum 50 required)'}
          </Typography>
          
          <Button 
            variant="text" 
            size="small" 
            onClick={handlePaste}
            disabled={loading}
          >
            Paste from clipboard
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Sample Texts */}
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent sx={{ p: 2 }}>
            <Typography variant="body2" fontWeight="500" color="text.secondary" gutterBottom>
              💡 Try sample texts:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {sampleTexts.map((sample, index) => (
                <Button
                  key={index}
                  variant="outlined"
                  size="small"
                  onClick={() => handleUseSample(sample)}
                  disabled={loading}
                  sx={{ borderRadius: 2, textTransform: 'none' }}
                >
                  {sample.title}
                </Button>
              ))}
            </Box>
          </CardContent>
        </Card>

        {/* Submit Button */}
        <Button
          type="submit"
          variant="contained"
          size="large"
          disabled={loading || !text.trim() || text.length < 50 || !title.trim()}
          startIcon={<AnalyticsIcon />}
          fullWidth
          sx={{
            py: 1.5,
            fontSize: '1.1rem',
            fontWeight: 600,
            borderRadius: 3,
          }}
        >
          {loading ? 'Analyzing...' : 'Start Analysis'}
        </Button>

        {/* Analysis Tips */}
        <Box sx={{ mt: 3, p: 2, backgroundColor: 'background.default', borderRadius: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            💡 Analysis Tips:
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
            • Longer texts (200+ words) generate more detailed topics<br/>
            • Clear, well-structured content produces better insights<br/>
            • Mixed sentiment texts provide balanced analysis
          </Typography>
        </Box>
      </form>
    </Box>
  );
};

export default TextInput;