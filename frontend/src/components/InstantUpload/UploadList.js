import React from 'react';
import UploadForm from './UploadForm';

function UploadList({ uploadContainers, onUpdate }) {
  return (
    <>
      {uploadContainers.map((container, index) => (
        <UploadForm
          key={index}
          container={container}
          index={index}
          onUpdate={onUpdate}
        />
      ))}
    </>
  );
}

export default UploadList;
