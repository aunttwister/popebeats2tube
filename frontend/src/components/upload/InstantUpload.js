import React, { useState, useEffect, useRef } from 'react';
import { Box, Button, CircularProgress, Typography, Fade } from '@mui/material';
import UploadList from './UploadList';
import { createBatchInstant } from '../../services/instantTuneService.ts';
import { fileConverter } from '../../utils/fileConverter';
import { toastHelper } from '../../utils/toastHelper';
import { initialUploadContainer } from '../../constants/uploadConstants';
import { validateContainer } from '../../utils/uploadValidator';

function InstantUpload() {
  const [uploadContainers, setUploadContainers] = useState([
    { ...initialUploadContainer, uploadDate: undefined }
  ]);

  const [errorsList, setErrorsList] = useState([]);
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  const timerRef = useRef(null);
  const startTimeRef = useRef(null);

  const handleAddContainer = () => {
    setUploadContainers(prev => [
      ...prev,
      { ...initialUploadContainer, uploadDate: undefined }
    ]);
  };

  const handleUpdateContainer = (index, updatedValues) => {
    const updated = [...uploadContainers];
    updated[index] = { ...updated[index], ...updatedValues };
    setUploadContainers(updated);

    if (hasSubmitted) {
      const updatedErrors = [...errorsList];
      updatedErrors[index] = validateContainer(updated[index], false);
      setErrorsList(updatedErrors);
    }
  };

  useEffect(() => {
    if (isUploading) {
      setElapsedSeconds(0);
      timerRef.current = setInterval(() => {
        setElapsedSeconds(prev => prev + 1);
      }, 1000);
    } else {
      clearInterval(timerRef.current);
    }

    return () => clearInterval(timerRef.current);
  }, [isUploading]);

  const resetForm = () => {
    // Reset everything to initial
    setUploadContainers([{ ...initialUploadContainer, uploadDate: undefined }]);
    setErrorsList([]);
    setHasSubmitted(false);
    setElapsedSeconds(0);
  };

  const handleSubmit = async () => {
    setHasSubmitted(true);

    const errors = uploadContainers.map(container =>
      validateContainer(container, false)
    );
    const hasErrors = errors.some(err => Object.keys(err).length > 0);
    setErrorsList(errors);

    if (hasErrors) {
      toastHelper.newMessage(
        'error',
        'Validation Error',
        'Please fix the form errors before submitting.'
      );
      return;
    }

    setIsUploading(true);
    startTimeRef.current = Date.now();

    try {
      const instantTunes = await Promise.all(
        uploadContainers.map(async c => ({
          video_title: c.title,
          video_description: c.description || '',
          tags: c.tags || [],
          category: c.category,
          privacy_status: c.privacyStatus,
          embeddable: c.embeddable,
          license: c.license,
          img_name: c.image?.name,
          img_type: c.image?.name.split('.').pop(),
          img_file_base64: await fileConverter.fileToBase64(c.image),
          audio_name: c.audio?.name,
          audio_type: c.audio?.name.split('.').pop(),
          audio_file_base64: await fileConverter.fileToBase64(c.audio),
          executed: true,
        }))
      );

      const response = await createBatchInstant(instantTunes);
      const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000);

      toastHelper.newMessage(
        'success',
        response.title,
        `${response.message} (in ${elapsed}s)`
      );

      resetForm();
    } catch (error) {
      toastHelper.newMessage('error', error.title, error.message);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Box sx={{ padding: 3 }}>
      <Fade in timeout={500}>
        <Box>
          <UploadList
            uploadContainers={uploadContainers}
            onUpdate={handleUpdateContainer}
            errorsList={errorsList}
          />
        </Box>
      </Fade>

      {isUploading && (
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          <CircularProgress size={24} />
          <Typography variant="body2">
            Uploading... {elapsedSeconds}s
          </Typography>
        </Box>
      )}

      <Box mt={2}>
        <Button
          variant="contained"
          onClick={handleAddContainer}
          sx={{ marginRight: 2 }}
          disabled={isUploading}
        >
          Add More Instant Containers
        </Button>

        <Button
          variant="contained"
          color="primary"
          onClick={handleSubmit}
          disabled={isUploading}
        >
          Submit Instant Uploads
        </Button>
      </Box>
    </Box>
  );
}

export default InstantUpload;
