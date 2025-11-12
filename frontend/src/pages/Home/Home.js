import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
  useTheme,
  useMediaQuery,
  alpha,
} from '@mui/material';
import {
  Analytics,
  Timeline,
  Description,
  Download,
  TrendingUp,
  Speed,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { analysisAPI } from '../../services/api';
import './Home.css';

const Home = () => {
  const [stats, setStats] = useState(null);
  const [recentAnalyses, setRecentAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsResponse, analysesResponse] = await Promise.all([
        analysisAPI.getStats(),
        analysisAPI.getAnalyses(),
      ]);

      setStats(statsResponse.data);
      setRecentAnalyses(analysesResponse.data.slice(0, 5));
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ icon, title, value, subtitle, color }) => (
    <Card 
      sx={{ 
        height: '100%',
        background: `linear-gradient(135deg, ${alpha(color, 0.1)} 0%, ${alpha(color, 0.05)} 100%)`,
        border: `1px solid ${alpha(color, 0.2)}`,
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: `0 8px 25px ${alpha(color, 0.15)}`,
        },
      }}
    >
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box
            sx={{
              p: 1,
              borderRadius: 3,
              backgroundColor: alpha(color, 0.1),
              color: color,
              mr: 2,
            }}
          >
            {icon}
          </Box>
          <Box>
            <Typography variant="h4" fontWeight="bold" color={color}>
              {value}
            </Typography>
            <Typography variant="body2" color="text.secondary" fontWeight="500">
              {title}
            </Typography>
          </Box>
        </Box>
        <Typography variant="body2" color="text.secondary">
          {subtitle}
        </Typography>
      </CardContent>
    </Card>
  );

  const FeatureCard = ({ icon, title, description, action }) => (
    <Card 
      sx={{ 
        height: '100%',
        transition: 'all 0.3s ease',
        border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`,
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: theme.shadows[8],
          border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`,
        },
      }}
    >
      <CardContent sx={{ p: 3, textAlign: 'center' }}>
        <Box
          sx={{
            p: 2,
            borderRadius: 4,
            backgroundColor: alpha(theme.palette.primary.main, 0.1),
            color: theme.palette.primary.main,
            display: 'inline-flex',
            mb: 2,
          }}
        >
          {icon}
        </Box>
        <Typography variant="h6" fontWeight="600" gutterBottom>
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {description}
        </Typography>
        {action}
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box sx={{ width: '100%', p: 3 }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box className="home-page fade-in">
      {/* Hero Section - Updated Background */}
      <Box
        sx={{
          background: `linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #60a5fa 100%)`,
          color: 'white',
          py: { xs: 8, md: 12 },
          mb: 6,
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'radial-gradient(circle at 30% 20%, rgba(255,255,255,0.1) 0%, transparent 50%)',
          },
        }}
      >
        <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography
                variant="h2"
                fontWeight="bold"
                gutterBottom
                sx={{
                  fontSize: { xs: '2.5rem', md: '3.5rem' },
                  lineHeight: 1.2,
                  textShadow: '0 2px 10px rgba(0,0,0,0.1)',
                }}
              >
                Unlock Insights from Your Text
              </Typography>
              <Typography
                variant="h6"
                sx={{
                  opacity: 0.95,
                  mb: 4,
                  fontSize: { xs: '1.1rem', md: '1.25rem' },
                  textShadow: '0 1px 5px rgba(0,0,0,0.1)',
                }}
              >
                Advanced AI-powered text analysis for topic modeling, sentiment analysis, and actionable insights.
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  size="large"
                  onClick={() => navigate('/analysis')}
                  sx={{
                    backgroundColor: '#f8fafc',
                    color: '#1e40af',
                    px: 4,
                    py: 1.5,
                    fontSize: '1.1rem',
                    fontWeight: 600,
                    borderRadius: 3,
                    boxShadow: '0 4px 15px rgba(255,255,255,0.2)',
                    '&:hover': {
                      backgroundColor: '#f1f5f9',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 6px 20px rgba(255,255,255,0.3)',
                    },
                    transition: 'all 0.3s ease',
                  }}
                >
                  Start Analyzing
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={() => navigate('/history')}
                  sx={{
                    borderColor: 'rgba(255,255,255,0.5)',
                    color: 'white',
                    px: 4,
                    py: 1.5,
                    fontSize: '1.1rem',
                    fontWeight: 600,
                    borderRadius: 3,
                    backdropFilter: 'blur(10px)',
                    '&:hover': {
                      backgroundColor: 'rgba(255,255,255,0.1)',
                      borderColor: 'white',
                      transform: 'translateY(-2px)',
                    },
                    transition: 'all 0.3s ease',
                  }}
                >
                  View History
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box
                sx={{
                  background: 'rgba(255,255,255,0.1)',
                  borderRadius: 4,
                  p: 4,
                  backdropFilter: 'blur(20px)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
                }}
              >
                <Typography variant="h5" fontWeight="600" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <span style={{ fontSize: '1.5rem' }}>🚀</span> Powerful Features
                </Typography>
                <Box sx={{ mt: 2 }}>
                  {[
                    { text: 'Topic Modeling', icon: '🔍' },
                    { text: 'Sentiment Analysis', icon: '😊' },
                    { text: 'Text Summarization', icon: '📝' },
                    { text: 'PDF Reports', icon: '📊' }
                  ].map((feature, index) => (
                    <Box key={feature.text} sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                      <Box
                        sx={{
                          width: 32,
                          height: 32,
                          borderRadius: '50%',
                          backgroundColor: 'rgba(255,255,255,0.2)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          mr: 2,
                          fontSize: '1rem',
                          fontWeight: 'bold',
                        }}
                      >
                        {feature.icon}
                      </Box>
                      <Typography variant="body1" sx={{ fontWeight: 500 }}>
                        {feature.text}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>

      <Container maxWidth="lg">
        {/* Stats Section */}
        {stats && (
          <Box sx={{ mb: 8 }}>
            <Typography 
              variant="h4" 
              fontWeight="bold" 
              gutterBottom 
              sx={{ 
                textAlign: 'center', 
                mb: 4,
                background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                color: 'transparent',
              }}
            >
              Platform Overview
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <StatCard
                  icon={<Analytics sx={{ fontSize: 32 }} />}
                  title="Total Analyses"
                  value={stats.total_analyses || 0}
                  subtitle="Text analyses performed"
                  color="#3b82f6"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <StatCard
                  icon={<Timeline sx={{ fontSize: 32 }} />}
                  title="Average Topics"
                  value={stats.average_topics || 0}
                  subtitle="Per analysis"
                  color="#10b981"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <StatCard
                  icon={<TrendingUp sx={{ fontSize: 32 }} />}
                  title="File Types"
                  value={stats.file_type_distribution?.length || 0}
                  subtitle="Supported formats"
                  color="#f59e0b"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <StatCard
                  icon={<Speed sx={{ fontSize: 32 }} />}
                  title="Success Rate"
                  value="100%"
                  subtitle="Analysis completion"
                  color="#ef4444"
                />
              </Grid>
            </Grid>
          </Box>
        )}

        {/* Features Section */}
        <Box sx={{ mb: 8 }}>
          <Typography 
            variant="h4" 
            fontWeight="bold" 
            gutterBottom 
            sx={{ 
              textAlign: 'center', 
              mb: 2,
              background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              color: 'transparent',
            }}
          >
            How It Works
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ textAlign: 'center', mb: 6, maxWidth: 600, mx: 'auto' }}>
            Transform your text data into actionable insights with our comprehensive analysis platform
          </Typography>
          
          <Grid container spacing={4}>
            <Grid item xs={12} md={4}>
              <FeatureCard
                icon={<Description sx={{ fontSize: 40 }} />}
                title="Upload Content"
                description="Paste text or upload files (TXT, CSV, DOCX) for analysis. Our platform supports multiple input formats."
                action={
                  <Button 
                    variant="contained" 
                    onClick={() => navigate('/analysis')}
                    sx={{ 
                      borderRadius: 3,
                      background: 'linear-gradient(135deg, #3b82f6 0%, #1e40af 100%)',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%)',
                      },
                    }}
                  >
                    Try Now
                  </Button>
                }
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FeatureCard
                icon={<Analytics sx={{ fontSize: 40 }} />}
                title="AI Analysis"
                description="Advanced algorithms perform topic modeling, sentiment analysis, and generate comprehensive summaries."
                action={
                  <Button 
                    variant="contained" 
                    onClick={() => navigate('/analysis')}
                    sx={{ 
                      borderRadius: 3,
                      background: 'linear-gradient(135deg, #10b981 0%, #047857 100%)',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #047857 0%, #065f46 100%)',
                      },
                    }}
                  >
                    Learn More
                  </Button>
                }
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FeatureCard
                icon={<Download sx={{ fontSize: 40 }} />}
                title="Get Insights"
                description="Download detailed PDF reports with visualizations, insights, and actionable recommendations."
                action={
                  <Button 
                    variant="contained" 
                    onClick={() => navigate('/history')}
                    sx={{ 
                      borderRadius: 3,
                      background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #d97706 0%, #b45309 100%)',
                      },
                    }}
                  >
                    View Reports
                  </Button>
                }
              />
            </Grid>
          </Grid>
        </Box>

        {/* Recent Analyses */}
        {recentAnalyses.length > 0 && (
          <Box sx={{ mb: 8 }}>
            <Typography 
              variant="h4" 
              fontWeight="bold" 
              gutterBottom 
              sx={{ 
                mb: 4,
                background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                color: 'transparent',
              }}
            >
              Recent Analyses
            </Typography>
            <Grid container spacing={3}>
              {recentAnalyses.map((analysis) => (
                <Grid item xs={12} md={6} key={analysis.id}>
                  <Card 
                    sx={{ 
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      border: `1px solid ${alpha('#3b82f6', 0.1)}`,
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: `0 8px 25px ${alpha('#3b82f6', 0.15)}`,
                        border: `1px solid ${alpha('#3b82f6', 0.3)}`,
                      },
                    }}
                    onClick={() => navigate('/history')}
                  >
                    <CardContent sx={{ p: 3 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                        <Typography variant="h6" fontWeight="600" noWrap sx={{ maxWidth: '70%' }}>
                          {analysis.title}
                        </Typography>
                        <Chip
                          label={analysis.file_type || 'Raw Text'}
                          size="small"
                          sx={{
                            background: `linear-gradient(135deg, ${alpha('#3b82f6', 0.1)} 0%, ${alpha('#3b82f6', 0.05)} 100%)`,
                            color: '#1e40af',
                            border: `1px solid ${alpha('#3b82f6', 0.3)}`,
                            fontWeight: 500,
                          }}
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {new Date(analysis.created_at).toLocaleDateString()} • {analysis.topics_json?.length || 0} topics
                      </Typography>
                      {analysis.sentiment_distribution && (
                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                          <Chip
                            label={`Positive: ${analysis.sentiment_distribution.distribution?.positive || 0}`}
                            size="small"
                            sx={{ 
                              backgroundColor: alpha('#10b981', 0.1), 
                              color: '#047857',
                              border: `1px solid ${alpha('#10b981', 0.3)}`,
                            }}
                          />
                          <Chip
                            label={`Neutral: ${analysis.sentiment_distribution.distribution?.neutral || 0}`}
                            size="small"
                            sx={{ 
                              backgroundColor: alpha('#f59e0b', 0.1), 
                              color: '#d97706',
                              border: `1px solid ${alpha('#f59e0b', 0.3)}`,
                            }}
                          />
                          <Chip
                            label={`Negative: ${analysis.sentiment_distribution.distribution?.negative || 0}`}
                            size="small"
                            sx={{ 
                              backgroundColor: alpha('#ef4444', 0.1), 
                              color: '#dc2626',
                              border: `1px solid ${alpha('#ef4444', 0.3)}`,
                            }}
                          />
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </Container>
    </Box>
  );
};

export default Home;