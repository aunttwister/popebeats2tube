import React from 'react';
import UploadForm from './UploadForm';

function UploadList({ uploadContainers, onUpdate, errorsList }) {
  return (
    <>
      {uploadContainers.map((container, index) => (
        <UploadForm
          key={index}
          container={container}
          index={index}
          onUpdate={onUpdate}
          errors={errorsList?.[index] || {}}
        />
      ))}
    </>
  );
}
export default UploadList;
