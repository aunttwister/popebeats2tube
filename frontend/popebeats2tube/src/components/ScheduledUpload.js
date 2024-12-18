import React, { useState } from 'react';
import { Box, Button, TextField } from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import UploadContainer from './UploadContainer';

function ScheduledUpload() {
  const [uploadContainers, setUploadContainers] = useState([{}]);

  const handleAddContainer = () => {
    setUploadContainers([...uploadContainers, {}]);
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Box sx={{ padding: 3 }}>
        {uploadContainers.map((_, index) => (
          <Box key={index} sx={{ marginBottom: 2 }}>
            <UploadContainer containerIndex={index} />
            <DatePicker
              label="Upload Date"
              onChange={(date) => console.log('Upload Date:', date)}
              renderInput={(params) => (
                <TextField {...params} fullWidth margin="normal" />
              )}
            />
          </Box>
        ))}

        <Button variant="contained" onClick={handleAddContainer}>
          Add More Scheduled Containers
        </Button>
      </Box>
    </LocalizationProvider>
  );
}

export default ScheduledUpload;
