 import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  IconButton,
  TextField,
  InputAdornment,
  Dialog,
  DialogContent,
  CircularProgress,
  Alert,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Search as SearchIcon,
  Download as DownloadIcon,
  Visibility as ViewIcon,
  Analytics as AnalyticsIcon,
  Clear as ClearIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { analysisAPI } from '../../services/api';
import Visualization from '../../components/Visualization/Visualization';
import ReportViewer from '../../components/ReportViewer/ReportViewer';
import './History.css';

const History = () => {
  const [analyses, setAnalyses] = useState([]);
  const [filteredAnalyses, setFilteredAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [detailView, setDetailView] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  useEffect(() => {
    fetchAnalyses();
  }, []);

  useEffect(() => {
    filterAnalyses();
  }, [analyses, searchTerm]);

  const fetchAnalyses = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await analysisAPI.getAnalyses();
      setAnalyses(response.data);
    } catch (error) {
      console.error('Error fetching analyses:', error);
      setError('Failed to load analysis history. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const filterAnalyses = () => {
    if (!searchTerm.trim()) {
      setFilteredAnalyses(analyses);
      return;
    }

    const filtered = analyses.filter(analysis =>
      analysis.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      analysis.input_text?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      analysis.file_type?.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredAnalyses(filtered);
  };

  const handleViewAnalysis = (analysis) => {
    setSelectedAnalysis(analysis);
    setViewDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setViewDialogOpen(false);
    setSelectedAnalysis(null);
    setDetailView(false);
  };

  const handleClearSearch = () => {
    setSearchTerm('');
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive': return 'success';
      case 'negative': return 'error';
      case 'neutral': return 'warning';
      default: return 'default';
    }
  };

  const AnalysisCard = ({ analysis }) => (
    <Card 
      sx={{ 
        height: '100%',
        transition: 'all 0.3s ease',
        cursor: 'pointer',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: theme.shadows[8],
        },
      }}
      onClick={() => handleViewAnalysis(analysis)}
    >
      <CardContent sx={{ p: 3 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Typography 
            variant="h6" 
            fontWeight="600" 
            noWrap 
            sx={{ 
              maxWidth: isMobile ? '100%' : '70%',
              mb: 1,
            }}
          >
            {analysis.title}
          </Typography>
          <Chip
            label={analysis.file_type || 'Raw Text'}
            size="small"
            color="primary"
            variant="outlined"
          />
        </Box>

        {/* Metadata */}
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {new Date(analysis.created_at).toLocaleDateString()} • {analysis.topics_json?.length || 0} topics
        </Typography>

        {/* Sentiment Chips */}
        {analysis.sentiment_distribution && (
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
            <Chip
              label={`Positive: ${analysis.sentiment_distribution.distribution?.positive || 0}`}
              size="small"
              sx={{ backgroundColor: alpha('#48BB78', 0.1), color: '#48BB78' }}
            />
            <Chip
              label={`Neutral: ${analysis.sentiment_distribution.distribution?.neutral || 0}`}
              size="small"
              sx={{ backgroundColor: alpha('#ED8936', 0.1), color: '#ED8936' }}
            />
            <Chip
              label={`Negative: ${analysis.sentiment_distribution.distribution?.negative || 0}`}
              size="small"
              sx={{ backgroundColor: alpha('#F56565', 0.1), color: '#F56565' }}
            />
          </Box>
        )}

        {/* Overall Sentiment */}
        {analysis.sentiment_distribution && (
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Typography variant="body2" fontWeight="500" sx={{ mr: 1 }}>
              Overall:
            </Typography>
            <Chip
              label={analysis.sentiment_distribution.overall_sentiment?.toUpperCase() || 'N/A'}
              size="small"
              color={getSentimentColor(analysis.sentiment_distribution.overall_sentiment)}
              variant="filled"
            />
          </Box>
        )}

        {/* Preview Text */}
        {analysis.input_text && (
          <Typography 
            variant="body2" 
            color="text.secondary"
            sx={{
              display: '-webkit-box',
              WebkitLineClamp: 3,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
              lineHeight: 1.5,
            }}
          >
            {analysis.input_text.substring(0, 150)}
            {analysis.input_text.length > 150 && '...'}
          </Typography>
        )}

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', gap: 1, mt: 2, pt: 2, borderTop: `1px solid ${theme.palette.divider}` }}>
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              handleViewAnalysis(analysis);
            }}
            sx={{ color: 'primary.main' }}
          >
            <ViewIcon fontSize="small" />
          </IconButton>
          <Typography variant="body2" color="text.secondary" sx={{ flexGrow: 1 }}>
            View Details
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box className="history-page">
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <Typography
            variant="h3"
            fontWeight="bold"
            gutterBottom
            className="gradient-text"
          >
            Analysis History
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 600, mx: 'auto' }}>
            Review your previous text analyses and download comprehensive reports
          </Typography>
        </Box>

        {/* Search and Controls */}
        <Card sx={{ mb: 4 }}>
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
              <TextField
                placeholder="Search analyses..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon color="action" />
                    </InputAdornment>
                  ),
                  endAdornment: searchTerm && (
                    <InputAdornment position="end">
                      <IconButton size="small" onClick={handleClearSearch}>
                        <ClearIcon fontSize="small" />
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                sx={{ 
                  flexGrow: 1,
                  maxWidth: 400,
                }}
              />
              
              <Box sx={{ display: 'flex', gap: 1, ml: 'auto' }}>
                <Button
                  startIcon={<RefreshIcon />}
                  onClick={fetchAnalyses}
                  variant="outlined"
                >
                  Refresh
                </Button>
                <Typography variant="body2" color="text.secondary" sx={{ display: 'flex', alignItems: 'center' }}>
                  {filteredAnalyses.length} of {analyses.length} analyses
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        {/* Error Alert */}
        {error && (
          <Alert 
            severity="error" 
            sx={{ mb: 4 }}
            action={
              <Button color="inherit" size="small" onClick={fetchAnalyses}>
                Retry
              </Button>
            }
          >
            {error}
          </Alert>
        )}

        {/* Analyses Grid */}
        {filteredAnalyses.length > 0 ? (
          <Grid container spacing={3}>
            {filteredAnalyses.map((analysis) => (
              <Grid item xs={12} md={6} lg={4} key={analysis.id}>
                <AnalysisCard analysis={analysis} />
              </Grid>
            ))}
          </Grid>
        ) : (
          <Card>
            <CardContent sx={{ p: 6, textAlign: 'center' }}>
              <AnalyticsIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                No analyses found
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                {searchTerm ? 'Try adjusting your search terms' : 'Start by analyzing some text to see your history here'}
              </Typography>
              {!searchTerm && (
                <Button variant="contained" href="/analysis">
                  Analyze Text
                </Button>
              )}
            </CardContent>
          </Card>
        )}

        {/* Analysis Detail Dialog */}
        <Dialog
          open={viewDialogOpen}
          onClose={handleCloseDialog}
          maxWidth="lg"
          fullWidth
          fullScreen={isMobile}
        >
          {selectedAnalysis && (
            <>
              <Box sx={{ p: 3, borderBottom: `1px solid ${theme.palette.divider}` }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 2 }}>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h5" fontWeight="bold" gutterBottom>
                      {selectedAnalysis.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Analyzed on {new Date(selectedAnalysis.created_at).toLocaleString()}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Button
                      variant={detailView ? "outlined" : "contained"}
                      onClick={() => setDetailView(false)}
                      size="small"
                    >
                      Overview
                    </Button>
                    <Button
                      variant={detailView ? "contained" : "outlined"}
                      onClick={() => setDetailView(true)}
                      size="small"
                    >
                      Full Report
                    </Button>
                  </Box>
                </Box>
              </Box>

              <DialogContent sx={{ p: 0 }}>
                {detailView ? (
                  <ReportViewer analysisData={selectedAnalysis} />
                ) : (
                  <Box sx={{ p: 3 }}>
                    <Visualization analysisData={selectedAnalysis} />
                  </Box>
                )}
              </DialogContent>
            </>
          )}
        </Dialog>
      </Container>
    </Box>
  );
};

// Add missing alpha function
const alpha = (color, opacity) => {
  return color + Math.round(opacity * 255).toString(16).padStart(2, '0');
};

export default History;
