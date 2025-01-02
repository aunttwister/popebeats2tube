import React, { useState } from 'react';
import { Box, Button, TextField } from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import UploadContainer from './UploadContainer';

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

  const handleSubmit = () => {
    console.log('Scheduled Upload Data:', uploadContainers);
    // API call logic can go here
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
