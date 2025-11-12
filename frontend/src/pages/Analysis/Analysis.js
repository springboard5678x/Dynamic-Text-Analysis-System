import React, { useState, useRef } from 'react';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Stepper,
  Step,
  StepLabel,
  Alert,
  CircularProgress,
  useTheme,
  useMediaQuery,
  Tabs,
  Tab,
  Paper,
  alpha as muiAlpha,
} from '@mui/material';
import {
  Upload as UploadIcon,
  Analytics as AnalyticsIcon,
  Description as DescriptionIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { analysisAPI } from '../../services/api';
import FileUpload from '../../components/FileUpload/FileUpload';
import TextInput from '../../components/TextInput/TextInput';
import Visualization from '../../components/Visualization/Visualization';
import ReportViewer from '../../components/ReportViewer/ReportViewer';
import './Analysis.css';

const Analysis = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [activeTab, setActiveTab] = useState(0);
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pollingCount, setPollingCount] = useState(0);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const currentAnalysisIdRef = useRef(null);
  const pollingIntervalRef = useRef(null);

  const steps = [
    { label: 'Input Text', icon: <UploadIcon /> },
    { label: 'Analysis', icon: <AnalyticsIcon /> },
    { label: 'Results', icon: <DescriptionIcon /> },
  ];

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleAnalysisSubmit = async (data) => {
    try {
      setLoading(true);
      setError('');
      setAnalysisData(null);
      setPollingCount(0);
      currentAnalysisIdRef.current = null;
      
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
      
      console.log('🚀 Starting new analysis...');
      
      const response = await analysisAPI.createAnalysis(data);
      
      // ✅ Store the analysis ID for polling
      const analysisId = response.data.id;
      currentAnalysisIdRef.current = analysisId;
      
      // ✅ Set initial data with status
      setAnalysisData({
        ...response.data,
        status: 'processing'
      });
      
      setActiveStep(1);
      
      // ✅ Start polling for results
      startPolling(analysisId);
      
    } catch (error) {
      console.error('❌ Analysis error:', error);
      setError(error.response?.data?.error || 'Failed to analyze text. Please try again.');
      setLoading(false);
    }
  };

  const startPolling = (analysisId) => {
    let count = 0;
    pollingIntervalRef.current = setInterval(async () => {
      try {
        count++;
        setPollingCount(count);
        
        const statusResponse = await analysisAPI.getAnalysisStatus(analysisId);
        console.log(`📊 Polling attempt ${count}:`, statusResponse.data);
        
        if (statusResponse.data.status === 'complete') {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
          
          console.log('✅ Analysis completed! Fetching full data...');
          
          // ✅ Get complete analysis data
          const completeResponse = await analysisAPI.getAnalysis(analysisId);
          console.log('📄 Full analysis data:', completeResponse.data);
          
          setAnalysisData(completeResponse.data);
          setActiveStep(2);
          setLoading(false);
          console.log('🎉 Moving to results step!');
        } else if (count > 60) { // 120 seconds timeout (60 * 2 seconds)
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
          console.warn('⏰ Polling timeout reached');
          setError('Analysis is taking longer than expected. Please check back later.');
          setLoading(false);
        } else {
          console.log(`🔄 Still processing... (${count}/60 attempts)`);
        }
      } catch (error) {
        console.error('❌ Polling error:', error);
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
        setError('Failed to get analysis results. Please try again.');
        setLoading(false);
      }
    }, 2000); // Poll every 2 seconds
  };

  const handleNewAnalysis = () => {
    // Clear any polling intervals
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
    
    setActiveStep(0);
    setAnalysisData(null);
    setError('');
    setActiveTab(0);
    setPollingCount(0);
    currentAnalysisIdRef.current = null;
  };

  React.useEffect(() => {
    // Cleanup polling on component unmount
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={4}>
            <Grid item xs={12} lg={6}>
              <Card sx={{ height: '100%' }}>
                <CardContent sx={{ p: 4 }}>
                  <Typography variant="h5" fontWeight="600" gutterBottom color="primary">
                    📝 Text Input
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    Paste your text directly into the editor. Perfect for quick analysis of articles, reviews, or any text content.
                  </Typography>
                  <TextInput onSubmit={handleAnalysisSubmit} loading={loading} />
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} lg={6}>
              <Card sx={{ height: '100%' }}>
                <CardContent sx={{ p: 4 }}>
                  <Typography variant="h5" fontWeight="600" gutterBottom color="secondary">
                    📁 File Upload
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    Upload documents for analysis. Supports TXT, CSV, and DOCX files up to 10MB.
                  </Typography>
                  <FileUpload onSubmit={handleAnalysisSubmit} loading={loading} />
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        );

      case 1:
        return (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <CircularProgress 
              size={80} 
              thickness={4}
              sx={{ 
                color: theme.palette.primary.main,
                mb: 4,
              }} 
            />
            <Typography variant="h4" fontWeight="600" gutterBottom color="primary">
              Analyzing Your Content
            </Typography>
            <Typography variant="h6" color="text.secondary" sx={{ mb: 4 }}>
              Our AI is processing your text to extract insights...
              <br />
              <Typography variant="body2" sx={{ mt: 1 }}>
                Polling for results... ({pollingCount * 2}s elapsed)
              </Typography>
            </Typography>
            
            <Grid container spacing={3} sx={{ maxWidth: 600, mx: 'auto', mt: 4 }}>
              <Grid item xs={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Box
                    sx={{
                      width: 60,
                      height: 60,
                      borderRadius: '50%',
                      backgroundColor: theme.palette.primary.main,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mx: 'auto',
                      mb: 2,
                    }}
                  >
                    <CheckCircleIcon sx={{ color: 'white', fontSize: 30 }} />
                  </Box>
                  <Typography variant="body2" fontWeight="500">
                    Text Processing
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Box
                    sx={{
                      width: 60,
                      height: 60,
                      borderRadius: '50%',
                      backgroundColor: theme.palette.primary.main,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mx: 'auto',
                      mb: 2,
                    }}
                  >
                    <CircularProgress 
                      size={30} 
                      sx={{ color: 'white' }} 
                    />
                  </Box>
                  <Typography variant="body2" fontWeight="500">
                    AI Analysis
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Box
                    sx={{
                      width: 60,
                      height: 60,
                      borderRadius: '50%',
                      backgroundColor: muiAlpha(theme.palette.primary.main, 0.3),
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mx: 'auto',
                      mb: 2,
                    }}
                  >
                    <DescriptionIcon sx={{ color: theme.palette.primary.main, fontSize: 30 }} />
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Report Generation
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Box>
        );

      case 2:
        if (!analysisData) {
          return (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <CircularProgress size={60} />
              <Typography variant="h6" sx={{ mt: 2 }}>
                Loading analysis results...
              </Typography>
            </Box>
          );
        }

        return (
          <Box className="fade-in">
            {/* Results Header */}
            <Card sx={{ mb: 4 }}>
              <CardContent sx={{ p: 4 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 2 }}>
                  <Box>
                    <Typography variant="h4" fontWeight="bold" gutterBottom>
                      {analysisData.title || 'Analysis Results'}
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                      Analysis completed • {new Date(analysisData.created_at).toLocaleString()}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1, fontFamily: 'monospace' }}>
                      Analysis ID: {analysisData.id}
                    </Typography>
                  </Box>
                  <Button
                    variant="contained"
                    onClick={handleNewAnalysis}
                    sx={{ borderRadius: 3 }}
                  >
                    New Analysis
                  </Button>
                </Box>
              </CardContent>
            </Card>

            {/* Results Tabs */}
            <Paper sx={{ mb: 4 }}>
              <Tabs
                value={activeTab}
                onChange={handleTabChange}
                variant={isMobile ? "scrollable" : "fullWidth"}
                scrollButtons="auto"
              >
                <Tab label="Overview" />
                <Tab label="Topics & Sentiment" />
                <Tab label="Summaries" />
                <Tab label="Full Report" />
              </Tabs>
            </Paper>

            {/* Tab Content */}
            <Box sx={{ mb: 4 }}>
              {activeTab === 0 && (
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent sx={{ p: 3 }}>
                        <Typography variant="h6" fontWeight="600" gutterBottom color="primary">
                          📊 Quick Stats
                        </Typography>
                        <Box sx={{ mt: 2 }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', py: 1 }}>
                            <Typography variant="body2">Topics Identified:</Typography>
                            <Typography variant="body2" fontWeight="600">
                              {analysisData.topics_json?.length || 0}
                            </Typography>
                          </Box>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', py: 1 }}>
                            <Typography variant="body2">Overall Sentiment:</Typography>
                            <Typography 
                              variant="body2" 
                              fontWeight="600"
                              sx={{
                                color: analysisData.sentiment_distribution?.overall_sentiment === 'positive' ? 'success.main' :
                                       analysisData.sentiment_distribution?.overall_sentiment === 'negative' ? 'error.main' : 'warning.main'
                              }}
                            >
                              {analysisData.sentiment_distribution?.overall_sentiment || 'N/A'}
                            </Typography>
                          </Box>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', py: 1 }}>
                            <Typography variant="body2">File Type:</Typography>
                            <Typography variant="body2" fontWeight="600">
                              {analysisData.file_type ? analysisData.file_type.toUpperCase() : 'Raw Text'}
                            </Typography>
                          </Box>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent sx={{ p: 3 }}>
                        <Typography variant="h6" fontWeight="600" gutterBottom color="primary">
                          💡 Key Insights
                        </Typography>
                        <Box sx={{ mt: 2 }}>
                          {!analysisData.actionable_insights ? (
                            <Box sx={{ textAlign: 'center', py: 3 }}>
                              <CircularProgress size={30} />
                              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                                Loading insights...
                              </Typography>
                            </Box>
                          ) : analysisData.actionable_insights.length === 0 ? (
                            <Typography variant="body2" color="text.secondary">
                              No insights available for this analysis.
                            </Typography>
                          ) : (
                            analysisData.actionable_insights.slice(0, 3).map((insight, index) => (
                              <Box key={index} sx={{ mb: 2, p: 2, backgroundColor: 'background.default', borderRadius: 2 }}>
                                <Typography variant="body2" fontWeight="500">
                                  {insight.title}
                                </Typography>
                                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                                  {insight.recommendation}
                                </Typography>
                              </Box>
                            ))
                          )}
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              )}

              {activeTab === 1 && (
                <Visualization analysisData={analysisData} />
              )}

              {activeTab === 2 && (
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Card sx={{ height: '100%' }}>
                      <CardContent sx={{ p: 3 }}>
                        <Typography variant="h6" fontWeight="600" gutterBottom color="primary">
                          📋 Extractive Summary
                        </Typography>
                        {!analysisData.extractive_summary ? (
                          <Box sx={{ textAlign: 'center', py: 3 }}>
                            <CircularProgress size={30} />
                            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                              Generating summary...
                            </Typography>
                          </Box>
                        ) : (
                          <Typography variant="body2" sx={{ mt: 2, lineHeight: 1.6 }}>
                            {analysisData.extractive_summary}
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <Card sx={{ height: '100%' }}>
                      <CardContent sx={{ p: 3 }}>
                        <Typography variant="h6" fontWeight="600" gutterBottom color="primary">
                          🧠 Abstractive Summary
                        </Typography>
                        {!analysisData.abstractive_summary ? (
                          <Box sx={{ textAlign: 'center', py: 3 }}>
                            <CircularProgress size={30} />
                            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                              Generating summary...
                            </Typography>
                          </Box>
                        ) : (
                          <Typography variant="body2" sx={{ mt: 2, lineHeight: 1.6 }}>
                            {analysisData.abstractive_summary}
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              )}

              {activeTab === 3 && (
                <ReportViewer 
                  analysisData={analysisData} 
                  analysisId={currentAnalysisIdRef.current}
                />
              )}
            </Box>
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Box className="analysis-page">
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <Typography
            variant="h3"
            fontWeight="bold"
            gutterBottom
            className="gradient-text"
          >
            Text Analysis
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 600, mx: 'auto' }}>
            Transform your text into actionable insights with AI-powered analysis
          </Typography>
        </Box>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 4 }}>
            {error}
          </Alert>
        )}

        {/* Stepper */}
        {!isMobile && (
          <Stepper activeStep={activeStep} sx={{ mb: 6 }}>
            {steps.map((step, index) => (
              <Step key={step.label}>
                <StepLabel
                  StepIconComponent={() => (
                    <Box
                      sx={{
                        width: 40,
                        height: 40,
                        borderRadius: '50%',
                        backgroundColor: activeStep >= index ? 'primary.main' : 'grey.300',
                        color: activeStep >= index ? 'white' : 'grey.500',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: 'bold',
                      }}
                    >
                      {activeStep > index ? <CheckCircleIcon /> : step.icon}
                    </Box>
                  )}
                >
                  {step.label}
                </StepLabel>
              </Step>
            ))}
          </Stepper>
        )}

        {/* Step Content */}
        {renderStepContent(activeStep)}
      </Container>
    </Box>
  );
};

export default Analysis;