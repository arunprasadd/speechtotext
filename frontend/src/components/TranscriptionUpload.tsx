// frontend/src/components/TranscriptionUpload.tsx
import React, { useState } from 'react';
import {
  Box,
  Button,
  VStack,
  Text,
  Progress,
  Select,
  useToast,
  Icon,
  Container,
  Heading,
} from '@chakra-ui/react';
import { FiUploadCloud } from 'react-icons/fi';
import axios from 'axios';

const TranscriptionUpload: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [transcriptionText, setTranscriptionText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [language, setLanguage] = useState('en');
  const [model, setModel] = useState('base');
  const toast = useToast();

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
      setTranscriptionText('');
      setUploadProgress(0);
    }
  };

  const checkTranscriptionStatus = async (transcriptionId: number) => {
    try {
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL}/transcription/${transcriptionId}`
      );
      
      if (response.data.status === 'completed') {
        setTranscriptionText(response.data.text);
        setIsProcessing(false);
        toast({
          title: 'Transcription completed',
          status: 'success',
          duration: 3000,
        });
      } else if (response.data.status === 'failed') {
        setIsProcessing(false);
        toast({
          title: 'Transcription failed',
          description: response.data.error,
          status: 'error',
          duration: 3000,
        });
      } else {
        // Continue checking status
        setTimeout(() => checkTranscriptionStatus(transcriptionId), 2000);
      }
    } catch (error) {
      console.error('Error checking status:', error);
      setIsProcessing(false);
      toast({
        title: 'Error checking status',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsProcessing(true);
    setUploadProgress(0);
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('language', language);
    formData.append('model_size', model);

    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/transcription/upload`,
        formData,
        {
          onUploadProgress: (progressEvent: any) => {
            if (progressEvent.total) {
              const progress = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
              setUploadProgress(progress);
            }
          },
        }
      );

      toast({
        title: 'File uploaded successfully',
        description: 'Starting transcription...',
        status: 'success',
        duration: 3000,
      });

      checkTranscriptionStatus(response.data.id);

    } catch (error: any) {
      setIsProcessing(false);
      toast({
        title: 'Upload failed',
        description: error.response?.data?.detail || 'An error occurred',
        status: 'error',
        duration: 3000,
      });
    }
  };

  return (
    <Container maxW="container.md" py={10}>
      <VStack spacing={8} align="stretch">
        <Heading textAlign="center" size="lg">
          Video to Text Transcription
        </Heading>

        {/* File Upload Area */}
        <Box
          borderWidth={2}
          borderRadius="lg"
          p={10}
          borderStyle="dashed"
          borderColor="gray.300"
          bg="gray.50"
          _hover={{ bg: 'gray.100' }}
          cursor="pointer"
          onClick={() => document.getElementById('file-upload')?.click()}
        >
          <input
            id="file-upload"
            type="file"
            accept="video/*,audio/*"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
          <VStack spacing={4}>
            <Icon as={FiUploadCloud} w={12} h={12} color="gray.400" />
            <Text fontSize="lg" color="gray.500">
              Click or drag video file to upload
            </Text>
            {selectedFile && (
              <Text color="blue.500" fontWeight="bold">
                Selected: {selectedFile.name}
              </Text>
            )}
          </VStack>
        </Box>

        {/* Language Selection */}
        <Select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          isDisabled={isProcessing}
        >
          <option value="en">English</option>
          <option value="es">Spanish</option>
          <option value="fr">French</option>
          <option value="de">German</option>
          <option value="hi">Hindi</option>
          <option value="ja">Japanese</option>
          <option value="zh">Chinese</option>
        </Select>

        {/* Model Selection */}
        <Select
          value={model}
          onChange={(e) => setModel(e.target.value)}
          isDisabled={isProcessing}
        >
          <option value="tiny">Tiny (Fastest)</option>
          <option value="base">Base</option>
          <option value="small">Small</option>
          <option value="medium">Medium</option>
          <option value="large">Large (Most Accurate)</option>
        </Select>

        {/* Upload Button */}
        <Button
          colorScheme="blue"
          size="lg"
          onClick={handleUpload}
          isLoading={isProcessing}
          loadingText="Processing..."
          isDisabled={!selectedFile || isProcessing}
        >
          Start Transcription
        </Button>

        {/* Progress Bar */}
        {(uploadProgress > 0 || isProcessing) && (
          <Box>
            <Progress
              value={uploadProgress}
              size="md"
              colorScheme="blue"
              hasStripe
              isAnimated
            />
            <Text mt={2} textAlign="center">
              {uploadProgress === 100 && isProcessing
                ? 'Transcribing...'
                : `Uploading: ${uploadProgress}%`}
            </Text>
          </Box>
        )}

        {/* Transcription Result */}
        {transcriptionText && (
          <Box
            p={6}
            borderWidth={1}
            borderRadius="lg"
            bg="white"
            shadow="sm"
          >
            <Text fontWeight="bold" mb={4}>
              Transcription Result:
            </Text>
            <Text whiteSpace="pre-wrap">{transcriptionText}</Text>
          </Box>
        )}
      </VStack>
    </Container>
  );
};

export default TranscriptionUpload;