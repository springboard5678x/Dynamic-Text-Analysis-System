import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import { CHART_COLORS, SENTIMENT_COLORS } from '../../utils/constants';
import './Visualization.css';

const Visualization = ({ analysisData }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  if (!analysisData) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="h6" color="text.secondary">
          No analysis data available for visualization
        </Typography>
      </Box>
    );
  }

  // Prepare topic data for bar chart
  const topicData = analysisData.topics_json?.map((topic, index) => ({
    name: `Topic ${topic.topic_id}`,
    words: topic.words.slice(0, 3).join(', '),
    strength: topic.strength || 1,
    fullTopic: topic,
    color: CHART_COLORS[index % CHART_COLORS.length],
  })) || [];

  // Prepare sentiment data for pie chart
  const sentimentData = analysisData.sentiment_distribution?.distribution ? 
    Object.entries(analysisData.sentiment_distribution.distribution).map(([key, value]) => ({
      name: key.charAt(0).toUpperCase() + key.slice(1),
      value: value,
      color: SENTIMENT_COLORS[key] || '#999999'
    })) : [];

  // Generate word cloud data from topics
  const generateWordCloudData = () => {
    const wordMap = new Map();
    
    // Extract words from all topics with their frequencies
    analysisData.topics_json?.forEach(topic => {
      topic.words?.forEach((word, index) => {
        const weight = topic.weights?.[index] || (topic.words.length - index) / topic.words.length;
        const currentWeight = wordMap.get(word) || 0;
        wordMap.set(word, currentWeight + weight);
      });
    });

    // Convert to array and sort by weight
    return Array.from(wordMap.entries())
      .map(([text, value]) => ({ text, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 60); // Reduced to 60 for better spacing
  };

  const wordCloudData = generateWordCloudData();

  // Vibrant multicolor palette
  const WORD_CLOUD_COLORS = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
    '#F8C471', '#82E0AA', '#F1948A', '#85C1E9', '#D7BDE2',
    '#F9E79F', '#A9DFBF', '#F5B7B1', '#AED6F1', '#E8DAEF',
    '#FAD7A0', '#ABEBC6', '#F5CBA7', '#AED6F1', '#D2B4DE',
    '#F7DC6F', '#A3E4D7', '#F1948A', '#7FB3D5', '#C39BD3'
  ];

  // Improved rectangular grid-based word cloud layout
  const getRectangularWordCloudLayout = () => {
    if (wordCloudData.length === 0) return [];

    const minValue = Math.min(...wordCloudData.map(w => w.value));
    const maxValue = Math.max(...wordCloudData.map(w => w.value));
    
    // Calculate sizes and colors
    const wordsWithStyles = wordCloudData.map((word, index) => {
      // Font size based on weight
      const fontSize = 16 + ((word.value - minValue) / (maxValue - minValue)) * 40;
      
      // Random color from vibrant palette
      const color = WORD_CLOUD_COLORS[index % WORD_CLOUD_COLORS.length];
      
      return {
        ...word,
        fontSize,
        color,
        fontWeight: word.value > (maxValue * 0.8) ? 900 : 
                   word.value > (maxValue * 0.6) ? 800 :
                   word.value > (maxValue * 0.4) ? 600 : 500,
        rotation: Math.random() > 0.8 ? Math.random() * 20 - 10 : 0, // Less rotation
      };
    });

    // Improved grid placement - more organized
    const rows = 6; // Reduced rows for better spacing
    const cols = 10; // Columns
    const cellWidth = 95 / cols; // Percentage width per cell
    const cellHeight = 95 / rows; // Percentage height per cell

    return wordsWithStyles.map((word, index) => {
      if (index >= rows * cols) return null; // Safety check
      
      // Calculate grid position - top to bottom, left to right
      const row = Math.floor(index / cols);
      const col = index % cols;
      
      // Center within cell with minimal random offset
      const baseX = (col * cellWidth) + (cellWidth / 2);
      const baseY = (row * cellHeight) + (cellHeight / 2);
      
      // Very small random offset for natural look
      const randomOffsetX = (Math.random() - 0.5) * (cellWidth * 0.3);
      const randomOffsetY = (Math.random() - 0.5) * (cellHeight * 0.3);
      
      const left = baseX + randomOffsetX;
      const top = baseY + randomOffsetY;
      
      // Ensure words stay within bounds
      const boundedLeft = Math.max(5, Math.min(95, left));
      const boundedTop = Math.max(5, Math.min(95, top));

      return {
        ...word,
        left: `${boundedLeft}%`,
        top: `${boundedTop}%`,
        zIndex: Math.floor(word.fontSize),
      };
    }).filter(Boolean); // Remove null entries
  };

  const wordCloudLayout = getRectangularWordCloudLayout();

  // Custom tooltip for topic chart
  const CustomTopicTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const topic = payload[0].payload.fullTopic;
      return (
        <Box
          sx={{
            backgroundColor: 'white',
            padding: 2,
            border: `1px solid ${theme.palette.divider}`,
            borderRadius: 2,
            boxShadow: theme.shadows[3],
          }}
        >
          <Typography variant="body2" fontWeight="600" gutterBottom>
            {label}
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Top words: {topic.words.slice(0, 5).join(', ')}
          </Typography>
          <Typography variant="body2">
            Strength: {(topic.strength || 0).toFixed(2)}
          </Typography>
        </Box>
      );
    }
    return null;
  };

  // Custom tooltip for sentiment chart
  const CustomSentimentTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      return (
        <Box
          sx={{
            backgroundColor: 'white',
            padding: 2,
            border: `1px solid ${theme.palette.divider}`,
            borderRadius: 2,
            boxShadow: theme.shadows[3],
          }}
        >
          <Typography variant="body2" fontWeight="600" gutterBottom>
            {data.payload.name}
          </Typography>
          <Typography variant="body2">
            Count: {data.value}
          </Typography>
        </Box>
      );
    }
    return null;
  };

  // Custom label for pie chart
  const renderCustomizedLabel = ({
    cx, cy, midAngle, innerRadius, outerRadius, percent, index
  }) => {
    if (percent < 0.1) return null;
    
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
        fontSize={12}
        fontWeight="600"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  return (
    <Box className="visualization-component">
      <Grid container spacing={3}>
        {/* Topics Bar Chart */}
        <Grid item xs={12} lg={8}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="600" gutterBottom color="primary">
                📊 Topic Distribution
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Visual representation of identified topics and their relative strength
              </Typography>
              
              <Box sx={{ height: 400, width: '100%' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={topicData}
                    margin={{
                      top: 20,
                      right: 30,
                      left: 20,
                      bottom: 80,
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
                    <XAxis 
                      dataKey="words" 
                      angle={-45}
                      textAnchor="end"
                      height={80}
                      fontSize={12}
                      tick={{ fill: theme.palette.text.secondary }}
                    />
                    <YAxis 
                      fontSize={12}
                      tick={{ fill: theme.palette.text.secondary }}
                    />
                    <Tooltip content={<CustomTopicTooltip />} />
                    <Bar 
                      dataKey="strength" 
                      name="Topic Strength"
                      radius={[4, 4, 0, 0]}
                    >
                      {topicData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Box>
              
              {topicData.length === 0 && (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    No topic data available for visualization
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Sentiment Pie Chart */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="600" gutterBottom color="primary">
                😊 Sentiment Analysis
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Distribution of positive, neutral, and negative sentiments
              </Typography>
              
              <Box sx={{ height: 300, width: '100%' }}>
                {sentimentData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={sentimentData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={renderCustomizedLabel}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {sentimentData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip content={<CustomSentimentTooltip />} />
                      <Legend 
                        layout={isMobile ? 'horizontal' : 'vertical'}
                        verticalAlign={isMobile ? 'bottom' : 'middle'}
                        align="right"
                        wrapperStyle={{
                          paddingLeft: isMobile ? 0 : 20,
                          paddingTop: isMobile ? 20 : 0,
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography variant="body2" color="text.secondary">
                      No sentiment data available
                    </Typography>
                  </Box>
                )}
              </Box>

              {/* Overall Sentiment Summary */}
              {analysisData.sentiment_distribution && (
                <Box 
                  sx={{ 
                    mt: 2, 
                    p: 2, 
                    backgroundColor: 'background.default', 
                    borderRadius: 2,
                    textAlign: 'center',
                  }}
                >
                  <Typography variant="body2" fontWeight="500" gutterBottom>
                    Overall Sentiment
                  </Typography>
                  <Typography 
                    variant="h6" 
                    fontWeight="600"
                    sx={{
                      color: 
                        analysisData.sentiment_distribution.overall_sentiment === 'positive' ? 'success.main' :
                        analysisData.sentiment_distribution.overall_sentiment === 'negative' ? 'error.main' : 'warning.main'
                    }}
                  >
                    {analysisData.sentiment_distribution.overall_sentiment?.toUpperCase() || 'N/A'}
                  </Typography>
                  {analysisData.sentiment_distribution.overall_polarity && (
                    <Typography variant="body2" color="text.secondary">
                      Polarity: {analysisData.sentiment_distribution.overall_polarity.toFixed(3)}
                    </Typography>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Properly Aligned Multicolor Word Cloud */}
        <Grid item xs={12}>
          <Card>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight="600" gutterBottom color="primary">
                🌈 Key Themes Word Cloud
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Visual representation of the most frequent words and themes
              </Typography>
              
              <Box 
                sx={{ 
                  height: 450,
                  background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
                  borderRadius: 2,
                  position: 'relative',
                  border: `1px solid #e2e8f0`,
                  overflow: 'hidden',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                {wordCloudLayout.length > 0 ? (
                  <Box sx={{ 
                    position: 'relative', 
                    width: '90%', 
                    height: '90%',
                    display: 'flex',
                    flexWrap: 'wrap',
                    alignContent: 'flex-start',
                    justifyContent: 'center',
                    gap: 1,
                    padding: 2,
                  }}>
                    {wordCloudLayout.map((word, index) => (
                      <Box
                        key={`${word.text}-${index}`}
                        sx={{
                          display: 'inline-block',
                          fontSize: `${word.fontSize}px`,
                          fontWeight: word.fontWeight,
                          color: word.color,
                          transform: `rotate(${word.rotation}deg)`,
                          padding: '4px 8px',
                          margin: '2px',
                          cursor: 'pointer',
                          transition: 'all 0.3s ease',
                          lineHeight: 1,
                          textShadow: '1px 1px 2px rgba(255,255,255,0.8)',
                          '&:hover': {
                            transform: `rotate(${word.rotation}deg) scale(1.2)`,
                            zIndex: 1000,
                            textShadow: '2px 2px 4px rgba(0,0,0,0.2)',
                            filter: 'brightness(1.1)',
                          },
                        }}
                        title={`"${word.text}" - Frequency: ${word.value.toFixed(2)}`}
                      >
                        {word.text}
                      </Box>
                    ))}
                  </Box>
                ) : analysisData.wordcloud_url ? (
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    height: '100%',
                  }}>
                    <img 
                      src={analysisData.wordcloud_url} 
                      alt="Word cloud" 
                      style={{ 
                        maxWidth: '100%', 
                        maxHeight: '100%',
                        objectFit: 'contain',
                      }}
                    />
                  </Box>
                ) : (
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    height: '100%',
                    flexDirection: 'column',
                    gap: 2,
                  }}>
                    <Typography variant="body1" color="text.secondary">
                      No word data available for word cloud
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Upload text or files to generate word cloud visualization
                    </Typography>
                  </Box>
                )}
              </Box>
              
              {/* Word Cloud Legend */}
              {wordCloudLayout.length > 0 && (
                <Box sx={{ mt: 2, textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    <strong>Word Cloud Guide:</strong>
                  </Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'center', gap: 3, flexWrap: 'wrap' }}>
                    <Typography variant="caption" color="text.secondary">
                      📏 <strong>Size:</strong> Larger words = higher frequency
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      🎨 <strong>Colors:</strong> Random vibrant colors for visual appeal
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      🔍 <strong>Hover:</strong> See exact frequency values
                    </Typography>
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Topic Details */}
        {analysisData.topics_json && analysisData.topics_json.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" fontWeight="600" gutterBottom color="primary">
                  🔍 Detailed Topic Analysis
                </Typography>
                
                <Grid container spacing={2}>
                  {analysisData.topics_json.map((topic, index) => (
                    <Grid item xs={12} md={6} lg={4} key={topic.topic_id}>
                      <Box
                        sx={{
                          p: 2,
                          border: `1px solid ${theme.palette.divider}`,
                          borderRadius: 2,
                          backgroundColor: 'background.default',
                          height: '100%',
                        }}
                      >
                        <Typography 
                          variant="subtitle1" 
                          fontWeight="600" 
                          gutterBottom
                          sx={{ color: CHART_COLORS[index % CHART_COLORS.length] }}
                        >
                          Topic {topic.topic_id}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Key words: {topic.words.slice(0, 8).join(', ')}
                          {topic.words.length > 8 && '...'}
                        </Typography>
                        {topic.strength && (
                          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                            <Box 
                              sx={{ 
                                flexGrow: 1,
                                height: 4,
                                backgroundColor: theme.palette.divider,
                                borderRadius: 2,
                                overflow: 'hidden',
                              }}
                            >
                              <Box 
                                sx={{
                                  height: '100%',
                                  backgroundColor: CHART_COLORS[index % CHART_COLORS.length],
                                  width: `${Math.min(topic.strength * 100, 100)}%`,
                                }}
                              />
                            </Box>
                            <Typography 
                              variant="body2" 
                              sx={{ ml: 1, minWidth: 40, textAlign: 'right' }}
                            >
                              {(topic.strength * 100).toFixed(1)}%
                            </Typography>
                          </Box>
                        )}
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default Visualization;