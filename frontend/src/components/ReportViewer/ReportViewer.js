 import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  CircularProgress,
  useTheme,
  Dialog,
  DialogContent,
  IconButton,
} from '@mui/material';
import {
  Download as DownloadIcon,
  PictureAsPdf as PdfIcon,
  Close as CloseIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';
import { analysisAPI } from '../../services/api';
import './ReportViewer.css';

const ReportViewer = ({ analysisData }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pdfUrl, setPdfUrl] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const theme = useTheme();

  const handleDownloadReport = async () => {
    if (!analysisData?.id) {
      setError('No analysis data available for download');
      return;
    }

    try {
      setLoading(true);
      setError('');

      const response = await analysisAPI.downloadReport(analysisData.id);
      
      // Create blob URL for download
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      
      // Create download link
      const link = document.createElement('a');
      link.href = url;
      link.download = `NarrativeNexus_Report_${analysisData.id}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Clean up URL
      window.URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('Download error:', error);
      setError('Failed to download report. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleViewReport = async () => {
    if (!analysisData?.id) {
      setError('No analysis data available for viewing');
      return;
    }

    try {
      setLoading(true);
      setError('');

      const response = await analysisAPI.downloadReport(analysisData.id);
      
      // Create blob URL for viewing
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      setPdfUrl(url);
      setDialogOpen(true);
      
    } catch (error) {
      console.error('View report error:', error);
      setError('Failed to load report for viewing. Please try downloading instead.');
    } finally {
      setLoading(false);
    }
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    if (pdfUrl) {
      window.URL.revokeObjectURL(pdfUrl);
      setPdfUrl(null);
    }
  };

  const ReportSection = ({ title, children, icon }) => (
    <Box sx={{ mb: 4 }}>
      <Typography 
        variant="h6" 
        fontWeight="600" 
        gutterBottom
        sx={{ 
          display: 'flex', 
          alignItems: 'center',
          color: 'primary.main',
        }}
      >
        {icon} {title}
      </Typography>
      {children}
    </Box>
  );

  return (
    <Box className="report-viewer-component">
      {/* Action Buttons */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
            <Button
              variant="contained"
              startIcon={<DownloadIcon />}
              onClick={handleDownloadReport}
              disabled={loading}
              sx={{
                borderRadius: 3,
                px: 3,
                py: 1,
                fontWeight: 600,
              }}
            >
              {loading ? 'Downloading...' : 'Download PDF Report'}
            </Button>
            
            <Button
              variant="outlined"
              startIcon={<ViewIcon />}
              onClick={handleViewReport}
              disabled={loading}
              sx={{
                borderRadius: 3,
                px: 3,
                py: 1,
                fontWeight: 600,
              }}
            >
              View in Browser
            </Button>
            
            <Box sx={{ display: 'flex', alignItems: 'center', ml: 'auto' }}>
              <PdfIcon sx={{ color: 'error.main', mr: 1 }} />
              <Typography variant="body2" color="text.secondary">
                Comprehensive analysis report
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Report Preview */}
      <Card>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h4" fontWeight="bold" gutterBottom align="center" color="primary">
            NarrativeNexus Analysis Report
          </Typography>
          
          <Typography variant="h6" gutterBottom align="center" color="text.secondary">
            {analysisData?.title || 'Text Analysis Report'}
          </Typography>
          
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 4 }}>
            Generated on {analysisData ? new Date(analysisData.created_at).toLocaleDateString() : new Date().toLocaleDateString()}
          </Typography>

          <Box sx={{ borderTop: `2px solid ${theme.palette.divider}`, pt: 3 }}>
            {/* Executive Summary */}
            <ReportSection title="Executive Summary" icon="📊">
              <Typography variant="body1" paragraph>
                This report provides a comprehensive analysis of the submitted text content, 
                including topic modeling, sentiment analysis, and actionable insights.
              </Typography>
              {analysisData?.sentiment_distribution && (
                <Box sx={{ p: 2, backgroundColor: 'background.default', borderRadius: 2 }}>
                  <Typography variant="body2" fontWeight="500">
                    Overall Sentiment: {' '}
                    <Typography 
                      component="span" 
                      fontWeight="600"
                      sx={{
                        color: 
                          analysisData.sentiment_distribution.overall_sentiment === 'positive' ? 'success.main' :
                          analysisData.sentiment_distribution.overall_sentiment === 'negative' ? 'error.main' : 'warning.main'
                      }}
                    >
                      {analysisData.sentiment_distribution.overall_sentiment?.toUpperCase()}
                    </Typography>
                  </Typography>
                  <Typography variant="body2">
                    Topics Identified: {analysisData.topics_json?.length || 0}
                  </Typography>
                </Box>
              )}
            </ReportSection>

            {/* Key Topics */}
            {analysisData?.topics_json && analysisData.topics_json.length > 0 && (
              <ReportSection title="Key Topics Identified" icon="🔍">
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {analysisData.topics_json.map((topic, index) => (
                    <Box
                      key={topic.topic_id}
                      sx={{
                        p: 2,
                        border: `1px solid ${theme.palette.divider}`,
                        borderRadius: 2,
                        flex: '1 1 calc(33.333% - 8px)',
                        minWidth: 200,
                        backgroundColor: 'background.default',
                      }}
                    >
                      <Typography variant="subtitle2" fontWeight="600" gutterBottom>
                        Topic {topic.topic_id}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {topic.words.slice(0, 5).join(', ')}
                        {topic.words.length > 5 && '...'}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </ReportSection>
            )}

            {/* Sentiment Analysis */}
            {analysisData?.sentiment_distribution && (
              <ReportSection title="Sentiment Analysis" icon="😊">
                <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
                  {Object.entries(analysisData.sentiment_distribution.distribution || {}).map(([key, value]) => (
                    <Box key={key} sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" fontWeight="bold" color="primary">
                        {value}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" textTransform="capitalize">
                        {key} Sentences
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </ReportSection>
            )}

            {/* Actionable Insights */}
            {analysisData?.actionable_insights && analysisData.actionable_insights.length > 0 && (
              <ReportSection title="Actionable Insights" icon="💡">
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {analysisData.actionable_insights.map((insight, index) => (
                    <Box
                      key={index}
                      sx={{
                        p: 2,
                        borderLeft: `4px solid ${theme.palette.primary.main}`,
                        backgroundColor: 'background.default',
                        borderRadius: '0 8px 8px 0',
                      }}
                    >
                      <Typography variant="subtitle1" fontWeight="600" gutterBottom>
                        {insight.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" paragraph>
                        {insight.description}
                      </Typography>
                      <Typography variant="body2" fontWeight="500" color="primary">
                        Recommendation: {insight.recommendation}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </ReportSection>
            )}

            {/* Summaries */}
            <ReportSection title="Text Summarization" icon="📝">
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                {analysisData?.extractive_summary && (
                  <Box>
                    <Typography variant="subtitle1" fontWeight="600" gutterBottom>
                      Extractive Summary
                    </Typography>
                    <Typography variant="body2" paragraph>
                      {analysisData.extractive_summary}
                    </Typography>
                  </Box>
                )}
                
                {analysisData?.abstractive_summary && (
                  <Box>
                    <Typography variant="subtitle1" fontWeight="600" gutterBottom>
                      Abstractive Summary
                    </Typography>
                    <Typography variant="body2">
                      {analysisData.abstractive_summary}
                    </Typography>
                  </Box>
                )}
              </Box>
            </ReportSection>

            {/* Technical Details */}
            <ReportSection title="Technical Details" icon="⚙️">
              <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
                <Box>
                  <Typography variant="body2" fontWeight="500">Analysis Method</Typography>
                  <Typography variant="body2" color="text.secondary">LDA Topic Modeling</Typography>
                </Box>
                <Box>
                  <Typography variant="body2" fontWeight="500">Sentiment Analysis</Typography>
                  <Typography variant="body2" color="text.secondary">TextBlob with Pattern Analysis</Typography>
                </Box>
                <Box>
                  <Typography variant="body2" fontWeight="500">File Type</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {analysisData?.file_type ? analysisData.file_type.toUpperCase() : 'Raw Text'}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" fontWeight="500">Report Version</Typography>
                  <Typography variant="body2" color="text.secondary">1.0</Typography>
                </Box>
              </Box>
            </ReportSection>
          </Box>
        </CardContent>
      </Card>

      {/* PDF Viewer Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        maxWidth="lg"
        fullWidth
        fullScreen={window.innerWidth < 768}
      >
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6" fontWeight="600">
            PDF Report Viewer
          </Typography>
          <IconButton onClick={handleCloseDialog}>
            <CloseIcon />
          </IconButton>
        </Box>
        
        <DialogContent sx={{ p: 0, height: '80vh' }}>
          {pdfUrl ? (
            <iframe
              src={pdfUrl}
              width="100%"
              height="100%"
              style={{ border: 'none' }}
              title="PDF Report"
            />
          ) : (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
              <CircularProgress />
            </Box>
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default ReportViewer;
