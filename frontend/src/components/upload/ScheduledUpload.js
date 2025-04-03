import React, { useState } from 'react';
import { Box, Button } from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import UploadList from '../ScheduledUpload/UploadList';
import { createBatchSchedule } from '../../services/scheduleTuneService.ts';
import { fileConverter } from '../../utils/fileConverter';
import { toastHelper } from '../../utils/toastHelper';
import { initialUploadContainer } from '../../constants/uploadConstants';
import { validateContainer } from '../../utils/uploadValidator';

function ScheduledUpload() {
  const [uploadContainers, setUploadContainers] = useState([
    { ...initialUploadContainer }
  ]);
  const [errorsList, setErrorsList] = useState([]);
  const [hasSubmitted, setHasSubmitted] = useState(false);

  const handleAddContainer = () => {
    setUploadContainers(prev => [...prev, { ...initialUploadContainer }]);
  };

  const handleUpdateContainer = (index, updatedValues) => {
    const updated = [...uploadContainers];
    updated[index] = { ...updated[index], ...updatedValues };
    setUploadContainers(updated);

    if (hasSubmitted) {
      const updatedErrors = [...errorsList];
      updatedErrors[index] = validateContainer(updated[index], true);
      setErrorsList(updatedErrors);
    }
  };

  const handleSubmit = async () => {
    setHasSubmitted(true);

    const errors = uploadContainers.map(container =>
      validateContainer(container, true)
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

    try {
      const schedules = await Promise.all(
        uploadContainers.map(async c => ({
          video_title: c.title,
          video_description: c.description || '',
          tags: c.tags || [],
          category: c.category,
          privacy_status: c.privacyStatus,
          embeddable: c.embeddable,
          license: c.license,
          upload_date: c.uploadDate?.toISOString(),
          img_name: c.image?.name,
          img_type: c.image?.name.split('.').pop(),
          img_file_base64: await fileConverter.fileToBase64(c.image),
          audio_name: c.audio?.name,
          audio_type: c.audio?.name.split('.').pop(),
          audio_file_base64: await fileConverter.fileToBase64(c.audio),
          executed: false,
        }))
      );

      const response = await createBatchSchedule(schedules);
      toastHelper.newMessage('success', response.title, response.message);
    } catch (error) {
      toastHelper.newMessage('error', error.title, error.message);
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Box sx={{ padding: 3 }}>
        <UploadList
          uploadContainers={uploadContainers}
          onUpdate={handleUpdateContainer}
          errorsList={errorsList}
        />
        <Button
          variant="contained"
          onClick={handleAddContainer}
          sx={{ marginRight: 2 }}
        >
          Add More Scheduled Containers
        </Button>
        <Button variant="contained" color="primary" onClick={handleSubmit}>
          Submit Scheduled Uploads
        </Button>
      </Box>
    </LocalizationProvider>
  );
}

export default ScheduledUpload;
