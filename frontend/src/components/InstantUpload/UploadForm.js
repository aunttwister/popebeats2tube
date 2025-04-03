import React from 'react';
import { Box } from '@mui/material';
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
    </Box>
  );
}

export default UploadForm;
