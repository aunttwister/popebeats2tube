import React from 'react';
import { Box, Typography } from '@mui/material';
import { useDropzone } from 'react-dropzone';
import './UploadContainer.css';
import { toastHelper } from '../../utils/toastHelper';

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

  const handleValidationErrors = (fileRejections, acceptedFileTypes, maxFileSize) => {
    fileRejections.forEach(({ errors }) => {
      errors.forEach((error) => {
        if (error.code === 'file-invalid-type') {
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
      <Box>{label}</Box>
      {file && (
        <Typography variant="body2" sx={{ marginTop: 1 }}>
          Uploaded: {file.name}
        </Typography>
      )}
    </Box>
  );
}

export default DropzoneField;
