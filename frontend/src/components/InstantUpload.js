import React, { useState } from 'react';
import { Button, Box } from '@mui/material';
import UploadContainer from './UploadContainer';

function InstantUpload() {
  const [uploadContainers, setUploadContainers] = useState([{}]);

  const handleAddContainer = () => {
    setUploadContainers([...uploadContainers, {}]);
  };

  return (
    <Box sx={{ padding: 3 }}>
      {uploadContainers.map((_, index) => (
        <UploadContainer
          key={index}
          containerIndex={index}
          onDropAudio={(files) => console.log('Audio:', files)}
          onDropImage={(files) => console.log('Image:', files)}
        />
      ))}

      <Button variant="contained" onClick={handleAddContainer}>
        Add More Upload Containers
      </Button>
    </Box>
  );
}

export default InstantUpload;
