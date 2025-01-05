import React, { useState } from 'react';
import { Box, Button } from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import UploadList from './UploadList';
import { createBatchSchedule } from '../../services/scheduleService.ts';
import { fileConverter } from '../../utils/fileConverter.js';
import { toastHelper } from '../../utils/toastHelper';

function ScheduledUpload() {
  const [uploadContainers, setUploadContainers] = useState([
    {
      audio: null,
      image: null,
      title: '',
      description: '',
      tags: [],
      category: '',
      privacyStatus: 'private',
      embeddable: false,
      license: 'youtube',
      uploadDate: null,
    },
  ]);

  const handleAddContainer = () => {
    setUploadContainers([
      ...uploadContainers,
      {
        audio: null,
        image: null,
        title: '',
        description: '',
        tags: [],
        category: '',
        privacyStatus: 'private',
        embeddable: false,
        license: 'youtube',
        uploadDate: null,
      },
    ]);
  };
  const handleUpdateContainer = (index, updatedValues) => {
    const updatedContainers = [...uploadContainers];
    updatedContainers[index] = { ...updatedContainers[index], ...updatedValues };
    setUploadContainers(updatedContainers);
  };

  const handleSubmit = async () => {
    try {
      const schedules = await Promise.all(
        uploadContainers.map(async (container) => {
          const imageBase64 = container.image
            ? await fileConverter.fileToBase64(container.image)
            : null;
          const audioBase64 = container.audio
            ? await fileConverter.fileToBase64(container.audio)
            : null;
  
          return {
            video_title: container.title,
            upload_date: container.uploadDate
              ? container.uploadDate.toISOString()
              : null,
            img_file: imageBase64,
            img_name: container.image?.name,
            img_type: container.image?.name.split('.').pop(),
            audio_file: audioBase64,
            audio_name: container.audio?.name,
            audio_type: container.audio?.name.split('.').pop(),
            tags: container.tags || [], // Ensure tags are passed as an array
            category: container.category || '', // Default empty string
            privacy_status: container.privacyStatus || 'private', // Default to 'private'
            embeddable: container.embeddable || false, // Default to false
            license: container.license || 'youtube', // Default to 'youtube'
            video_description: container.description || '', // Map description
            executed: false,
          };
        })
      );
  
      console.log('Schedules:', schedules);
  
      const response = await createBatchSchedule(schedules);
      toastHelper.newMessage('success', response.title, response.message);
    } catch (error) {
      console.error('Error creating schedules:', error);
      toastHelper.newMessage('error', error.title, error.message);
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Box sx={{ padding: 3 }}>
        <UploadList
          uploadContainers={uploadContainers}
          onUpdate={handleUpdateContainer}
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
