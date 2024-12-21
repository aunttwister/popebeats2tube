import React, { useState } from 'react';
import { Button, Box } from '@mui/material';
import UploadContainer from './UploadContainer';
import axios from 'axios';
import { toast } from 'react-toastify';

function InstantUpload() {
  const [uploadContainers, setUploadContainers] = useState([{ audio: null, image: null, title: '', description: '' }]);

  const handleAddContainer = () => {
    setUploadContainers([...uploadContainers, { audio: null, image: null, title: '', description: '' }]);
  };

  const handleUpdateContainer = (index, updatedValues) => {
    const updatedContainers = [...uploadContainers];
    updatedContainers[index] = { ...updatedContainers[index], ...updatedValues };
    setUploadContainers(updatedContainers);
  };

  const handleUpload = async () => {
    // Validate files before proceeding with upload
    const invalidFiles = uploadContainers.some((container) => {
      const audioFile = container.audio && container.audio[0];
      const imageFile = container.image && container.image[0];
      return (
        !audioFile || !imageFile || 
        !audioFile.type.startsWith('audio/') || 
        !imageFile.type.startsWith('image/') || 
        audioFile.size > 10485760 || // Example size validation for audio
        imageFile.size > 5242880 // Example size validation for image
      );
    });
  
    if (invalidFiles) {
      toast.error('One or more files are invalid. Please check the file types and sizes.');
      return;
    }
  
    try {
      const formDataArray = uploadContainers.map((container) => {
        const formData = new FormData();
        formData.append('title', container.title);
        formData.append('description', container.description);
        formData.append('audio_file', container.audio[0]);
        formData.append('image_file', container.image[0]);
        return formData;
      });
  
      for (const formData of formDataArray) {
        await axios.post('/upload_tune/single', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      }
  
      toast.sucess('Upload successful!');
    } catch (error) {
      console.error('Upload failed:', error);
      toast.error('Upload failed. Please try again.');
    }
  };
  

  return (
    <Box sx={{ padding: 3 }}>
      {uploadContainers.map((container, index) => (
        <UploadContainer
          key={index}
          containerIndex={index}
          onDropAudio={(idx, files) => handleUpdateContainer(idx, { audio: files })}
          onDropImage={(idx, files) => handleUpdateContainer(idx, { image: files })}
          onChange={(idx, updatedValues) => handleUpdateContainer(idx, updatedValues)}
          audioFile={container.audio && container.audio[0]}
          imageFile={container.image && container.image[0]}
        />
      ))}

      <Button variant="contained" onClick={handleAddContainer} sx={{ marginRight: 2 }}>
        Add More Upload Containers
      </Button>
      <Button variant="contained" onClick={handleUpload} color="primary">
        Upload All
      </Button>
    </Box>
  );
}

export default InstantUpload;