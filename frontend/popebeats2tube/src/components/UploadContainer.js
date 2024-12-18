import React from 'react';
import { Box, TextField, Typography } from '@mui/material';
import { useDropzone } from 'react-dropzone';

function UploadContainer({ onDropAudio, onDropImage, containerIndex }) {
  return (
    <Box sx={{ border: '1px solid #ccc', padding: 2, marginBottom: 2, borderRadius: 2 }}>
      <Typography variant="subtitle1">Upload Container {containerIndex + 1}</Typography>

      {/* Drag-and-drop for Audio */}
      <DropzoneField onDrop={onDropAudio} label="Drag and drop audio file here" />
      {/* Drag-and-drop for Image */}
      <DropzoneField onDrop={onDropImage} label="Drag and drop image file here" />

      {/* YouTube Title */}
      <TextField fullWidth margin="normal" label="YouTube Video Title" />

      {/* YouTube Description */}
      <TextField fullWidth margin="normal" label="YouTube Video Description" multiline rows={3} />
    </Box>
  );
}

function DropzoneField({ onDrop, label }) {
  const { getRootProps, getInputProps } = useDropzone({ onDrop });

  return (
    <Box
      {...getRootProps()}
      sx={{
        border: '2px dashed #aaa',
        padding: 2,
        textAlign: 'center',
        marginTop: 1,
        cursor: 'pointer',
      }}
    >
      <input {...getInputProps()} />
      <Typography>{label}</Typography>
    </Box>
  );
}

export default UploadContainer;
