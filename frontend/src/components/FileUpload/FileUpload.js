 import React, { useState, useRef } from 'react';
import {
  Box,
  Button,
  Typography,
  Card,
  CardContent,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Description as FileIcon,
  Close as CloseIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { SUPPORTED_FILE_TYPES, MAX_FILE_SIZE } from '../../utils/constants';
import './FileUpload.css';

const FileUpload = ({ onSubmit, loading }) => {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFileSelect(droppedFile);
    }
  };

  const handleFileSelect = (selectedFile) => {
    setError('');

    // Check file type
    const fileExtension = selectedFile.name.split('.').pop().toLowerCase();
    const isValidType = SUPPORTED_FILE_TYPES.some(type => type.extension === fileExtension);
    
    if (!isValidType) {
      setError(`Unsupported file type. Supported formats: ${SUPPORTED_FILE_TYPES.map(t => t.extension).join(', ')}`);
      return;
    }

    // Check file size
    if (selectedFile.size > MAX_FILE_SIZE) {
      setError('File size exceeds 10MB limit');
      return;
    }

    setFile(selectedFile);
    setTitle(selectedFile.name.replace(/\.[^/.]+$/, "")); // Remove extension for title
  };

  const handleFileInput = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      handleFileSelect(selectedFile);
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setTitle('');
    setError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    if (!title.trim()) {
      setError('Please enter a title for your analysis');
      return;
    }

    onSubmit({
      title: title.trim(),
      uploaded_file: file,
    });
  };

  const getFileTypeInfo = (fileName) => {
    const extension = fileName.split('.').pop().toLowerCase();
    return SUPPORTED_FILE_TYPES.find(type => type.extension === extension) || { name: 'Unknown' };
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Box className="file-upload-component">
      <form onSubmit={handleSubmit}>
        {/* Drag & Drop Area */}
        {!file && (
          <Box
            className={`drop-zone ${dragActive ? 'active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            sx={{
              border: '2px dashed',
              borderColor: dragActive ? 'primary.main' : 'grey.300',
              borderRadius: 3,
              p: 4,
              textAlign: 'center',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              backgroundColor: dragActive ? 'primary.light' : 'background.default',
              mb: 3,
              '&:hover': {
                borderColor: 'primary.main',
                backgroundColor: 'primary.light',
              },
            }}
          >
            <UploadIcon 
              sx={{ 
                fontSize: 48, 
                color: dragActive ? 'primary.main' : 'grey.400',
                mb: 2,
              }} 
            />
            <Typography variant="h6" gutterBottom>
              Drag & drop your file here
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              or click to browse files
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
              Supports: {SUPPORTED_FILE_TYPES.map(type => type.extension.toUpperCase()).join(', ')} • Max 10MB
            </Typography>
            
            <input
              ref={fileInputRef}
              type="file"
              hidden
              onChange={handleFileInput}
              accept={SUPPORTED_FILE_TYPES.map(type => type.accept).join(',')}
            />
          </Box>
        )}

        {/* Selected File Preview */}
        {file && (
          <Card variant="outlined" sx={{ mb: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <FileIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                  <Box>
                    <Typography variant="h6" fontWeight="600">
                      {file.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {getFileTypeInfo(file.name).name} • {formatFileSize(file.size)}
                    </Typography>
                  </Box>
                </Box>
                <IconButton onClick={handleRemoveFile} disabled={loading}>
                  <CloseIcon />
                </IconButton>
              </Box>

              {/* Title Input */}
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" fontWeight="500" gutterBottom>
                  Analysis Title:
                </Typography>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Enter analysis title..."
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    border: '1px solid #e0e0e0',
                    borderRadius: '8px',
                    fontSize: '16px',
                    fontFamily: 'inherit',
                  }}
                  disabled={loading}
                />
              </Box>

              {/* File Info */}
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip
                  label={getFileTypeInfo(file.name).name}
                  variant="outlined"
                  size="small"
                  color="primary"
                />
                <Chip
                  label={formatFileSize(file.size)}
                  variant="outlined"
                  size="small"
                />
                <Chip
                  icon={<CheckIcon />}
                  label="Ready for analysis"
                  color="success"
                  variant="outlined"
                  size="small"
                />
              </Box>
            </CardContent>
          </Card>
        )}

        {/* Error Display */}
        {error && (
          <Alert 
            severity="error" 
            sx={{ mb: 3 }}
            action={
              error.includes('Unsupported file type') && (
                <Button color="inherit" size="small" onClick={handleRemoveFile}>
                  Change File
                </Button>
              )
            }
          >
            {error}
          </Alert>
        )}

        {/* Submit Button */}
        <Button
          type="submit"
          variant="contained"
          size="large"
          disabled={loading || !file || !title.trim()}
          startIcon={<UploadIcon />}
          fullWidth
          sx={{
            py: 1.5,
            fontSize: '1.1rem',
            fontWeight: 600,
            borderRadius: 3,
          }}
        >
          {loading ? 'Uploading & Analyzing...' : 'Upload & Analyze'}
        </Button>

        {/* Supported Formats */}
        <Card variant="outlined" sx={{ mt: 3 }}>
          <CardContent sx={{ p: 2 }}>
            <Typography variant="body2" fontWeight="500" color="text.secondary" gutterBottom>
              📁 Supported File Formats:
            </Typography>
            <List dense sx={{ py: 0 }}>
              {SUPPORTED_FILE_TYPES.map((type, index) => (
                <ListItem key={index} sx={{ px: 0, py: 0.5 }}>
                  <ListItemIcon sx={{ minWidth: 32 }}>
                    <FileIcon sx={{ fontSize: 16, color: 'primary.main' }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={`${type.name} (.${type.extension})`}
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>

        {/* Loading Progress */}
        {loading && (
          <Box sx={{ mt: 2 }}>
            <LinearProgress />
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1, textAlign: 'center' }}>
              Uploading and processing your file...
            </Typography>
          </Box>
        )}
      </form>
    </Box>
  );
};

export default FileUpload;
