import React, { useState } from 'react';
import { Box, Button, TextField } from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import UploadContainer from './UploadContainer';
import { toast } from 'react-toastify';
import { createBatchSchedule } from '../../services/scheduleService.ts'
import { fileConverter } from '../../utils/fileConverter.js'

function ScheduledUpload() {
  const [uploadContainers, setUploadContainers] = useState([
    { audio: null, image: null, title: '', description: '', uploadDate: null },
  ]);

  const handleAddContainer = () => {
    setUploadContainers([
      ...uploadContainers,
      { audio: null, image: null, title: '', description: '', uploadDate: null },
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
          try {
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
              img: {file: imageBase64, type: container.image.name.split('.').pop() },
              audio: { file: audioBase64, type: container.audio.name.split('.').pop() },
              executed: false
            };
          } catch (error) {
            console.error('Error converting file to base64:', error.message);
            throw error;
          }
        })
      );
  
      const response = await createBatchSchedule(schedules);
      toast.success('Schedules created successfully!');
      console.log('Batch Schedule Upload Result:', response);
    } catch (error) {
      console.error('Error creating schedules:', error);
      toast.error('Failed to create schedules. Please try again.');
    }
  };
  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Box sx={{ padding: 3 }}>
        {uploadContainers.map((container, index) => (
          <Box key={index} sx={{ marginBottom: 2 }}>
            <UploadContainer
              containerIndex={index}
              onDropAudio={(idx, files) =>
                handleUpdateContainer(idx, { audio: files[0] })
              }
              onDropImage={(idx, files) =>
                handleUpdateContainer(idx, { image: files[0] })
              }
              onChange={(idx, updatedValues) =>
                handleUpdateContainer(idx, updatedValues)
              }
              audioFile={container.audio}
              imageFile={container.image}
            />
            <DatePicker
              label="Upload Date"
              value={container.uploadDate}
              onChange={(date) =>
                handleUpdateContainer(index, { uploadDate: date })
              }
              renderInput={(params) => (
                <TextField {...params} fullWidth margin="normal" />
              )}
            />
          </Box>
        ))}

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
