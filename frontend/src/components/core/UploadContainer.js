import React, { useState } from 'react';
import { Box, TextField, Typography } from '@mui/material';
import { toastHelper } from '../../utils/toastHelper';
import { useDropzone } from 'react-dropzone';
import config from '../../config.json'; // Import the configuration file

function UploadContainer({ onDropAudio, onDropImage, onChange, containerIndex, audioFile, imageFile }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isTitleValid, setIsTitleValid] = useState(true); // State for title validation

  // States for validation
  const [isAudioValid, setIsAudioValid] = useState(true); // Audio file validity
  const [isImageValid, setIsImageValid] = useState(true); // Image file validity

  // Extract audio and image configurations from the JSON
  const audioConfig = config.fileUpload.audio;
  const imageConfig = config.fileUpload.image;

  const handleTitleChange = (e) => {
    const newTitle = e.target.value;
    setTitle(newTitle);
    setIsTitleValid(newTitle.trim() !== ''); // Check if title is not empty
    onChange(containerIndex, { title: newTitle, description });
  };

  const handleDescriptionChange = (e) => {
    setDescription(e.target.value);
    onChange(containerIndex, { title, description: e.target.value });
  };

  return (
    <Box sx={{ border: '1px solid #ccc', padding: 2, marginBottom: 2, borderRadius: 2 }}>
      <Typography variant="subtitle1">Upload Container {containerIndex + 1}</Typography>

      {/* Drag-and-drop for Audio */}
      <DropzoneField
        onDrop={(files) => onDropAudio(containerIndex, files)}
        label="Drag and drop audio file here"
        file={audioFile}
        acceptedFileTypes={audioConfig.accept}
        maxFileSize={audioConfig.maxFileSize}
        isValid={isAudioValid} // Pass isValid for audio validation
        setIsValid={setIsAudioValid} // Pass setIsValid for audio validation
      />

      {/* Drag-and-drop for Image */}
      <DropzoneField
        onDrop={(files) => onDropImage(containerIndex, files)}
        label="Drag and drop image file here"
        file={imageFile}
        acceptedFileTypes={imageConfig.accept}
        maxFileSize={imageConfig.maxFileSize}
        isValid={isImageValid} // Pass isValid for image validation
        setIsValid={setIsImageValid} // Pass setIsValid for image validation
      />

      {/* YouTube Title */}
      <TextField
        fullWidth
        margin="normal"
        label="YouTube Video Title"
        value={title}
        onChange={handleTitleChange}
        error={!isTitleValid} // Display error if title is invalid
        helperText={!isTitleValid ? 'Title is required' : ''}
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

function DropzoneField({ onDrop, label, file, acceptedFileTypes, maxFileSize, isValid, setIsValid }) {
  const { getRootProps, getInputProps } = useDropzone({
    onDrop: (acceptedFiles, fileRejections) => {
      if (fileRejections.length > 0) {
        handleValidationErrors(fileRejections, acceptedFileTypes, maxFileSize);
        setIsValid(false);
        return;
      }
      if (acceptedFiles.length > 0) {
        onDrop(acceptedFiles.slice(0, 1)); // Pass the first file
        setIsValid(true);
        toastHelper.newMessage('success', 'Success.', 'File attached successfully!');
      }
    },
    accept: acceptedFileTypes,
    maxFiles: 1,
    maxSize: maxFileSize,
  });

  // Handle validation errors for rejected files
  const handleValidationErrors = (fileRejections, acceptedFileTypes, maxFileSize) => {
    fileRejections.forEach(({ errors }) => {
      errors.forEach((error) => {
        if (error.code === 'file-invalid-type') {
          // Extract the file types from the values to display in the error
          const acceptedTypes = Object.values(acceptedFileTypes).join(', ');
          toastHelper.newMessage('error', 'Validation error.', `Invalid file format. Accepted file types: ${acceptedTypes}`);
        } else if (error.code === 'file-too-large') {
          toastHelper.newMessage('error', 'Validation error.', `File size exceeds the allowed limit of ${maxFileSize / 1048576} MB.`);
        }
      });
    });
  };

  return (
    <Box
      {...getRootProps()}
      sx={{
        border: `2px dashed ${isValid ? (file ? '#2ac759' : '#aaa') : 'red'}`,
        padding: 2,
        textAlign: 'center',
        marginTop: 1,
        cursor: 'pointer',
      }}
    >
      <input {...getInputProps()} />
      <Typography>{label}</Typography>
      {file && (
        <Typography variant="body2" sx={{ marginTop: 1 }}>
          Uploaded: {file.name}
        </Typography>
      )}
    </Box>
  );
}

export default UploadContainer;
