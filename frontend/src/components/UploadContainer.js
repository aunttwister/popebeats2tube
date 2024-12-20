import React, { useState } from 'react';
import { Box, TextField, Typography } from '@mui/material';
import { useDropzone } from 'react-dropzone';

function UploadContainer({ onDropAudio, onDropImage, onChange, containerIndex }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  const handleTitleChange = (e) => {
    setTitle(e.target.value);
    onChange(containerIndex, { title: e.target.value, description });
  };

  const handleDescriptionChange = (e) => {
    setDescription(e.target.value);
    onChange(containerIndex, { title, description: e.target.value });
  };

  return (
    <Box sx={{ border: '1px solid #ccc', padding: 2, marginBottom: 2, borderRadius: 2 }}>
      <Typography variant="subtitle1">Upload Container {containerIndex + 1}</Typography>

      {/* Drag-and-drop for Audio */}
      <DropzoneField onDrop={(files) => onDropAudio(containerIndex, files)} label="Drag and drop audio file here" />
      
      {/* Drag-and-drop for Image */}
      <DropzoneField onDrop={(files) => onDropImage(containerIndex, files)} label="Drag and drop image file here" />

      {/* YouTube Title */}
      <TextField
        fullWidth
        margin="normal"
        label="YouTube Video Title"
        value={title}
        onChange={handleTitleChange}
      />

      {/* YouTube Description */}
      <TextField
        fullWidth
        margin="normal"
        label="YouTube Video Description"
        multiline
        rows={3}
        value={description}
        onChange={handleDescriptionChange}
      />
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
