import React from 'react';
import { Box, TextField } from '@mui/material';
import { MobileDateTimePicker } from '@mui/x-date-pickers/MobileDateTimePicker';
import UploadContainer from '../UploadContainer/UploadContainer';

function UploadForm({ container, index, onUpdate }) {
  return (
    <Box key={index} sx={{ marginBottom: 2 }}>
      <UploadContainer
        containerIndex={index}
        onDropAudio={(idx, files) => onUpdate(idx, { audio: files[0] })}
        onDropImage={(idx, files) => onUpdate(idx, { image: files[0] })}
        onChange={(idx, updatedValues) => onUpdate(idx, updatedValues)}
        audioFile={container.audio}
        imageFile={container.image}
      />
      <MobileDateTimePicker
        label="Upload Date and Time"
        value={container.uploadDate}
        onChange={(date) => onUpdate(index, { uploadDate: date })}
        renderInput={(params) => (
          <TextField {...params} fullWidth margin="normal" />
        )}
      />
    </Box>
  );
}

export default UploadForm;
