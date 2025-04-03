import React from 'react';
import { Box } from '@mui/material';
import { MobileDateTimePicker } from '@mui/x-date-pickers/MobileDateTimePicker';
import UploadContainer from '../UploadContainer/UploadContainer';

function UploadForm({ container, index, onUpdate, errors }) {
  return (
    <Box key={index} sx={{ marginBottom: 2 }}>
      <UploadContainer
        containerIndex={index}
        onDropAudio={(idx, files) => onUpdate(idx, { audio: files[0] })}
        onDropImage={(idx, files) => onUpdate(idx, { image: files[0] })}
        onChange={(idx, updatedValues) => onUpdate(idx, updatedValues)}
        audioFile={container.audio}
        imageFile={container.image}
        errors={errors}
      />

      {container.uploadDate !== undefined && (
        <MobileDateTimePicker
          label="Upload Date and Time"
          value={container.uploadDate}
          onChange={(date) => onUpdate(index, { uploadDate: date })}
          slotProps={{
            textField: {
              fullWidth: true,
              margin: 'normal',
              error: Boolean(errors?.uploadDate),
              helperText: errors?.uploadDate,
              sx: {
                '& .MuiOutlinedInput-root .MuiOutlinedInput-notchedOutline': {
                  borderColor: errors?.uploadDate ? 'red' : 'rgba(0, 0, 0, 0.23)',
                  borderWidth: '1px',
                  borderStyle: 'solid',
                },
                '& label.Mui-error': {
                  color: 'red',
                },
              },
            },
          }}
        />
      )}
    </Box>
  );
}

export default UploadForm;
