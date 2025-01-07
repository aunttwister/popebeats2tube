// InstantUpload.js
import React, { useState } from 'react';
import { Box, Button } from '@mui/material';
import UploadList from './UploadList.js';
import { createBatchInstant } from '../../services/instantTuneService.ts';
import { fileConverter } from '../../utils/fileConverter.js';
import { toastHelper } from '../../utils/toastHelper.js';

function InstantUpload() {
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
      const instantTunes = await Promise.all(
        uploadContainers.map(async (container) => {
          const imageBase64 = container.image
            ? await fileConverter.fileToBase64(container.image)
            : null;
          const audioBase64 = container.audio
            ? await fileConverter.fileToBase64(container.audio)
            : null;

          return {
            video_title: container.title,
            img_file_base64: imageBase64,
            img_name: container.image?.name,
            img_type: container.image?.name.split('.').pop(),
            audio_file_base64: audioBase64,
            audio_name: container.audio?.name,
            audio_type: container.audio?.name.split('.').pop(),
            tags: container.tags || [], // Ensure tags are passed as an array
            category: container.category || '', // Default empty string
            privacy_status: container.privacyStatus || 'private', // Default to 'private'
            embeddable: container.embeddable || false, // Default to false
            license: container.license || 'youtube', // Default to 'youtube'
            video_description: container.description || '', // Map description
            executed: true,
          };
        })
      );

      console.log('Instants tunes:', instantTunes);

      const response = await createBatchInstant(instantTunes);
      toastHelper.newMessage('success', response.title, response.message);
    } catch (error) {
      console.error('Error creating instants:', error);
      toastHelper.newMessage('error', error.title, error.message);
    }
  };

  return (
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
        Add More Instant Containers
      </Button>
      <Button variant="contained" color="primary" onClick={handleSubmit}>
        Submit Instant Uploads
      </Button>
    </Box>
  );
}

export default InstantUpload;